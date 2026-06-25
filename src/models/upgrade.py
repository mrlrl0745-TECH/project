from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Upgrade:
    name: str
    base_cost: int
    attack_bonus: float = 0.0
    health_bonus: int = 0
    speed_bonus: float = 0.0
    income_multiplier_bonus: float = 0.0
    per_language: bool = False
    bought: bool = False
    purchased_for: set[str] = field(default_factory=set)
