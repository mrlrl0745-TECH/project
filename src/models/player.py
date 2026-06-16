class Player:
    def __init__(self):
        self.coins: float = 0.0
        self.languages: list[Language] = []
        self.office_slots: int = 3

    def income_per_sec(self) -> float:
        return sum(l.income for l in self.languages if l.owned)
    
    def tick(self, dt: float) -> None:
        self.coins += self.income_per_sec() * dt
