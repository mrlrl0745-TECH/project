import json
from pathlib import Path
SAVE = Path('savegame.json')
def save_player(player: Player) -> None:
    data = {
    'coins': player.coins,
    'office_slots': player.office_slots,
    'owned': [l.id for l in player.languages if l.owned],
    }
    SAVE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def load_player(player: Player, catalog: list[Language]) -> None:
    if not SAVE.exists():
        return
    data = json.loads(SAVE.read_text(encoding='utf-8'))
    player.coins = data.get('coins', 0)
    owned_ids = set(data.get('owned', ['scratch']))
    for lang in catalog:
        lang.owned = lang.id in owned_ids
