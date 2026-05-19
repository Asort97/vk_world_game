from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"


def copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("*.zip", "*.tar", "*.tar.gz"))


def main() -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()

    copytree(ROOT / "static", BUILD / "static")
    copytree(ROOT / "data", BUILD / "data")

    print(f"Static build ready: {BUILD}")


if __name__ == "__main__":
    main()
