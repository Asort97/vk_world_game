const state = {
  sessionId: "",
  route: [],
  screen: "welcome",
  lastResult: null,
  locked: false,
};

const elements = {
  welcomeScreen: document.querySelector("#welcome-screen"),
  gameScreen: document.querySelector("#game-screen"),
  resultScreen: document.querySelector("#result-screen"),
  startButton: document.querySelector("#start-button"),
  levelTitle: document.querySelector("#level-title"),
  correctCount: document.querySelector("#correct-count"),
  wrongCount: document.querySelector("#wrong-count"),
  movesCount: document.querySelector("#moves-count"),
  daysCount: document.querySelector("#days-count"),
  progressCurrent: document.querySelector("#progress-current"),
  questionNumber: document.querySelector("#question-number"),
  nextCountry: document.querySelector("#next-country"),
  questionCountry: document.querySelector("#question-country"),
  questionText: document.querySelector("#question-text"),
  answers: document.querySelector("#answers"),
  routePoints: document.querySelector("#route-points"),
  balloon: document.querySelector("#balloon"),
  resultKicker: document.querySelector("#result-kicker"),
  resultTitle: document.querySelector("#result-title"),
  resultMessage: document.querySelector("#result-message"),
  finalStats: document.querySelector("#final-stats"),
  promoCard: document.querySelector("#promo-card"),
  rankCard: document.querySelector("#rank-card"),
  resultButton: document.querySelector("#result-button"),
};

function initVkBridge() {
  if (window.vkBridge && !window.__vkInitSent) {
    window.__vkInitSent = true;
    window.vkBridge.send("VKWebAppInit").catch(() => {});
  }
}

function vkUserId() {
  const params = new URLSearchParams(window.location.search);
  const value = params.get("vk_user_id") || params.get("viewer_id") || "";
  return value ? Number(value) : null;
}

async function api(path, body) {
  const response = await fetch(path, {
    method: body ? "POST" : "GET",
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Ошибка сервера");
  }
  return data;
}

function showScreen(name) {
  state.screen = name;
  elements.welcomeScreen.classList.toggle("hidden", name !== "welcome");
  elements.gameScreen.classList.toggle("hidden", name !== "game");
  elements.resultScreen.classList.toggle("hidden", name !== "result");
}

function drawMap(route) {
  state.route = route;
  elements.routePoints.innerHTML = "";
  route.forEach((point, index) => {
    const marker = document.createElement("span");
    marker.className = "route-point";
    marker.style.left = `${point.x}%`;
    marker.style.top = `${point.y}%`;
    marker.dataset.index = String(index);
    elements.routePoints.appendChild(marker);
  });
}

function updateMap(position) {
  document.querySelectorAll(".route-point").forEach((marker) => {
    const index = Number(marker.dataset.index);
    marker.classList.toggle("done", index < position);
    marker.classList.toggle("current", index === position);
  });
  const point = state.route[position] || state.route[0];
  if (!point) return;
  elements.balloon.style.left = `${point.x}%`;
  elements.balloon.style.top = `${point.y}%`;
}

function renderStats(stats, progress, total) {
  elements.correctCount.textContent = stats.correct;
  elements.wrongCount.textContent = stats.wrong;
  elements.movesCount.textContent = stats.moves;
  elements.daysCount.textContent = stats.days;
  elements.progressCurrent.textContent = progress;
  elements.questionNumber.textContent = Math.min(progress + 1, total);
}

function renderQuestion(view) {
  const question = view.question;
  elements.levelTitle.textContent = view.level.title;
  elements.nextCountry.textContent = view.next_country;
  elements.questionCountry.textContent = question.country;
  elements.questionText.textContent = question.text;
  elements.answers.innerHTML = "";
  question.options.forEach((text, index) => {
    const button = document.createElement("button");
    button.className = "answer-button";
    button.type = "button";
    button.dataset.index = String(index);
    button.innerHTML = `<span class="answer-letter">${String.fromCharCode(65 + index)}</span><span>${text}</span>`;
    button.addEventListener("click", () => sendAnswer(index));
    elements.answers.appendChild(button);
  });
}

function renderGame(view) {
  if (!state.route.length) drawMap(view.route);
  renderStats(view.stats, view.progress, view.total);
  renderQuestion(view);
  updateMap(view.position);
  showScreen("game");
}

function statCard(label, value) {
  const item = document.createElement("span");
  item.innerHTML = `${label}<b>${value}</b>`;
  return item;
}

function renderResult(view) {
  const result = view.result;
  state.lastResult = result;
  elements.resultTitle.textContent = result.title;
  elements.resultMessage.textContent = result.message;
  elements.resultKicker.textContent = view.status === "completed" ? "Маршрут завершен" : "Маршрут уровня завершен";
  elements.finalStats.innerHTML = "";
  Object.entries(result.stats).forEach(([label, value]) => {
    elements.finalStats.appendChild(statCard(label, value));
  });

  elements.promoCard.classList.toggle("hidden", !result.promo);
  elements.promoCard.innerHTML = result.promo ? `Промокод <b>${result.promo}</b>` : "";

  elements.rankCard.classList.toggle("hidden", !result.rank);
  elements.rankCard.innerHTML = result.rank ? `Место среди участников <b>${result.rank}</b>` : "";

  if (result.next_level) {
    elements.resultButton.textContent = `Перейти на ${result.next_level.label.toLowerCase()} уровень`;
  } else {
    elements.resultButton.textContent = view.status === "completed" ? "Играть еще раз" : "Попробовать еще раз";
  }
  showScreen("result");
}

function renderState(view) {
  state.sessionId = view.session_id;
  if (view.route && !state.route.length) drawMap(view.route);
  if (view.status === "playing") {
    renderGame(view);
  } else {
    updateMap(view.position);
    renderResult(view);
  }
}

function markFeedback(feedback) {
  document.querySelectorAll(".answer-button").forEach((button) => {
    const index = Number(button.dataset.index);
    button.disabled = true;
    button.classList.toggle("wrong", index === feedback.selected_index && !feedback.is_correct);
    button.classList.toggle("correct", index === feedback.correct_index);
  });
}

async function startGame() {
  elements.startButton.disabled = true;
  elements.startButton.textContent = "Загрузка...";
  try {
    const view = await api("/api/session", { vk_user_id: vkUserId() });
    renderState(view);
  } catch (error) {
    elements.startButton.textContent = "Не удалось загрузить игру";
    console.error(error);
  } finally {
    elements.startButton.disabled = false;
  }
}

async function sendAnswer(optionIndex) {
  if (state.locked) return;
  state.locked = true;
  try {
    const response = await api(`/api/session/${state.sessionId}/answer`, { option_index: optionIndex });
    markFeedback(response.feedback);
    window.setTimeout(() => {
      renderState(response.state);
      state.locked = false;
    }, 650);
  } catch (error) {
    state.locked = false;
    console.error(error);
  }
}

async function handleResultButton() {
  if (state.lastResult && state.lastResult.next_level) {
    const view = await api(`/api/session/${state.sessionId}/continue`, {});
    renderState(view);
    return;
  }
  state.route = [];
  showScreen("welcome");
}

async function loadGame() {
  initVkBridge();
  const bootstrap = await api("/api/bootstrap");
  drawMap(bootstrap.route);
  updateMap(0);
}

elements.startButton.addEventListener("click", startGame);
elements.resultButton.addEventListener("click", handleResultButton);

loadGame().catch((error) => {
  elements.startButton.disabled = true;
  elements.startButton.textContent = "Не удалось загрузить игру";
  console.error(error);
});
