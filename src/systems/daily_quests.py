@dataclass
class DailyQuest:
    title: str
    target: int
    progress: int = 0
    reward: int = 100
    quest_type: str = 'buy' # buy | earn | office
    def is_done(self) -> bool:
        return self.progress >= self.target
    def claim(self, player: Player) -> bool:
        if not self.is_done():
            return False
        player.coins += self.reward
        return True