"""Terminal blackjack — uses shared blackjack_core logic."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from blackjack_core import (  # noqa: E402
    get_hand_value,
    initial_state,
    max_additional_double_bet,
    next_hand,
    player_double_down,
    player_hit,
    player_stand,
    start_round,
    state_for_client,
)

print(
    """Blackjack

Try to get close to 21 without going over. Dealer stands on 17.
(H)it, (S)tand, or (D)ouble down on your first two cards.
"""
)


def display(state: dict) -> None:
    view = state_for_client(state)
    print()
    if view["dealer_total"] is None:
        print("DEALER: ???")
    else:
        print("DEALER:", view["dealer_total"])
    for c in view["dealer_hand"]:
        print(f"  {c['rank']} {c['suit']}")
    print("PLAYER:", view["player_total"])
    for c in view["player_hand"]:
        print(f"  {c['rank']} {c['suit']}")
    if view["message"]:
        print(view["message"])


state = initial_state()

while True:
    if state["phase"] == "broke":
        print("You're broke! Resetting bankroll for practice.")
        state = initial_state()

    if state["phase"] in ("betting", "finished"):
        if state["phase"] == "finished":
            display(state)
            input("Press Enter for the next hand...")
            state = next_hand(state)
        print(f"Money: ${state['money']}")
        raw = input(f"How much do you bet? (1-{state['money']}, or QUIT)\n> ").strip()
        if raw.upper() == "QUIT":
            print("Thanks for playing!")
            break
        if not raw.isdecimal():
            continue
        bet = int(raw)
        try:
            state = start_round(state, bet)
        except ValueError as exc:
            print(exc)
            continue

    while state["phase"] == "playing":
        display(state)
        if get_hand_value(state["player_hand"]) > 21:
            state = player_stand(state)
            break
        moves = "(H)it, (S)tand"
        if len(state["player_hand"]) == 2 and state["money"] > state["bet"]:
            moves += ", (D)ouble"
        move = input(moves + "\n> ").upper().strip()
        try:
            if move == "H":
                state = player_hit(state)
            elif move == "S":
                state = player_stand(state)
            elif move == "D":
                max_extra = max_additional_double_bet(state)
                extra_raw = input(f"Additional bet (1-{max_extra}): ").strip()
                if not extra_raw.isdecimal():
                    continue
                state = player_double_down(state, int(extra_raw))
            else:
                continue
        except ValueError as exc:
            print(exc)

print("Thanks for playing!")
