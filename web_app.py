from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "questions.json"
DATA_DIR = ROOT / "data"
STATIC_DIR = ROOT / "static"

app = FastAPI(title="VK World Game")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/game-data")
def game_data() -> dict:
    if not DATA_FILE.exists():
        raise HTTPException(status_code=404, detail="questions.json not found")
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))
