from __future__ import annotations

import json
import random
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
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


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


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
