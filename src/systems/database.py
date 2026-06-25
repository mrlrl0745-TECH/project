from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from paths import DATABASE_PATH


DB_PATH = DATABASE_PATH


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                name TEXT PRIMARY KEY,
                ui_language TEXT NOT NULL DEFAULT 'ru',
                best_coins REAL NOT NULL DEFAULT 0,
                rebirths INTEGER NOT NULL DEFAULT 0,
                total_coins REAL NOT NULL DEFAULT 0,
                attacks INTEGER NOT NULL DEFAULT 0,
                games_won INTEGER NOT NULL DEFAULT 0,
                last_seen TEXT NOT NULL
            )
            """
        )
        conn.commit()


def upsert_user(game_state, session_total: float = 0.0) -> None:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO users (name, ui_language, best_coins, rebirths, total_coins, attacks, games_won, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                ui_language=excluded.ui_language,
                best_coins=max(users.best_coins, excluded.best_coins),
                rebirths=excluded.rebirths,
                total_coins=users.total_coins + excluded.total_coins,
                attacks=excluded.attacks,
                games_won=excluded.games_won,
                last_seen=excluded.last_seen
            """,
            (
                game_state.player_name,
                game_state.ui_language,
                float(game_state.player.coins),
                int(game_state.rebirths),
                float(session_total),
                int(game_state.player.attacks_done),
                int(game_state.player.games_won),
                now,
            ),
        )
        conn.commit()


def top_users(limit: int = 5) -> list[dict]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT name, best_coins, rebirths FROM users ORDER BY rebirths DESC, best_coins DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {"name": row["name"], "coins": int(row["best_coins"]), "rebirths": row["rebirths"]}
        for row in rows
    ]
