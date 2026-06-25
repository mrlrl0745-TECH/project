from __future__ import annotations

import json
from models.player import Player
from paths import SAVEGAME_PATH
from systems.database import upsert_user


SAVE = SAVEGAME_PATH


def save_game(game_state) -> None:
    player: Player = game_state.player
    data = {
        "player_name": game_state.player_name,
        "ui_language": game_state.ui_language,
        "scene": game_state.scene,
        "coins": player.coins,
        "clicks": player.clicks,
        "health": player.health,
        "max_health": player.max_health,
        "x": player.x,
        "y": player.y,
        "speed": player.speed,
        "rebirths": game_state.rebirths,
        "permanent_multiplier": game_state.permanent_multiplier,
        "total_earned": game_state.total_earned,
        "db_synced_total": game_state.db_synced_total,
        "freelance_last_payout": game_state._freelance_last_payout,
        "base_chest_last": game_state._base_chest_last,
        "owned_languages": [
            {
                "id": language.id,
                "owned": language.owned,
                "income_multiplier": language.income_multiplier,
            }
            for language in player.languages
        ],
        "owned_upgrades": [
            {
                "name": upgrade.name,
                "bought": upgrade.bought,
                "purchased_for": list(upgrade.purchased_for),
            }
            for upgrade in player.upgrades
        ],
    }
    SAVE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    session_total = max(0.0, float(game_state.total_earned) - float(game_state.db_synced_total))
    upsert_user(game_state, session_total=session_total)
    game_state.db_synced_total = game_state.total_earned


def load_game(game_state) -> None:
    if not SAVE.exists():
        return

    raw = SAVE.read_text(encoding="utf-8").strip()
    if not raw:
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return

    player: Player = game_state.player
    player.coins = data.get("coins", 0)
    player.clicks = data.get("clicks", 0)
    player.health = data.get("health", 100)
    player.max_health = data.get("max_health", 100)
    player.x = data.get("x", player.x)
    player.y = data.get("y", player.y)
    player.speed = data.get("speed", player.speed)
    game_state.player_name = data.get("player_name", game_state.player_name)[:16] or "You"
    saved_language = data.get("ui_language")
    if saved_language in {"en", "ru"}:
        game_state.ui_language = saved_language
    scene = data.get("scene", game_state.scene)
    game_state.scene = scene if scene in {"world", "base"} else "world"
    game_state.rebirths = int(data.get("rebirths", game_state.rebirths))
    game_state.permanent_multiplier = float(data.get("permanent_multiplier", game_state.permanent_multiplier))
    game_state.total_earned = float(data.get("total_earned", game_state.total_earned))
    game_state.db_synced_total = float(data.get("db_synced_total", game_state.total_earned))
    player.rebirths = game_state.rebirths
    player.rebirth_bonus = game_state.permanent_multiplier
    game_state._freelance_last_payout = float(data.get("freelance_last_payout", game_state._freelance_last_payout))
    game_state._base_chest_last = float(data.get("base_chest_last", game_state._base_chest_last))

    raw_languages = data.get("owned_languages", [])
    raw_upgrades = data.get("owned_upgrades", [])
    owned_languages = {}
    owned_upgrades = {}

    for item in raw_languages:
        if isinstance(item, dict) and "id" in item:
            owned_languages[item["id"]] = item
        elif isinstance(item, str):
            owned_languages[item] = {"id": item, "owned": True, "income_multiplier": 1.0}

    for item in raw_upgrades:
        if isinstance(item, dict) and "name" in item:
            owned_upgrades[item["name"]] = item
        elif isinstance(item, str):
            owned_upgrades[item] = {"name": item, "bought": True, "purchased_for": []}

    for language in player.languages:
        saved = owned_languages.get(language.id)
        if saved:
            language.owned = bool(saved.get("owned", False)) or language.cost == 0
            language.income_multiplier = float(saved.get("income_multiplier", 1.0))
        else:
            language.owned = language.cost == 0
            language.income_multiplier = 1.0

    for upgrade in player.upgrades:
        saved = owned_upgrades.get(upgrade.name)
        if saved:
            upgrade.bought = bool(saved.get("bought", False))
            upgrade.purchased_for = set(saved.get("purchased_for", []))
        else:
            upgrade.bought = False
            upgrade.purchased_for.clear()

    upsert_user(game_state, session_total=0.0)
