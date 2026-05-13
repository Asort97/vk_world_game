const POINTS = [
  { name: "Красноярск", x: 69, y: 24 },
  { name: "Монголия", x: 65, y: 34 },
  { name: "Китай", x: 71, y: 43 },
  { name: "Мьянма", x: 68, y: 53 },
  { name: "Таиланд", x: 70, y: 60 },
  { name: "Индонезия", x: 76, y: 72 },
  { name: "Филиппины", x: 82, y: 58 },
  { name: "Перу", x: 26, y: 70 },
  { name: "Бразилия", x: 35, y: 76 },
  { name: "Камерун", x: 51, y: 62 },
  { name: "Уганда", x: 57, y: 68 },
  { name: "Сомали", x: 62, y: 67 },
  { name: "Индия", x: 63, y: 52 },
  { name: "Узбекистан", x: 56, y: 42 },
  { name: "Красноярск", x: 69, y: 24 },
];

const state = {
  data: null,
  countryQuestions: new Map(),
  questionCursor: new Map(),
  currentStep: 0,
  visualPosition: 0,
  correct: 0,
  wrong: 0,
  currentQuestion: null,
  currentAnswers: [],
  locked: false,
};

const elements = {
  correctCount: document.querySelector("#correct-count"),
  wrongCount: document.querySelector("#wrong-count"),
  progressCurrent: document.querySelector("#progress-current"),
  nextCountry: document.querySelector("#next-country"),
  questionCountry: document.querySelector("#question-country"),
  questionText: document.querySelector("#question-text"),
  answers: document.querySelector("#answers"),
  questionCard: document.querySelector("#question-card"),
  resultCard: document.querySelector("#result-card"),
  finalCorrect: document.querySelector("#final-correct"),
  finalWrong: document.querySelector("#final-wrong"),
  restartButton: document.querySelector("#restart-button"),
  routeLine: document.querySelector("#route-line"),
  routeDone: document.querySelector("#route-done"),
  routePoints: document.querySelector("#route-points"),
  balloon: document.querySelector("#balloon"),
};

function initVkBridge() {
  if (window.vkBridge) {
    window.vkBridge.send("VKWebAppInit").catch(() => {});
  }
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

function groupQuestions(questions) {
  state.countryQuestions = new Map();
  questions.forEach((item) => {
    if (!state.countryQuestions.has(item.country)) {
      state.countryQuestions.set(item.country, []);
    }
    state.countryQuestions.get(item.country).push(item);
  });
}

function pointsToSvg(points) {
  return points.map((point) => `${point.x * 10},${point.y * 5.6}`).join(" ");
}

function drawMap() {
  elements.routeLine.setAttribute("points", pointsToSvg(POINTS));
  elements.routePoints.innerHTML = "";

  POINTS.forEach((point, index) => {
    const marker = document.createElement("span");
    marker.className = "route-point";
    marker.style.left = `${point.x}%`;
    marker.style.top = `${point.y}%`;
    marker.dataset.index = String(index);
    elements.routePoints.appendChild(marker);

    const label = document.createElement("span");
    label.className = "route-label";
    label.style.left = `${point.x}%`;
    label.style.top = `${point.y}%`;
    label.textContent = point.name;
    elements.routePoints.appendChild(label);
  });
}

function updateMap() {
  const donePoints = POINTS.slice(0, state.visualPosition + 1);
  elements.routeDone.setAttribute("points", pointsToSvg(donePoints));

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
  elements.progressCurrent.textContent = String(state.currentStep);
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
  state.currentAnswers = shuffle(question.answers);
  state.locked = false;

  elements.nextCountry.textContent = country;
  elements.questionCountry.textContent = country;
  elements.questionText.textContent = question.question;
  elements.answers.innerHTML = "";

  state.currentAnswers.forEach((answer) => {
    const button = document.createElement("button");
    button.className = "answer-button";
    button.type = "button";
    button.textContent = answer;
    button.addEventListener("click", () => handleAnswer(answer, button));
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

function handleAnswer(answer, button) {
  if (state.locked) return;
  state.locked = true;
  setButtonsDisabled(true);

  const isCorrect = answer === state.currentQuestion.correct;
  if (isCorrect) {
    state.correct += 1;
    state.currentStep += 1;
    state.visualPosition = state.currentStep;
    button.classList.add("correct");
  } else {
    state.wrong += 1;
    state.currentStep = Math.max(0, state.currentStep - 1);
    state.visualPosition = state.currentStep;
    button.classList.add("wrong");

    document.querySelectorAll(".answer-button").forEach((item) => {
      if (item.textContent === state.currentQuestion.correct) {
        item.classList.add("correct");
      }
    });
  }

  updateStats();
  updateMap();

  window.setTimeout(() => {
    if (state.currentStep >= questionCountries().length) {
      finishGame();
    } else {
      renderQuestion();
    }
  }, 850);
}

function finishGame() {
  state.visualPosition = POINTS.length - 1;
  updateMap();
  updateStats();
  elements.questionCard.classList.add("hidden");
  elements.resultCard.classList.remove("hidden");
  elements.finalCorrect.textContent = String(state.correct);
  elements.finalWrong.textContent = String(state.wrong);
  elements.nextCountry.textContent = "Финиш";
}

function restartGame() {
  state.questionCursor = new Map();
  state.currentStep = 0;
  state.visualPosition = 0;
  state.correct = 0;
  state.wrong = 0;
  elements.resultCard.classList.add("hidden");
  elements.questionCard.classList.remove("hidden");
  renderQuestion();
}

async function loadGame() {
  initVkBridge();
  drawMap();
  const response = await fetch("/api/game-data");
  state.data = await response.json();
  groupQuestions(state.data.questions);
  renderQuestion();
}

elements.restartButton.addEventListener("click", restartGame);
loadGame().catch((error) => {
  elements.questionText.textContent = "Не удалось загрузить игру";
  elements.answers.innerHTML = `<p class="muted">${error.message}</p>`;
});
