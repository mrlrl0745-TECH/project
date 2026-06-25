from __future__ import annotations

from dataclasses import dataclass, field
import time


@dataclass
class Player:
    coins: float = 0.0
    clicks: int = 0
    health: int = 100
    max_health: int = 100
    x: float = 180.0
    y: float = 260.0
    speed: float = 4.5
    attack_power: float = 4.0
    languages: list = field(default_factory=list)
    upgrades: list = field(default_factory=list)
    office_slots: int = 999
    click_times: list[float] = field(default_factory=list)
    quests_completed: int = 0
    attacks_done: int = 0
    games_won: int = 0
    damage_done: int = 0
    rebirths: int = 0
    rebirth_bonus: float = 1.0

    def language_income(self) -> float:
        return sum(
            language.income * language.income_multiplier
            for language in self.languages
            if language.owned
        )

    def income_per_click(self) -> float:
        return self.language_income() * self.rebirth_bonus

    def passive_income(self) -> float:
        income = self.language_income() * 0.12 * self.rebirth_bonus
        return max(0.25, income)

    def click(self) -> bool:
        now = time.time()
        self.click_times = [t for t in self.click_times if now - t < 1]

        if len(self.click_times) >= 10:
            return False

        self.click_times.append(now)
        self.clicks += 1
        self.coins += self.income_per_click()
        return True

    def bonus_attack(self) -> float:
        return sum(upgrade.attack_bonus for upgrade in self.upgrades if upgrade.bought)

    def buy_language(self, language) -> bool:
        if language.owned or self.coins < language.cost:
            return False
        self.coins -= language.cost
        language.owned = True
        return True

    def buy_upgrade(self, upgrade) -> bool:
        if upgrade.bought or self.coins < upgrade.base_cost:
            return False
        self.coins -= upgrade.base_cost
        upgrade.bought = True
        if upgrade.health_bonus:
            self.max_health += upgrade.health_bonus
            self.health = min(self.max_health, self.health + upgrade.health_bonus)
        if upgrade.speed_bonus:
            self.speed += upgrade.speed_bonus
        return True

    def spend_for_quest(self, reward: float) -> None:
        self.coins += reward
        self.quests_completed += 1

    def attack_damage(self) -> int:
        return max(2, int(self.attack_power + self.bonus_attack() + self.language_income() * 0.35))

    def reset_for_rebirth(self) -> None:
        self.coins = 0.0
        self.clicks = 0
        self.health = 100
        self.max_health = 100
        self.x = 180.0
        self.y = 260.0
        self.speed = 4.5
        self.attack_power = 4.0
        self.quests_completed = 0
        self.attacks_done = 0
        self.games_won = 0
        self.damage_done = 0
        self.click_times.clear()
