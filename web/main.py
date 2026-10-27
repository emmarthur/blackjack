"""
FastAPI app — Blackjack (21).

Run: uvicorn main:app --reload --port 3027
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

_DEMO_ROOT = Path(__file__).resolve().parent.parent
if str(_DEMO_ROOT) not in sys.path:
    sys.path.insert(0, str(_DEMO_ROOT))

from blackjack_core import (  # noqa: E402
    initial_state,
    internal_from_roundtrip,
    next_hand,
    player_double_down,
    player_hit,
    player_stand,
    reset_bankroll,
    start_round,
    state_for_client_with_deck,
)

app = FastAPI(title="Blackjack")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


class BetRequest(BaseModel):
    state: dict[str, Any]
    bet: int = Field(..., ge=1)


class ActionRequest(BaseModel):
    state: dict[str, Any]
    action: Literal["hit", "stand", "double"]
    additional_bet: int = Field(0, ge=0)


class StateRequest(BaseModel):
    state: dict[str, Any]


def _respond(state: dict[str, Any]) -> JSONResponse:
    return JSONResponse(state_for_client_with_deck(state))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "help.html")


@app.post("/api/reset-bankroll")
async def api_reset_bankroll() -> JSONResponse:
    return _respond(reset_bankroll(initial_state()))


@app.post("/api/bet")
async def api_bet(body: BetRequest) -> JSONResponse:
    try:
        state = internal_from_roundtrip(body.state)
        new_state = start_round(state, body.bet)
        return _respond(new_state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/action")
async def api_action(body: ActionRequest) -> JSONResponse:
    try:
        state = internal_from_roundtrip(body.state)
        if body.action == "hit":
            new_state = player_hit(state)
        elif body.action == "stand":
            new_state = player_stand(state)
        else:
            if body.additional_bet < 1:
                raise ValueError("Enter an additional bet for double down.")
            new_state = player_double_down(state, body.additional_bet)
        return _respond(new_state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/next-hand")
async def api_next_hand(body: StateRequest) -> JSONResponse:
    try:
        state = internal_from_roundtrip(body.state)
        return _respond(next_hand(state))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
