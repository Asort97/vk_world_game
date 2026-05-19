from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game_engine import GameEngine  # noqa: E402


def choose_correct_answer(engine: GameEngine, session_id: str) -> int:
    session = engine.sessions[session_id]
    correct = session.current_question["correct"]
    for index, option in enumerate(session.current_options):
        if option["text"] == correct:
            return index
    raise AssertionError(f"Correct answer is absent: {correct}")


def pass_current_level(engine: GameEngine, session_id: str) -> dict:
    state = engine.public_state(engine.sessions[session_id])
    while state["status"] == "playing":
        answer_index = choose_correct_answer(engine, session_id)
        state = engine.answer(session_id, answer_index)["state"]
    return state


def main() -> None:
    engine = GameEngine(ROOT / "data" / "questions.json")
    state = engine.start()
    session_id = state["session_id"]
    completed_levels = 0

    while True:
        state = pass_current_level(engine, session_id)
        completed_levels += 1
        if state["status"] == "completed":
            break
        if state["status"] != "level_complete":
            raise AssertionError(f"Unexpected game status: {state['status']}")
        state = engine.continue_next_level(session_id)

    result = state["result"]
    if completed_levels != 3:
        raise AssertionError(f"Expected 3 completed levels, got {completed_levels}")
    if not result["promo"]:
        raise AssertionError("Promo code was not issued")
    if len(result["stats"]) != 6:
        raise AssertionError("Result page must contain 6 statistic cards")

    print("Smoke test passed")
    print(f"Promo: {result['promo']}")
    print(f"Final level: {result['stats']['Уровень']}")


if __name__ == "__main__":
    main()
