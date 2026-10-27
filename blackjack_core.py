"""
Blackjack logic — shared by CLI and web.

Follows Al Sweigart's rules: 21, face cards 10, aces 1/11, dealer stands on 17,
optional double down on first two cards (no split/insurance).
"""

from __future__ import annotations

import random
from copy import deepcopy
from typing import Any, Literal

HEARTS = "\u2665"
DIAMONDS = "\u2666"
SPADES = "\u2660"
CLUBS = "\u2663"
SUITS: tuple[str, ...] = (HEARTS, DIAMONDS, SPADES, CLUBS)

STARTING_MONEY = 5000
BACKSIDE = "backside"

Phase = Literal["betting", "playing", "finished", "broke"]
Outcome = Literal["win", "lose", "tie", "bust"] | None


def card(rank: str, suit: str) -> dict[str, str]:
    return {"rank": rank, "suit": suit}


def hidden_card() -> dict[str, str]:
    return {"rank": BACKSIDE, "suit": BACKSIDE}


def get_deck(rng: random.Random | None = None) -> list[dict[str, str]]:
    deck: list[dict[str, str]] = []
    for suit in SUITS:
        for rank_num in range(2, 11):
            deck.append(card(str(rank_num), suit))
        for face in ("J", "Q", "K", "A"):
            deck.append(card(face, suit))
    (rng or random).shuffle(deck)
    return deck


def get_hand_value(cards: list[dict[str, str]]) -> int:
    value = 0
    aces = 0
    for c in cards:
        if c.get("rank") == BACKSIDE:
            continue
        rank = c["rank"]
        if rank == "A":
            aces += 1
        elif rank in ("K", "Q", "J"):
            value += 10
        else:
            value += int(rank)
    value += aces
    for _ in range(aces):
        if value + 10 <= 21:
            value += 10
    return value


def initial_state() -> dict[str, Any]:
    return {
        "money": STARTING_MONEY,
        "bet": 0,
        "phase": "betting",
        "deck": [],
        "player_hand": [],
        "dealer_hand": [],
        "doubled": False,
        "outcome": None,
        "message": "",
    }


def reset_bankroll(state: dict[str, Any]) -> dict[str, Any]:
    fresh = initial_state()
    return {**fresh, "money": STARTING_MONEY}


def can_double_down(state: dict[str, Any]) -> bool:
    return (
        state["phase"] == "playing"
        and len(state["player_hand"]) == 2
        and not state["doubled"]
        and state["money"] > state["bet"]
    )


def max_additional_double_bet(state: dict[str, Any]) -> int:
    return min(state["bet"], state["money"] - state["bet"])


def start_round(state: dict[str, Any], bet: int) -> dict[str, Any]:
    if state["phase"] not in ("betting", "finished", "broke"):
        raise ValueError("Finish the current hand before betting again.")
    if bet < 1 or bet > state["money"]:
        raise ValueError(f"Bet must be between 1 and {state['money']}.")

    deck = get_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    return {
        **state,
        "bet": bet,
        "phase": "playing",
        "deck": deck,
        "player_hand": player_hand,
        "dealer_hand": dealer_hand,
        "doubled": False,
        "outcome": None,
        "message": "",
    }


def _dealer_play(state: dict[str, Any]) -> dict[str, Any]:
    next_state = deepcopy(state)
    while get_hand_value(next_state["dealer_hand"]) < 17:
        next_state["dealer_hand"].append(next_state["deck"].pop())
        if get_hand_value(next_state["dealer_hand"]) > 21:
            break
    return _resolve_round(next_state)


def _resolve_round(state: dict[str, Any]) -> dict[str, Any]:
    player_value = get_hand_value(state["player_hand"])
    dealer_value = get_hand_value(state["dealer_hand"])
    bet = state["bet"]
    money = state["money"]
    outcome: Outcome
    message: str

    if player_value > 21:
        outcome = "bust"
        message = "You busted! You lost."
        money -= bet
    elif dealer_value > 21:
        outcome = "win"
        message = f"Dealer busts! You win ${bet}!"
        money += bet
    elif player_value < dealer_value:
        outcome = "lose"
        message = "You lost!"
        money -= bet
    elif player_value > dealer_value:
        outcome = "win"
        message = f"You won ${bet}!"
        money += bet
    else:
        outcome = "tie"
        message = "It's a tie; your bet is returned."

    phase: Phase = "broke" if money <= 0 else "finished"
    return {
        **state,
        "money": money,
        "phase": phase,
        "outcome": outcome,
        "message": message,
    }


def player_hit(state: dict[str, Any]) -> dict[str, Any]:
    if state["phase"] != "playing":
        raise ValueError("You are not in an active hand.")
    next_state = deepcopy(state)
    next_state["player_hand"].append(next_state["deck"].pop())
    if get_hand_value(next_state["player_hand"]) > 21:
        return _resolve_round(next_state)
    return next_state


def player_stand(state: dict[str, Any]) -> dict[str, Any]:
    if state["phase"] != "playing":
        raise ValueError("You are not in an active hand.")
    if get_hand_value(state["player_hand"]) > 21:
        return _resolve_round(deepcopy(state))
    return _dealer_play(state)


def player_double_down(state: dict[str, Any], additional_bet: int) -> dict[str, Any]:
    if not can_double_down(state):
        raise ValueError("Double down is not available.")
    max_extra = max_additional_double_bet(state)
    if additional_bet < 1 or additional_bet > max_extra:
        raise ValueError(f"Additional bet must be between 1 and {max_extra}.")

    next_state = deepcopy(state)
    next_state["bet"] += additional_bet
    next_state["doubled"] = True
    next_state["player_hand"].append(next_state["deck"].pop())
    if get_hand_value(next_state["player_hand"]) > 21:
        return _resolve_round(next_state)
    return _dealer_play(next_state)


def next_hand(state: dict[str, Any]) -> dict[str, Any]:
    if state["phase"] not in ("finished", "broke"):
        raise ValueError("No round to clear.")
    if state["money"] <= 0:
        return {**state, "phase": "broke"}
    return {
        **state,
        "phase": "betting",
        "bet": 0,
        "deck": [],
        "player_hand": [],
        "dealer_hand": [],
        "doubled": False,
        "outcome": None,
        "message": "",
    }


def _hand_for_client(hand: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{"rank": c["rank"], "suit": c["suit"]} for c in hand]


def state_for_client(state: dict[str, Any]) -> dict[str, Any]:
    hide_dealer = state["phase"] == "playing"
    dealer_hand = state["dealer_hand"]
    if hide_dealer and len(dealer_hand) >= 2:
        dealer_view = [hidden_card(), *_hand_for_client(dealer_hand[1:])]
        dealer_total: int | None = None
    else:
        dealer_view = _hand_for_client(dealer_hand)
        dealer_total = get_hand_value(dealer_hand) if dealer_hand else None

    player_hand = _hand_for_client(state["player_hand"])
    player_total = get_hand_value(state["player_hand"]) if player_hand else None

    return {
        "money": state["money"],
        "bet": state["bet"],
        "phase": state["phase"],
        "player_hand": player_hand,
        "dealer_hand": dealer_view,
        "player_total": player_total,
        "dealer_total": dealer_total,
        "doubled": state.get("doubled", False),
        "can_double": can_double_down(state),
        "max_double_extra": max_additional_double_bet(state) if can_double_down(state) else 0,
        "outcome": state.get("outcome"),
        "message": state.get("message") or "",
    }


def state_from_client(payload: dict[str, Any]) -> dict[str, Any]:
    """Rebuild internal state from prior server response + carried deck."""
    return {
        "money": payload["money"],
        "bet": payload["bet"],
        "phase": payload["phase"],
        "deck": payload.get("deck") or [],
        "player_hand": payload.get("player_hand") or [],
        "dealer_hand": payload.get("dealer_hand") or [],
        "doubled": payload.get("doubled", False),
        "outcome": payload.get("outcome"),
        "message": payload.get("message", ""),
    }


def state_for_client_with_deck(state: dict[str, Any]) -> dict[str, Any]:
    """Include hidden deck for round-trip (demo trust model)."""
    public = state_for_client(state)
    public["_deck"] = state.get("deck", [])
    public["_dealer_hand_full"] = _hand_for_client(state.get("dealer_hand", []))
    public["_player_hand_full"] = _hand_for_client(state.get("player_hand", []))
    return public


def internal_from_roundtrip(body: dict[str, Any]) -> dict[str, Any]:
    return {
        "money": body["money"],
        "bet": body["bet"],
        "phase": body["phase"],
        "deck": body.get("_deck") or [],
        "player_hand": body.get("_player_hand_full") or body.get("player_hand") or [],
        "dealer_hand": body.get("_dealer_hand_full") or body.get("dealer_hand") or [],
        "doubled": body.get("doubled", False),
        "outcome": body.get("outcome"),
        "message": body.get("message", ""),
    }
