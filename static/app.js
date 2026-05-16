const POINTS = [
  { name: "Красноярск", x: 67.0, y: 6.8 },
  { name: "Монголия", x: 72.0, y: 18.9 },
  { name: "Китай", x: 75.2, y: 29.1 },
  { name: "Мьянма", x: 73.6, y: 39.1 },
  { name: "Таиланд", x: 74.2, y: 47.5 },
  { name: "Индонезия", x: 75.2, y: 60.0 },
  { name: "Филиппины", x: 86.4, y: 50.4 },
  { name: "Перу", x: 7.5, y: 58.4 },
  { name: "Бразилия", x: 25.1, y: 62.4 },
  { name: "Камерун", x: 34.3, y: 55.0 },
  { name: "Уганда", x: 44.4, y: 56.0 },
  { name: "Сомали", x: 51.0, y: 63.6 },
  { name: "Индия", x: 57.8, y: 39.4 },
  { name: "Узбекистан", x: 52.9, y: 22.1 },
  { name: "Красноярск", x: 67.0, y: 6.8 },
];

const LEVELS = {
  easy: {
    title: "Легкий уровень",
    label: "Легкий",
    wrongStepBack: 1,
  },
  medium: {
    title: "Средний уровень",
    label: "Средний",
    wrongStepBack: 2,
  },
  hard: {
    title: "Сложный уровень",
    label: "Сложный",
    wrongStepBack: 0,
  },
};

const DAYS_PER_MOVE = 5;
const TOTAL_DAYS = 80;
const HARD_RESULTS_KEY = "vk_world_game_hard_results";

const state = {
  data: null,
  countryQuestions: new Map(),
  questionCursor: new Map(),
  level: null,
  currentStep: 0,
  visualPosition: 0,
  correct: 0,
  wrong: 0,
  moves: 0,
  days: 0,
  startedAt: 0,
  currentQuestion: null,
  currentOptions: [],
  locked: false,
  debug: new URLSearchParams(window.location.search).get("debug") === "1",
};

const elements = {
  welcomeScreen: document.querySelector("#welcome-screen"),
  levelScreen: document.querySelector("#level-screen"),
  gameScreen: document.querySelector("#game-screen"),
  resultScreen: document.querySelector("#result-screen"),
  toLevelsButton: document.querySelector("#to-levels-button"),
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
  finalLevel: document.querySelector("#final-level"),
  finalDays: document.querySelector("#final-days"),
  finalMoves: document.querySelector("#final-moves"),
  finalCorrect: document.querySelector("#final-correct"),
  finalWrong: document.querySelector("#final-wrong"),
  finalRank: document.querySelector("#final-rank"),
  rankRow: document.querySelector("#rank-row"),
  resultKicker: document.querySelector("#result-kicker"),
  resultTitle: document.querySelector("#result-title"),
  resultMessage: document.querySelector("#result-message"),
  restartButton: document.querySelector("#restart-button"),
  routePoints: document.querySelector("#route-points"),
  balloon: document.querySelector("#balloon"),
};

function initVkBridge() {
  if (window.vkBridge && !window.__vkInitSent) {
    window.__vkInitSent = true;
    window.vkBridge.send("VKWebAppInit").catch(() => {});
  }
}

function showScreen(screen) {
  [elements.welcomeScreen, elements.levelScreen, elements.gameScreen, elements.resultScreen].forEach((item) => {
    item.classList.toggle("hidden", item !== screen);
  });
}

function shuffle(items) {
  return [...items]
    .map((value) => ({ value, sort: Math.random() }))
    .sort((a, b) => a.sort - b.sort)
    .map(({ value }) => value);
}

function questionCountries() {
  return POINTS.slice(1, -1).map((point) => point.name);
}

function routeIndexByCountry(country) {
  if (!country) return -1;
  return questionCountries().findIndex((item) => item === country);
}

function groupQuestions(questions) {
  state.countryQuestions = new Map();
  questions.forEach((item) => {
    if (!state.countryQuestions.has(item.country)) {
      state.countryQuestions.set(item.country, []);
    }
    state.countryQuestions.get(item.country).push(item);
  });
}

function normalizeOptions(question) {
  if (Array.isArray(question.options) && question.options.length > 0) {
    return question.options.map((option) => ({
      text: option.text,
      target: option.target || "",
    }));
  }
  return question.answers.map((answer) => ({
    text: answer,
    target: answer === question.correct ? question.country : "",
  }));
}

function drawMap() {
  elements.routePoints.innerHTML = "";
  POINTS.forEach((point, index) => {
    const marker = document.createElement("span");
    marker.className = "route-point";
    marker.style.left = `${point.x}%`;
    marker.style.top = `${point.y}%`;
    marker.dataset.index = String(index);
    elements.routePoints.appendChild(marker);
  });
}

function updateMap() {
  document.querySelectorAll(".route-point").forEach((marker) => {
    const index = Number(marker.dataset.index);
    marker.classList.toggle("done", index < state.visualPosition);
    marker.classList.toggle("current", index === state.visualPosition);
  });

  const point = POINTS[state.visualPosition];
  elements.balloon.style.left = `${point.x}%`;
  elements.balloon.style.top = `${point.y}%`;
}

function updateStats() {
  elements.correctCount.textContent = String(state.correct);
  elements.wrongCount.textContent = String(state.wrong);
  elements.movesCount.textContent = String(state.moves);
  elements.daysCount.textContent = String(state.days);
  elements.progressCurrent.textContent = String(state.currentStep);
  elements.questionNumber.textContent = String(Math.min(state.currentStep + 1, questionCountries().length));
}

function pickQuestion(country) {
  const pool = state.countryQuestions.get(country) || [];
  if (pool.length === 0) {
    throw new Error(`No questions for country: ${country}`);
  }

  const cursor = state.questionCursor.get(country) || 0;
  state.questionCursor.set(country, cursor + 1);
  return pool[cursor % pool.length];
}

function renderQuestion() {
  const countries = questionCountries();
  const country = countries[state.currentStep];
  const question = pickQuestion(country);

  state.currentQuestion = question;
  state.currentOptions = shuffle(normalizeOptions(question));
  state.locked = false;

  elements.nextCountry.textContent = country;
  elements.questionCountry.textContent = country;
  elements.questionText.textContent = question.question;
  elements.answers.innerHTML = "";

  state.currentOptions.forEach((option, index) => {
    const button = document.createElement("button");
    button.className = "answer-button";
    button.type = "button";
    button.dataset.answer = option.text;
    button.innerHTML = `<span class="answer-letter">${String.fromCharCode(65 + index)}</span><span>${option.text}</span>`;
    if (state.debug && option.text === question.correct) {
      button.classList.add("debug-correct");
      button.title = "Debug: правильный ответ";
    }
    button.addEventListener("click", () => handleAnswer(option, button));
    elements.answers.appendChild(button);
  });

  updateStats();
  updateMap();
}

function setButtonsDisabled(disabled) {
  document.querySelectorAll(".answer-button").forEach((button) => {
    button.disabled = disabled;
  });
}

function moveOnWrongAnswer(option) {
  if (state.level === "hard") {
    if (option.target === "Красноярск") {
      return 0;
    }
    const targetIndex = routeIndexByCountry(option.target);
    if (targetIndex >= 0) {
      return targetIndex;
    }
    return Math.max(0, state.currentStep - 1);
  }

  const back = LEVELS[state.level].wrongStepBack;
  return Math.max(0, state.currentStep - back);
}

function handleAnswer(option, button) {
  if (state.locked) return;
  state.locked = true;
  setButtonsDisabled(true);

  state.moves += 1;
  state.days = Math.min(999, state.days + DAYS_PER_MOVE);

  const isCorrect = option.text === state.currentQuestion.correct;
  if (isCorrect) {
    state.correct += 1;
    state.currentStep += 1;
    state.visualPosition = state.currentStep;
    button.classList.add("correct");
  } else {
    state.wrong += 1;
    state.currentStep = moveOnWrongAnswer(option);
    state.visualPosition = state.currentStep;
    button.classList.add("wrong");

    document.querySelectorAll(".answer-button").forEach((item) => {
      if (item.dataset.answer === state.currentQuestion.correct) {
        item.classList.add("correct");
      }
    });
  }

  updateStats();
  updateMap();

  window.setTimeout(() => {
    if (state.currentStep >= questionCountries().length) {
      finishGame();
    } else if (state.days > TOTAL_DAYS) {
      finishGame();
    } else {
      renderQuestion();
    }
  }, 850);
}

function hardRank(result) {
  let results = [];
  try {
    results = JSON.parse(localStorage.getItem(HARD_RESULTS_KEY) || "[]");
  } catch {
    results = [];
  }
  results.push(result);
  results.sort((a, b) => a.moves - b.moves || a.seconds - b.seconds);
  localStorage.setItem(HARD_RESULTS_KEY, JSON.stringify(results.slice(0, 50)));
  return results.findIndex((item) => item.id === result.id) + 1;
}

function finishGame() {
  const countries = questionCountries();
  const completed = state.currentStep >= countries.length;
  const success = completed && state.days <= TOTAL_DAYS;
  const seconds = Math.max(1, Math.round((Date.now() - state.startedAt) / 1000));

  state.visualPosition = success ? POINTS.length - 1 : state.visualPosition;
  updateMap();
  updateStats();

  elements.finalLevel.textContent = LEVELS[state.level].label;
  elements.finalDays.textContent = String(state.days);
  elements.finalMoves.textContent = String(state.moves);
  elements.finalCorrect.textContent = String(state.correct);
  elements.finalWrong.textContent = String(state.wrong);

  elements.rankRow.classList.add("hidden");
  if (success) {
    elements.resultKicker.textContent = "Маршрут завершен";
    elements.resultTitle.textContent = "Поздравляю, уровень пройден";
    elements.resultMessage.textContent =
      "Сделайте скрин этой страницы и представьте ее в ООО Путешествие для получения скидки.";
    if (state.level === "hard") {
      const place = hardRank({
        id: `${Date.now()}-${Math.random()}`,
        moves: state.moves,
        seconds,
      });
      elements.finalRank.textContent = String(place);
      elements.rankRow.classList.remove("hidden");
    }
  } else {
    elements.resultKicker.textContent = "Маршрут не завершен";
    elements.resultTitle.textContent = "К сожалению, вы не справились с заданием";
    elements.resultMessage.textContent = "Попробуйте еще раз и постарайтесь пройти кругосветное путешествие за 80 дней.";
  }

  showScreen(elements.resultScreen);
}

function startGame(level) {
  state.level = level;
  state.questionCursor = new Map();
  state.currentStep = 0;
  state.visualPosition = 0;
  state.correct = 0;
  state.wrong = 0;
  state.moves = 0;
  state.days = 0;
  state.startedAt = Date.now();
  elements.levelTitle.textContent = LEVELS[level].title;
  showScreen(elements.gameScreen);
  renderQuestion();
}

function restartGame() {
  showScreen(elements.levelScreen);
}

async function loadGame() {
  initVkBridge();
  drawMap();
  updateMap();

  for (const url of ["/data/questions.json", "/api/game-data"]) {
    const response = await fetch(url, { cache: "no-store" });
    const contentType = response.headers.get("content-type") || "";
    if (response.ok && contentType.includes("application/json")) {
      state.data = await response.json();
      groupQuestions(state.data.questions);
      return;
    }
  }

  throw new Error("Не найден файл с вопросами");
}

elements.toLevelsButton.addEventListener("click", () => showScreen(elements.levelScreen));
document.querySelectorAll(".level-button").forEach((button) => {
  button.addEventListener("click", () => startGame(button.dataset.level));
});
elements.restartButton.addEventListener("click", restartGame);

loadGame().catch((error) => {
  elements.toLevelsButton.disabled = true;
  elements.toLevelsButton.textContent = "Не удалось загрузить игру";
  console.error(error);
});
