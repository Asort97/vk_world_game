from __future__ import annotations

from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = {
    ".py": "Python",
    ".js": "JavaScript",
    ".css": "CSS",
    ".html": "HTML",
}


def tracked_source_files() -> list[Path]:
    ignored = {"deploy_static_vps.ps1", "vk-hosting-config.json"}
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and ".venv" not in path.parts
        and "build" not in path.parts
        and path.name not in ignored
        and path.suffix in LANGUAGES
    ]


def main() -> None:
    totals: dict[str, int] = defaultdict(int)
    for path in tracked_source_files():
        totals[LANGUAGES[path.suffix]] += path.stat().st_size

    overall = sum(totals.values()) or 1
    for language, size in sorted(totals.items(), key=lambda item: item[1], reverse=True):
        percent = size / overall * 100
        print(f"{language}: {percent:.1f}% ({size} bytes)")


if __name__ == "__main__":
    main()
