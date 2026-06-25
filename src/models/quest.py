from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Quest:
    title: str
    description: str
    target: int
    reward: int
    progress: int = 0
    claimed: bool = False

    @property
    def done(self) -> bool:
        return self.progress >= self.target
