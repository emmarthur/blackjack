const moneyEl = document.getElementById("money");
const betEl = document.getElementById("bet");
const betLine = document.getElementById("bet-line");
const statusText = document.getElementById("status-text");
const errorEl = document.getElementById("error-text");
const tableSection = document.getElementById("table-section");
const dealerCards = document.getElementById("dealer-cards");
const playerCards = document.getElementById("player-cards");
const dealerTotalEl = document.getElementById("dealer-total");
const playerTotalEl = document.getElementById("player-total");
const betPanel = document.getElementById("bet-panel");
const playPanel = document.getElementById("play-panel");
const afterPanel = document.getElementById("after-panel");
const betInput = document.getElementById("bet-input");
const doublePanel = document.getElementById("double-panel");
const doubleInput = document.getElementById("double-input");

const SESSION_KEY = "blackjack-v1";

let state = null;

function persistState() {
  if (state) AppSession.save(SESSION_KEY, state);
}

function restoreState() {
  const saved = AppSession.load(SESSION_KEY);
  if (!saved?.money) return false;
  state = saved;
  render();
  return true;
}

AppSession.wireHelpSave(SESSION_KEY, () => state);

function setError(message) {
  errorEl.hidden = !message;
  errorEl.textContent = message || "";
}

function formatMoney(n) {
  return `$${n}`;
}

function isHiddenCard(card) {
  return card.rank === "backside";
}

function renderCard(card) {
  const el = document.createElement("div");
  el.className = "playing-card";
  if (isHiddenCard(card)) {
    el.classList.add("is-back");
    el.setAttribute("aria-label", "Hidden card");
    return el;
  }
  const red = card.suit === "\u2665" || card.suit === "\u2666";
  el.classList.toggle("is-red", red);
  el.innerHTML = `<span class="rank">${card.rank}</span><span class="suit">${card.suit}</span>`;
  el.setAttribute("aria-label", `${card.rank} of ${card.suit}`);
  return el;
}

function renderHand(container, hand) {
  container.innerHTML = "";
  hand.forEach((c) => container.appendChild(renderCard(c)));
}

function render() {
  if (!state) return;

  moneyEl.textContent = formatMoney(state.money);
  betLine.hidden = state.bet <= 0;
  betEl.textContent = formatMoney(state.bet);

  const showTable = state.player_hand?.length > 0;
  tableSection.hidden = !showTable;
  if (showTable) {
    renderHand(dealerCards, state.dealer_hand);
    renderHand(playerCards, state.player_hand);
    dealerTotalEl.textContent =
      state.dealer_total != null ? `(${state.dealer_total})` : "(?)";
    playerTotalEl.textContent =
      state.player_total != null ? `(${state.player_total})` : "";
  }

  statusText.textContent = state.message || "";
  statusText.className = "status-text";
  if (state.outcome === "win") statusText.classList.add("is-win");
  if (state.outcome === "lose" || state.outcome === "bust") {
    statusText.classList.add("is-lose");
  }

  betPanel.hidden = state.phase !== "betting" && state.phase !== "finished";
  playPanel.hidden = state.phase !== "playing";
  afterPanel.hidden = state.phase !== "finished" && state.phase !== "broke";

  const btnDouble = document.getElementById("btn-double");
  btnDouble.hidden = !state.can_double;
  doublePanel.hidden = true;

  if (state.phase === "betting" || state.phase === "finished") {
    betInput.max = state.money;
    if (Number(betInput.value) > state.money) betInput.value = Math.max(1, state.money);
  }

  if (state.can_double) {
    doubleInput.max = state.max_double_extra;
    doubleInput.value = state.max_double_extra;
  }
}

async function postJson(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Request failed.");
  return data;
}

async function deal() {
  setError(null);
  const bet = Number(betInput.value);
  if (!bet || bet < 1) {
    setError("Enter a valid bet.");
    return;
  }
  try {
    state = await postJson("/api/bet", { state, bet });
    render();
    persistState();
  } catch (err) {
    setError(err.message);
  }
}

async function action(kind, additionalBet = 0) {
  setError(null);
  try {
    state = await postJson("/api/action", {
      state,
      action: kind,
      additional_bet: additionalBet,
    });
    render();
    persistState();
  } catch (err) {
    setError(err.message);
  }
}

async function nextHand() {
  setError(null);
  try {
    state = await postJson("/api/next-hand", { state });
    render();
    persistState();
  } catch (err) {
    setError(err.message);
  }
}

async function resetBankroll() {
  setError(null);
  try {
    state = await postJson("/api/reset-bankroll", {});
    AppSession.clear(SESSION_KEY);
    render();
    persistState();
  } catch (err) {
    setError(err.message);
  }
}

document.getElementById("btn-deal").addEventListener("click", () => deal());
document.getElementById("btn-hit").addEventListener("click", () => action("hit"));
document.getElementById("btn-stand").addEventListener("click", () => action("stand"));
document.getElementById("btn-double").addEventListener("click", () => {
  doublePanel.hidden = false;
});
document.getElementById("btn-confirm-double").addEventListener("click", () => {
  action("double", Number(doubleInput.value));
});
document.getElementById("btn-next").addEventListener("click", () => nextHand());
document.getElementById("btn-reset-bankroll").addEventListener("click", () => resetBankroll());

async function init() {
  if (restoreState()) return;
  await resetBankroll();
}

init();
