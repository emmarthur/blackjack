# Book directions — Blackjack

**Catalog #439** · Al Sweigart, *The Big Book of Small Python Projects*, **Project #4** — Blackjack

- Invent with Python: [project4.html](https://inventwithpython.com/bigbookpython/project4.html)
- Upstream: [blackjack.py](https://github.com/asweigart/the-big-book-of-small-python-projects/blob/main/blackjack.py)
- Local reference: [`reference/blackjack.py`](./reference/blackjack.py)
- Shared logic: [`blackjack_core.py`](./blackjack_core.py)

## What the book asks you to build

A casino-style **21** loop with $5,000 play money:

1. Player bets each round; dealer and player get two cards.
2. Card values: 2–10 face value, J/Q/K = 10, ace = 1 or 11 (best total ≤ 21).
3. **Hit** / **stand**; **double down** on first two cards (extra bet, one hit, then stand).
4. Dealer hits until total ≥ 17. No split or insurance.
5. Win, lose, tie (bet returned), or bust.

## Web version (`web/` — FastAPI, port **3027**)

| Book step | Web equivalent |
|-----------|----------------|
| Bet | `POST /api/bet` |
| Hit / stand / double | `POST /api/action` |
| Round result | `blackjack_core._resolve_round` |
| Next hand / broke | `POST /api/next-hand`, reset bankroll |

CLI: [`reference/run_cli.py`](./reference/run_cli.py)
