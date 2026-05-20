from __future__ import annotations

import html
import json
import random
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from game_engine import GameEngine


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "questions.json"
DATA_DIR = ROOT / "data"
STATIC_DIR = ROOT / "static"
VK_MESSAGES_SEND_URL = "https://api.vk.com/method/messages.send"

app = FastAPI(title="VK World Game")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")
engine = GameEngine(DATA_FILE)


class StartGameRequest(BaseModel):
    vk_user_id: int | None = None


class AnswerRequest(BaseModel):
    option_index: int


def send_vk_result(vk_user_id: int | None, text: str) -> bool:
    if not vk_user_id or not settings.vk_group_token:
        return False
    payload: dict[str, Any] = {
        "access_token": settings.vk_group_token,
        "v": settings.vk_api_version,
        "user_id": vk_user_id,
        "message": text,
        "random_id": random.randint(1, 2_147_483_647),
    }
    body = urllib.parse.urlencode(payload).encode("utf-8")
    try:
        with urllib.request.urlopen(VK_MESSAGES_SEND_URL, data=body, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
    except OSError:
        return False
    return "response" in data


def page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(
        f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{html.escape(title)}</title>
    <link rel="stylesheet" href="/static/styles.css?v=20260519-nojs1" />
    <script src="/static/vendor/vk-bridge.min.js?v=20260516"></script>
    <script>
      if (window.vkBridge) {{
        window.vkBridge.send("VKWebAppInit").catch(function () {{}});
      }}
    </script>
  </head>
  <body>
    <main class="app-shell">
      <div class="cloud-layer" aria-hidden="true">
        <span class="cloud cloud-one"></span>
        <span class="cloud cloud-two"></span>
        <span class="cloud cloud-three"></span>
        <span class="cloud cloud-four"></span>
        <span class="cloud cloud-five"></span>
        <span class="cloud cloud-six"></span>
      </div>
      {body}
    </main>
  </body>
</html>"""
    )


def map_html(view: dict[str, Any]) -> str:
    points = []
    for index, point in enumerate(view["route"]):
        classes = ["route-point"]
        if index < view["position"]:
            classes.append("done")
        if index == view["position"]:
            classes.append("current")
        points.append(
            f'<span class="{" ".join(classes)}" style="left:{point["x"]}%;top:{point["y"]}%"></span>'
        )
    current = view["route"][view["position"]]
    return f"""
      <div class="map-stage game-map">
        <img src="/static/assets/world-map-cartoon-20260517.jpg" alt="Маршрут кругосветного путешествия" />
        <div class="route-points">{''.join(points)}</div>
        <div class="balloon" style="left:{current["x"]}%;top:{current["y"]}%" aria-label="Воздушный шар">
          <span class="balloon-top"></span>
          <span class="balloon-basket"></span>
        </div>
      </div>
    """


def render_welcome(vk_user_id: int | None = None) -> HTMLResponse:
    user_input = f'<input type="hidden" name="vk_user_id" value="{vk_user_id}" />' if vk_user_id else ""
    return page(
        "Вокруг света за 80 дней",
        f"""
      <section class="screen welcome-screen">
        <div class="map-stage welcome-map">
          <img src="/static/assets/world-map-cartoon-20260517.jpg" alt="Карта кругосветного путешествия" />
          <div class="welcome-copy">
            <p class="eyebrow">ООО Путешествие</p>
            <h1>Добро пожаловать в кругосветное путешествие</h1>
            <p>Ответьте на вопросы, пройдите маршрут и получите скидку.</p>
            <form class="action-form" method="post" action="/play/start">
              {user_input}
              <button class="primary-button" type="submit">Начать игру</button>
            </form>
          </div>
        </div>
      </section>
        """,
    )


def render_game(view: dict[str, Any]) -> HTMLResponse:
    stats = view["stats"]
    question = view["question"]
    answers = []
    for index, option in enumerate(question["options"]):
        letter = chr(65 + index)
        answers.append(
            f'<form class="answer-form" method="post" action="/play/{view["session_id"]}/answer/{index}">'
            f'<button class="answer-button" type="submit">'
            f'<span class="answer-letter">{letter}</span><span>{html.escape(option)}</span></button></form>'
        )
    return page(
        "Вокруг света за 80 дней",
        f"""
      <section class="screen game-screen">
        <section class="topbar" aria-label="Статистика игры">
          <div>
            <p class="eyebrow">Вокруг света за 80 дней</p>
            <h1>{html.escape(view["level"]["title"])}</h1>
          </div>
          <div class="score-row">
            <span class="score-pill"><span>Дней</span><b><span>{stats["days"]}</span>/80</b></span>
            <span class="score-pill"><span>Ходы</span><b>{stats["moves"]}</b></span>
            <span class="score-pill good"><span>Верно</span><b>{stats["correct"]}</b></span>
            <span class="score-pill bad"><span>Ошибки</span><b>{stats["wrong"]}</b></span>
          </div>
        </section>

        <section class="game-layout">
          <section class="map-panel" aria-label="Игровая карта">
            <div class="map-head">
              <div>
                <span class="muted">Следующая остановка</span>
                <strong>{html.escape(view["next_country"])}</strong>
              </div>
              <div class="route-hud">
                <span class="route-hud-label">Маршрут</span>
                <span class="progress-label">{view["progress"]}/{view["total"]}</span>
              </div>
            </div>
            {map_html(view)}
          </section>

          <section class="question-panel" aria-label="Вопрос">
            <div class="question-card">
              <div class="question-meta">
                <p class="country-kicker">{html.escape(question["country"])}</p>
                <span class="step-chip">Вопрос {question["number"]}</span>
              </div>
              <h2>{html.escape(question["text"])}</h2>
              <div class="answers">{''.join(answers)}</div>
            </div>
          </section>
        </section>
      </section>
        """,
    )


def render_result(view: dict[str, Any]) -> HTMLResponse:
    result = view["result"]
    stat_cards = "".join(
        f"<span>{html.escape(str(label))}<b>{html.escape(str(value))}</b></span>"
        for label, value in result["stats"].items()
    )
    promo = (
        f'<div class="promo-card">Промокод <b>{html.escape(result["promo"])}</b></div>'
        if result.get("promo")
        else ""
    )
    rank = (
        f'<div class="promo-card">Место среди участников <b>{result["rank"]}</b></div>'
        if result.get("rank")
        else ""
    )
    if result.get("next_level"):
        button_href = f'/play/{view["session_id"]}/next'
        button_text = f'Перейти на {result["next_level"]["label"].lower()} уровень'
        button_method = "post"
    else:
        button_href = "/"
        button_text = "Играть еще раз" if view["status"] == "completed" else "Попробовать еще раз"
        button_method = "get"
    kicker = "Маршрут завершен" if view["status"] == "completed" else "Маршрут уровня завершен"
    return page(
        "Результат игры",
        f"""
      <section class="screen result-screen">
        <div class="result-card">
          <p class="country-kicker">{html.escape(kicker)}</p>
          <h2>{html.escape(result["title"])}</h2>
          <p class="result-message">{html.escape(result["message"])}</p>
          <div class="final-stats">{stat_cards}</div>
          {promo}
          {rank}
          <form class="action-form" method="{button_method}" action="{button_href}">
            <button class="primary-button" type="submit">{html.escape(button_text)}</button>
          </form>
        </div>
      </section>
        """,
    )


def render_view(view: dict[str, Any]) -> HTMLResponse:
    if view["status"] == "playing":
        return render_game(view)
    return render_result(view)


@app.get("/")
def index(request: Request) -> HTMLResponse:
    user_id = request.query_params.get("vk_user_id") or request.query_params.get("viewer_id")
    return render_welcome(int(user_id) if user_id and user_id.isdigit() else None)


@app.get("/play/start")
def start_play(request: Request) -> RedirectResponse:
    user_id = request.query_params.get("vk_user_id") or request.query_params.get("viewer_id")
    view = engine.start(int(user_id) if user_id and user_id.isdigit() else None)
    return RedirectResponse(f'/play/{view["session_id"]}', status_code=303)


@app.post("/play/start")
async def start_play_post(request: Request) -> RedirectResponse:
    body = (await request.body()).decode("utf-8", "replace")
    form = urllib.parse.parse_qs(body)
    user_id = str((form.get("vk_user_id") or [""])[0])
    view = engine.start(int(user_id) if user_id.isdigit() else None)
    return RedirectResponse(f'/play/{view["session_id"]}', status_code=303)


@app.get("/play/{session_id}")
def play(session_id: str) -> HTMLResponse:
    try:
        session = engine.sessions[session_id]
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Игровая сессия не найдена") from error
    return render_view(engine.public_state(session))


@app.get("/play/{session_id}/answer/{option_index}")
def play_answer(session_id: str, option_index: int) -> RedirectResponse:
    try:
        result = engine.answer(session_id, option_index)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if result["state"]["status"] == "completed":
        session = engine.sessions.get(session_id)
        if session and not session.notified:
            session.notified = send_vk_result(session.vk_user_id, engine.final_summary(session))
    return RedirectResponse(f"/play/{session_id}", status_code=303)


@app.post("/play/{session_id}/answer/{option_index}")
def play_answer_post(session_id: str, option_index: int) -> RedirectResponse:
    return play_answer(session_id, option_index)


@app.get("/play/{session_id}/next")
def play_next(session_id: str) -> RedirectResponse:
    try:
        engine.continue_next_level(session_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return RedirectResponse(f"/play/{session_id}", status_code=303)


@app.post("/play/{session_id}/next")
def play_next_post(session_id: str) -> RedirectResponse:
    return play_next(session_id)


@app.get("/api/game-data")
def game_data() -> dict:
    if not DATA_FILE.exists():
        raise HTTPException(status_code=404, detail="questions.json not found")
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


@app.get("/api/bootstrap")
def bootstrap() -> dict:
    return engine.bootstrap()


@app.post("/api/session")
def start_session(request: StartGameRequest) -> dict:
    try:
        return engine.start(request.vk_user_id)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/session/{session_id}/answer")
def answer(session_id: str, request: AnswerRequest) -> dict:
    try:
        result = engine.answer(session_id, request.option_index)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    state = result["state"]
    if state["status"] == "completed":
        session = engine.sessions.get(session_id)
        if session and not session.notified:
            session.notified = send_vk_result(session.vk_user_id, engine.final_summary(session))
    return result


@app.post("/api/session/{session_id}/continue")
def continue_level(session_id: str) -> dict:
    try:
        return engine.continue_next_level(session_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
