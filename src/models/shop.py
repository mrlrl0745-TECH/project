from __future__ import annotations

from models.language import Language
from models.player import Player


class Shop:
    def can_buy(self, player: Player, lang: Language) -> bool:
        owned_count = sum(1 for item in player.languages if item.owned)
        office_slots = getattr(player, "office_slots", len(player.languages))
        return not lang.owned and player.coins >= lang.cost and owned_count < office_slots

    def buy(self, player: Player, lang: Language) -> bool:
        if not self.can_buy(player, lang):
            return False

        player.coins -= lang.cost
        lang.owned = True
        return True
