const POINTS = [
  { name: "Красноярск", x: 16, y: 27, labelX: 10, labelY: 37 },
  { name: "Монголия", x: 26, y: 36, labelX: 24, labelY: 47 },
  { name: "Китай", x: 37, y: 44, labelX: 36, labelY: 55 },
  { name: "Мьянма", x: 48, y: 53, labelX: 48, labelY: 64 },
  { name: "Таиланд", x: 60, y: 62, labelX: 60, labelY: 73 },
  { name: "Индонезия", x: 72, y: 74, labelX: 72, labelY: 85 },
  { name: "Филиппины", x: 85, y: 62, labelX: 86, labelY: 52 },
  { name: "Перу", x: 79, y: 45, labelX: 79, labelY: 35 },
  { name: "Бразилия", x: 69, y: 33, labelX: 69, labelY: 23 },
  { name: "Камерун", x: 58, y: 26, labelX: 58, labelY: 16 },
  { name: "Уганда", x: 48, y: 22, labelX: 47, labelY: 12 },
  { name: "Сомали", x: 38, y: 18, labelX: 38, labelY: 8 },
  { name: "Индия", x: 29, y: 17, labelX: 30, labelY: 7 },
  { name: "Узбекистан", x: 21, y: 18, labelX: 20, labelY: 8 },
  { name: "Красноярск", x: 16, y: 27, labelX: 10, labelY: 37 },
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
  debug: new URLSearchParams(window.location.search).get("debug") === "1",
};

const elements = {
  correctCount: document.querySelector("#correct-count"),
  wrongCount: document.querySelector("#wrong-count"),
  progressCurrent: document.querySelector("#progress-current"),
  questionNumber: document.querySelector("#question-number"),
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
  labelLines: document.querySelector("#label-lines"),
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
  elements.labelLines.innerHTML = "";
  elements.routePoints.innerHTML = "";

  POINTS.forEach((point, index) => {
    const isDuplicateFinish = index === POINTS.length - 1;
    if (isDuplicateFinish) return;

    const leader = document.createElementNS("http://www.w3.org/2000/svg", "line");
    leader.setAttribute("x1", String((point.labelX || point.x) * 10));
    leader.setAttribute("y1", String((point.labelY || point.y) * 5.6));
    leader.setAttribute("x2", String(point.x * 10));
    leader.setAttribute("y2", String(point.y * 5.6));
    leader.setAttribute("class", "label-line");
    elements.labelLines.appendChild(leader);

    const marker = document.createElement("span");
    marker.className = "route-point";
    marker.style.left = `${point.x}%`;
    marker.style.top = `${point.y}%`;
    marker.dataset.index = String(index);
    elements.routePoints.appendChild(marker);

    const label = document.createElement("span");
    label.className = "route-label";
    label.style.left = `${point.labelX || point.x}%`;
    label.style.top = `${point.labelY || point.y}%`;
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
  state.currentAnswers = shuffle(question.answers);
  state.locked = false;

  elements.nextCountry.textContent = country;
  elements.questionCountry.textContent = country;
  elements.questionText.textContent = question.question;
  elements.answers.innerHTML = "";

  state.currentAnswers.forEach((answer, index) => {
    const button = document.createElement("button");
    button.className = "answer-button";
    button.type = "button";
    button.dataset.answer = answer;
    button.innerHTML = `<span class="answer-letter">${String.fromCharCode(65 + index)}</span><span>${answer}</span>`;
    if (state.debug && answer === question.correct) {
      button.classList.add("debug-correct");
      button.title = "Debug: правильный ответ";
    }
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

  for (const url of ["/data/questions.json", "/api/game-data"]) {
    const response = await fetch(url, { cache: "no-store" });
    const contentType = response.headers.get("content-type") || "";
    if (response.ok && contentType.includes("application/json")) {
      state.data = await response.json();
      groupQuestions(state.data.questions);
      renderQuestion();
      return;
    }
  }

  throw new Error("Не найден файл с вопросами");
}

elements.restartButton.addEventListener("click", restartGame);
loadGame().catch((error) => {
  elements.questionText.textContent = "Не удалось загрузить игру";
  elements.answers.innerHTML = `<p class="muted">${error.message}</p>`;
});
