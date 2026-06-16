from dataclasses import dataclass
@dataclass
class Language:
    id: str
    name: str
    cost: int
    income: float
    owned: bool = False
