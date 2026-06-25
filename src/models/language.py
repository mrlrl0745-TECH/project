from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Language:
    id: str
    name: str
    cost: int
    income: float
    owned: bool = False
    income_multiplier: float = 1.0
