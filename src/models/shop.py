class Shop:
    def can_buy(self, player: Player, lang: Language) -> bool:
        owned_count = sum(1 for l in player.languages if l.owned)
        return (not lang.owned and player.coins >= lang.cost
        and owned_count < player.office_slots)
    def buy(self, player: Player, lang: Language) -> bool:
        if not self.can_buy(player, lang):
            return False
        player.coins -= lang.cost
        lang.owned = True
        return True
