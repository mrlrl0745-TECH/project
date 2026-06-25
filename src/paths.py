from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
DATA_DIR = ROOT_DIR / "data"
SAVEGAME_PATH = ROOT_DIR / "savegame.json"
DATABASE_PATH = DATA_DIR / "users.sqlite3"
