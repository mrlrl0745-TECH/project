class BoosterManager:
    def __init__(self):
        self.multiplier: float = 1.0
        self.expires_at: float = 0.0
    def activate(self, mult: float, duration: float) -> None:
        import time
        self.multiplier = mult
        self.expires_at = time.time() + duration
    def current_mult(self) -> float:
        import time
        if time.time() > self.expires_at:
            self.multiplier = 1.0
        return self.multiplier