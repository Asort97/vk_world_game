from __future__ import annotations

import json
import random
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


POINTS = [
    {"name": "Красноярск", "x": 60.5, "y": 17.0},
    {"name": "Монголия", "x": 75.7, "y": 19.4},
    {"name": "Китай", "x": 77.1, "y": 29.4},
    {"name": "Мьянма", "x": 76.8, "y": 40.1},
    {"name": "Таиланд", "x": 75.7, "y": 48.0},
    {"name": "Индонезия", "x": 76.8, "y": 62.1},
    {"name": "Филиппины", "x": 89.9, "y": 52.6},
    {"name": "Перу", "x": 19.6, "y": 68.6},
    {"name": "Бразилия", "x": 29.0, "y": 61.7},
    {"name": "Камерун", "x": 36.2, "y": 56.5},
    {"name": "Уганда", "x": 45.7, "y": 56.9},
    {"name": "Сомали", "x": 50.9, "y": 63.4},
    {"name": "Индия", "x": 57.4, "y": 39.8},
    {"name": "Узбекистан", "x": 50.0, "y": 22.5},
    {"name": "Красноярск", "x": 60.5, "y": 17.0},
]

LEVELS = [
    {"key": "easy", "label": "Легкий", "title": "Легкий уровень", "block": "Блок 1", "wrong_back": 1},
    {"key": "medium", "label": "Средний", "title": "Средний уровень", "block": "Блок 2", "wrong_back": 2},
    {"key": "hard", "label": "Сложный", "title": "Сложный уровень", "block": "Блок 3", "wrong_back": 0},
]

COUNTRIES = [point["name"] for point in POINTS[1:-1]]
DAYS_PER_MOVE = 5
TOTAL_DAYS = 80
SESSION_TTL_SECONDS = 6 * 60 * 60


@dataclass
class GameSession:
    id: str
    vk_user_id: int | None = None
    level_index: int = 0
    step: int = 0
    visual_position: int = 0
    correct: int = 0
    wrong: int = 0
    moves: int = 0
    days: int = 0
    started_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    current_question: dict[str, Any] | None = None
    current_options: list[dict[str, Any]] = field(default_factory=list)
    completed_levels: list[dict[str, Any]] = field(default_factory=list)
    final_promo: str = ""
    notified: bool = False
    level_finished: bool = False


class GameEngine:
    def __init__(self, data_file: Path) -> None:
        self.data_file = data_file
        self.sessions: dict[str, GameSession] = {}
        self.hard_results: list[dict[str, Any]] = []
        self.questions_by_level = self._load_questions()

    def bootstrap(self) -> dict[str, Any]:
        return {
            "route": POINTS,
            "countries": COUNTRIES,
            "levels": [{"key": item["key"], "label": item["label"], "title": item["title"]} for item in LEVELS],
            "total_days": TOTAL_DAYS,
        }

    def start(self, vk_user_id: int | None = None) -> dict[str, Any]:
        self._cleanup()
        session = GameSession(id=uuid.uuid4().hex, vk_user_id=vk_user_id)
        self.sessions[session.id] = session
        self._pick_question(session)
        return self.public_state(session)

    def continue_next_level(self, session_id: str) -> dict[str, Any]:
        session = self._session(session_id)
        if session.level_index >= len(LEVELS) - 1:
            return self.public_state(session)
        session.level_index += 1
        self._reset_level(session)
        self._pick_question(session)
        return self.public_state(session)

    def answer(self, session_id: str, option_index: int) -> dict[str, Any]:
        session = self._session(session_id)
        if session.current_question is None or not session.current_options:
            raise ValueError("Вопрос не подготовлен")
        if option_index < 0 or option_index >= len(session.current_options):
            raise ValueError("Такого варианта ответа нет")

        option = session.current_options[option_index]
        correct_text = str(session.current_question["correct"])
        is_correct = option["text"] == correct_text

        session.moves += 1
        session.days = min(999, session.days + DAYS_PER_MOVE)
        if is_correct:
            session.correct += 1
            session.step += 1
        else:
            session.wrong += 1
            session.step = self._wrong_step(session, option)
        session.visual_position = session.step
        session.updated_at = time.time()

        feedback = {
            "selected_index": option_index,
            "correct_index": self._correct_index(session),
            "is_correct": is_correct,
        }

        if session.step >= len(COUNTRIES) or session.days > TOTAL_DAYS:
            self._finish_level(session)
            return {"feedback": feedback, "state": self.public_state(session)}

        self._pick_question(session)
        return {"feedback": feedback, "state": self.public_state(session)}

    def final_summary(self, session: GameSession) -> str:
        total_correct = sum(item["correct"] for item in session.completed_levels)
        total_wrong = sum(item["wrong"] for item in session.completed_levels)
        total_moves = sum(item["moves"] for item in session.completed_levels)
        total_seconds = sum(item["seconds"] for item in session.completed_levels)
        promo = session.final_promo or "не выдан"
        return (
            "Игра завершена.\n"
            f"Время: {self._format_seconds(total_seconds)}\n"
            f"Ходы: {total_moves}\n"
            f"Верных ответов: {total_correct}\n"
            f"Неверных ответов: {total_wrong}\n"
            f"Промокод: {promo}"
        )

    def public_state(self, session: GameSession) -> dict[str, Any]:
        level = LEVELS[session.level_index]
        status = self._status(session)
        question = None
        if status == "playing" and session.current_question:
            question = {
                "country": COUNTRIES[session.step],
                "number": session.step + 1,
                "text": session.current_question["question"],
                "options": [item["text"] for item in session.current_options],
            }

        return {
            "session_id": session.id,
            "status": status,
            "level": {"key": level["key"], "label": level["label"], "title": level["title"]},
            "route": POINTS,
            "position": session.visual_position,
            "progress": min(session.step, len(COUNTRIES)),
            "total": len(COUNTRIES),
            "next_country": COUNTRIES[min(session.step, len(COUNTRIES) - 1)],
            "stats": self._stats(session),
            "question": question,
            "result": self._result(session) if status != "playing" else None,
        }

    def _load_questions(self) -> dict[str, dict[str, list[dict[str, Any]]]]:
        if not self.data_file.exists():
            raise FileNotFoundError(f"questions file not found: {self.data_file}")
        data = json.loads(self.data_file.read_text(encoding="utf-8"))
        grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
        for level in LEVELS:
            grouped[level["key"]] = {country: [] for country in COUNTRIES}
        for item in data.get("questions", []):
            country = item.get("country")
            block = item.get("block")
            if country not in COUNTRIES:
                continue
            for level in LEVELS:
                if block == level["block"]:
                    grouped[level["key"]][country].append(item)
        return grouped

    def _session(self, session_id: str) -> GameSession:
        try:
            session = self.sessions[session_id]
        except KeyError as error:
            raise ValueError("Игровая сессия не найдена") from error
        session.updated_at = time.time()
        return session

    def _pick_question(self, session: GameSession) -> None:
        level = LEVELS[session.level_index]
        country = COUNTRIES[session.step]
        pool = self.questions_by_level[level["key"]].get(country, [])
        if not pool:
            raise ValueError(f"Нет вопроса для страны: {country}")
        question = random.choice(pool)
        session.current_question = question
        session.current_options = self._normalize_options(question)
        random.shuffle(session.current_options)

    def _normalize_options(self, question: dict[str, Any]) -> list[dict[str, Any]]:
        if question.get("options"):
            return [{"text": item["text"], "target": item.get("target", "")} for item in question["options"]]
        return [{"text": answer, "target": question["country"] if answer == question["correct"] else ""} for answer in question["answers"]]

    def _wrong_step(self, session: GameSession, option: dict[str, Any]) -> int:
        level = LEVELS[session.level_index]
        if level["key"] == "hard":
            target = option.get("target") or ""
            if target == "Красноярск":
                return 0
            if target in COUNTRIES:
                return COUNTRIES.index(target)
            return max(0, session.step - 1)
        return max(0, session.step - int(level["wrong_back"]))

    def _finish_level(self, session: GameSession) -> None:
        success = session.step >= len(COUNTRIES) and session.days <= TOTAL_DAYS
        seconds = max(1, int(time.time() - session.started_at))
        summary = {
            "level": LEVELS[session.level_index]["label"],
            "level_key": LEVELS[session.level_index]["key"],
            "success": success,
            "days": session.days,
            "moves": session.moves,
            "correct": session.correct,
            "wrong": session.wrong,
            "seconds": seconds,
        }
        if LEVELS[session.level_index]["key"] == "hard" and success:
            summary["rank"] = self._rank_hard(summary)
        session.completed_levels.append(summary)
        if success and session.level_index == len(LEVELS) - 1:
            session.final_promo = self._promo_code(session)
        session.visual_position = len(POINTS) - 1 if success else session.visual_position
        session.level_finished = True

    def _reset_level(self, session: GameSession) -> None:
        session.step = 0
        session.visual_position = 0
        session.correct = 0
        session.wrong = 0
        session.moves = 0
        session.days = 0
        session.started_at = time.time()
        session.current_question = None
        session.current_options = []
        session.level_finished = False

    def _status(self, session: GameSession) -> str:
        if not session.level_finished:
            return "playing"
        last = session.completed_levels[-1]
        if not last["success"]:
            return "failed"
        if session.level_index >= len(LEVELS) - 1:
            return "completed"
        return "level_complete"

    def _stats(self, session: GameSession) -> dict[str, Any]:
        return {
            "days": session.days,
            "moves": session.moves,
            "correct": session.correct,
            "wrong": session.wrong,
            "seconds": max(0, int(time.time() - session.started_at)),
        }

    def _result(self, session: GameSession) -> dict[str, Any]:
        last = session.completed_levels[-1]
        next_level = None
        if last["success"] and session.level_index < len(LEVELS) - 1:
            next_item = LEVELS[session.level_index + 1]
            next_level = {"key": next_item["key"], "label": next_item["label"]}
        title = "Поздравляю, уровень пройден" if last["success"] else "К сожалению, вы не справились с заданием"
        message = (
            "Сделайте скрин этой страницы и представьте ее в ООО Путешествие для получения скидки."
            if session.final_promo
            else "Переходите к следующему уровню, чтобы продолжить борьбу за скидку."
        )
        if not last["success"]:
            message = "Попробуйте еще раз и постарайтесь пройти кругосветное путешествие за 80 дней."
        return {
            "title": title,
            "message": message,
            "promo": session.final_promo,
            "rank": last.get("rank"),
            "next_level": next_level,
            "stats": {
                "Уровень": last["level"],
                "Дней": last["days"],
                "Ходов": last["moves"],
                "Верных ответов": last["correct"],
                "Неверных ответов": last["wrong"],
                "Время": self._format_seconds(last["seconds"]),
            },
        }

    def _correct_index(self, session: GameSession) -> int:
        correct = str(session.current_question["correct"]) if session.current_question else ""
        for index, option in enumerate(session.current_options):
            if option["text"] == correct:
                return index
        return -1

    def _rank_hard(self, result: dict[str, Any]) -> int:
        item = {"id": uuid.uuid4().hex, "moves": result["moves"], "seconds": result["seconds"]}
        self.hard_results.append(item)
        self.hard_results.sort(key=lambda row: (row["moves"], row["seconds"]))
        self.hard_results = self.hard_results[:100]
        return self.hard_results.index(item) + 1

    def _promo_code(self, session: GameSession) -> str:
        return f"TRAVEL-{session.id[:6].upper()}"

    def _format_seconds(self, seconds: int) -> str:
        minutes, rest = divmod(max(0, seconds), 60)
        return f"{minutes:02d}:{rest:02d}"

    def _cleanup(self) -> None:
        now = time.time()
        expired = [session_id for session_id, session in self.sessions.items() if now - session.updated_at > SESSION_TTL_SECONDS]
        for session_id in expired:
            self.sessions.pop(session_id, None)
