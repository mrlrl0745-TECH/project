from __future__ import annotations

from dataclasses import dataclass
import math
import random
import time

from models.language import Language
from models.player import Player
from models.upgrade import Upgrade


@dataclass
class OnlineOpponent:
    name: str
    power: int
    hp: int
    max_hp: int
    x: float
    y: float
    alive: bool = True


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


class GameState:
    TEXT = {
        "en": {
            "title": "Programmer Simulator",
            "start_name": "Enter your username",
            "start_button": "Start",
            "program": "Program",
            "save": "Save game",
            "toggle_language": "RU / EN",
            "language_switched": "Interface language switched.",
            "languages": "Languages",
            "upgrades": "Upgrades",
            "quests": "Quests",
            "stats": "Statistics",
            "arena": "Online arena",
            "base": "Base",
            "buy": "Buy",
            "owned": "Owned",
            "claim": "Claim",
            "attack": "Attack",
            "collect": "Collect",
            "rebirth": "Rebirth",
            "rebirth_ready": "Rebirth is ready.",
            "rebirth_done": "Rebirth complete. Permanent bonus increased.",
            "price_tip": "Upgrade prices grow with language income.",
            "language_upgrade_tip": "Each buff applies to only one language.",
            "power": "Power",
            "reward": "Reward",
            "defeated": "DEFEATED",
            "click": "click",
            "shop_only": "You need to be inside the base.",
            "enter_base": "You are near the base. Press E to enter.",
            "leave_base": "Press E to leave the base.",
            "base_entered": "You entered the base.",
            "base_left": "You left the base.",
            "too_fast": "Too fast. Give your hands a second.",
            "bought_language": "Bought {name}.",
            "bought_upgrade": "Bought {name}.",
            "not_enough_language": "Not enough coins for this language.",
            "not_enough_upgrade": "Not enough coins for this upgrade.",
            "quest_done": "Quest completed: {name}.",
            "attack_hit": "You hit {name} for {damage} damage.",
            "attack_win": "You defeated {name} and earned {reward} coins.",
            "attack_dead": "{name} already defeated.",
            "base_hint": "Press E at the door",
            "base_title": "BASE",
            "base_interior": "PROGRAMMING BASE",
            "exit": "EXIT",
            "counter": "Desk",
            "player": "Player",
            "coins": "Coins",
            "health": "Health",
            "click_power": "Click power",
            "attack_power": "Attack power",
            "position": "Position",
            "top_players": "Top players",
            "language_tip": "Walk to the language shelves and collect them.",
            "enter_exit": "Press E to leave",
            "attack_tip": "Attack online players and earn coins from victories.",
            "program_earned": "+{coins:.0f} coins",
            "languages_income": "Languages income",
            "attacks": "Attacks",
            "damage_done": "Damage done",
            "quests_completed": "Quests completed",
            "freelance": "Freelance",
            "freelance_ready": "Freelance payout is ready.",
            "freelance_claimed": "Freelance paid out 500 coins.",
            "base_chest": "Nickname coins",
            "base_chest_claimed": "You collected nickname coins.",
            "buy_for": "Buy for {name}",
            "language_boost": "Language boost",
            "rebirth_bonus": "Permanent bonus",
        },
        "ru": {
            "title": "Симулятор Программиста",
            "start_name": "Введите ваше имя",
            "start_button": "Начать",
            "program": "Программировать",
            "save": "Сохранить",
            "toggle_language": "RU / EN",
            "language_switched": "Язык интерфейса изменён.",
            "languages": "Языки",
            "upgrades": "Улучшения",
            "quests": "Задания",
            "stats": "Статистика",
            "arena": "Онлайн-арена",
            "base": "База",
            "buy": "Купить",
            "owned": "Куплено",
            "claim": "Забрать",
            "attack": "Атаковать",
            "collect": "Собрать",
            "rebirth": "Ребирт",
            "rebirth_ready": "Ребирт доступен.",
            "rebirth_done": "Ребирт выполнен. Постоянный бонус увеличен.",
            "price_tip": "Цены на улучшения растут вместе с доходом от языков.",
            "language_upgrade_tip": "Каждый баф действует только на один язык.",
            "power": "Сила",
            "reward": "Награда",
            "defeated": "ПОБЕЖДЁН",
            "click": "клик",
            "shop_only": "Нужно зайти в базу.",
            "enter_base": "Ты рядом с базой. Нажми E, чтобы войти.",
            "leave_base": "Нажми E, чтобы выйти из базы.",
            "base_entered": "Ты вошёл в базу.",
            "base_left": "Ты вышел из базы.",
            "too_fast": "Слишком быстро. Дай рукам секунду.",
            "bought_language": "Куплен {name}.",
            "bought_upgrade": "Куплено: {name}.",
            "not_enough_language": "Не хватает монет на этот язык.",
            "not_enough_upgrade": "Не хватает монет на это улучшение.",
            "quest_done": "Задание выполнено: {name}.",
            "attack_hit": "Ты ударил {name} на {damage} урона.",
            "attack_win": "Ты победил {name} и получил {reward} монет.",
            "attack_dead": "{name} уже побеждён.",
            "base_hint": "Нажми E у двери",
            "base_title": "БАЗА",
            "base_interior": "БАЗА ПРОГРАММИРОВАНИЯ",
            "exit": "ВЫХОД",
            "counter": "Стол",
            "player": "Игрок",
            "coins": "Монеты",
            "health": "Здоровье",
            "click_power": "Доход за клик",
            "attack_power": "Сила атаки",
            "position": "Позиция",
            "top_players": "Топ игроков",
            "language_tip": "Подойди к полкам с языками и забирай их.",
            "enter_exit": "Нажми E, чтобы выйти",
            "attack_tip": "Нападай на онлайн-игроков и получай монеты за победы.",
            "program_earned": "+{coins:.0f} монет",
            "languages_income": "Доход языков",
            "attacks": "Атаки",
            "damage_done": "Урон",
            "quests_completed": "Задания выполнены",
            "freelance": "Фриланс",
            "freelance_ready": "Платёж за фриланс готов.",
            "freelance_claimed": "Фриланс принёс 500 монет.",
            "base_chest": "Монетки по нику",
            "base_chest_claimed": "Ты забрал монетки по нику.",
            "buy_for": "Купить для {name}",
            "language_boost": "Баф языка",
            "rebirth_bonus": "Постоянный бонус",
        },
    }

    def __init__(self):
        self.player = Player()
        self.player_name = "You"
        self.ui_language = "ru"
        self.scene = "world"
        self.world_width = 1800
        self.world_height = 1200
        self.view_width = 900
        self.view_height = 700
        self.base_x = 1280
        self.base_y = 680
        self.base_exit_x = 215
        self.base_exit_y = 965
        self.base_door_x = 1280
        self.base_door_y = 680
        self.base_radius = 70
        self.base_chest_x = 1165
        self.base_chest_y = 690
        self.base_chest_reward = 250
        self.base_chest_respawn = 90.0
        self._base_chest_last = 0.0
        self._freelance_last_payout = time.time()
        self._last_tick = time.time()
        self.rebirth_threshold = 1_000_000
        self.rebirths = 0
        self.permanent_multiplier = 1.0
        self.message = self.t("enter_base")
        self.total_earned = 0
        self.db_synced_total = 0
        self.session_attacks = 0
        self.unlocked_achievements: set[str] = set()

        self.languages = [
            Language("scratch", "Scratch", 0, 1.5, True),
            Language("python", "Python", 75, 3, False),
            Language("java", "Java", 180, 6, False),
            Language("cpp", "C++", 420, 10, False),
            Language("javascript", "JavaScript", 850, 18, False),
            Language("csharp", "C#", 1200, 25, False),
            Language("go", "Go", 1750, 35, False),
            Language("rust", "Rust", 2400, 48, False),
            Language("kotlin", "Kotlin", 3200, 65, False),
        ]
        self.player.languages = self.languages

        self.upgrades = [
            Upgrade("Power mouse", 150, attack_bonus=1),
            Upgrade("Mechanic keyboard", 260, attack_bonus=2),
            Upgrade("Armor vest", 340, health_bonus=25),
            Upgrade("Stamina sneakers", 320, speed_bonus=0.7),
            Upgrade("Heavy armor", 620, health_bonus=55),
            Upgrade("Turbo mouse", 720, attack_bonus=4),
            Upgrade("Freelance contract", 2500, income_multiplier_bonus=0.0),
            Upgrade("Python focus", 520, income_multiplier_bonus=0.5, per_language=True),
            Upgrade("Java focus", 720, income_multiplier_bonus=0.5, per_language=True),
            Upgrade("C++ focus", 960, income_multiplier_bonus=0.5, per_language=True),
        ]
        self.player.upgrades = self.upgrades

        self.quests = [
            Quest("First clicks", "Earn coins by programming", 25, 50),
            Quest("Language hunter", "Buy new programming languages", 2, 120),
            Quest("Arena fighter", "Win attacks against online players", 3, 180),
        ]
        self.online_players = self._build_online_players()
        self.top_players = [
            {"name": "Neo", "coins": 1280, "rebirths": 2},
            {"name": "Ada", "coins": 980, "rebirths": 1},
            {"name": "Linus", "coins": 760, "rebirths": 1},
            {"name": self.player_name, "coins": 0, "rebirths": 0},
        ]
        self._refresh_quests()

    def t(self, key: str, **kwargs) -> str:
        text = self.TEXT.get(self.ui_language, self.TEXT["en"]).get(key, key)
        return text.format(**kwargs)

    def toggle_ui_language(self) -> None:
        self.ui_language = "en" if self.ui_language == "ru" else "ru"
        self.message = self.t("language_switched")

    def _build_online_players(self) -> list[OnlineOpponent]:
        names = ["Vex", "Mira", "Byte", "Sora", "Rex"]
        result = []
        for idx, name in enumerate(names):
            hp = random.randint(28, 55)
            result.append(
                OnlineOpponent(
                    name=name,
                    power=random.randint(4, 12),
                    hp=hp,
                    max_hp=hp,
                    x=110 + idx * 95,
                    y=340,
                )
            )
        return result

    def set_player_name(self, name: str) -> None:
        cleaned = " ".join(name.strip().split())
        self.player_name = cleaned[:16] or "You"
        self.top_players[-1]["name"] = self.player_name

    def player_near_base(self) -> bool:
        if self.scene != "world":
            return False
        dx = self.player.x - self.base_x
        dy = self.player.y - self.base_y
        return math.hypot(dx, dy) <= self.base_radius

    def player_near_base_exit(self) -> bool:
        if self.scene != "base":
            return False
        dx = self.player.x - self.base_exit_x
        dy = self.player.y - self.base_exit_y
        return math.hypot(dx, dy) <= self.base_radius

    def player_near_base_chest(self) -> bool:
        if self.scene != "base":
            return False
        dx = self.player.x - self.base_chest_x
        dy = self.player.y - self.base_chest_y
        return math.hypot(dx, dy) <= 58

    def enter_base(self) -> bool:
        if not self.player_near_base():
            return False
        self.scene = "base"
        self.player.x = 420
        self.player.y = 560
        self.message = self.t("base_entered")
        return True

    def exit_base(self) -> bool:
        if not self.player_near_base_exit():
            return False
        self.scene = "world"
        self.player.x = self.base_door_x - 70
        self.player.y = self.base_door_y
        self.message = self.t("base_left")
        return True

    def move_player(self, dx: float, dy: float) -> None:
        if self.scene == "world":
            self.player.x = max(40, min(self.world_width - 40, self.player.x + dx))
            self.player.y = max(40, min(self.world_height - 40, self.player.y + dy))
        else:
            self.player.x = max(60, min(self.world_width - 60, self.player.x + dx))
            self.player.y = max(60, min(self.world_height - 60, self.player.y + dy))

    def language_income_total(self) -> float:
        return self.player.language_income() * self.permanent_multiplier

    def upgrade_price(self, upgrade: Upgrade) -> int:
        income = self.language_income_total()
        scale = 1.0 + min(2.0, income / 90.0)
        if upgrade.attack_bonus:
            scale += min(0.45, upgrade.attack_bonus * 0.06)
        if upgrade.health_bonus:
            scale += min(0.35, upgrade.health_bonus / 220.0)
        if upgrade.income_multiplier_bonus and upgrade.per_language:
            scale += min(0.7, upgrade.income_multiplier_bonus * 0.5)
        return max(upgrade.base_cost, int(math.ceil(upgrade.base_cost * scale)))

    def can_rebirth(self) -> bool:
        return self.player.coins >= self.rebirth_threshold

    def rebirth(self) -> bool:
        if not self.can_rebirth():
            return False

        self.rebirths += 1
        self.permanent_multiplier = 1.0 + self.rebirths * 0.25
        self.player.rebirths = self.rebirths
        self.player.rebirth_bonus = self.permanent_multiplier
        self.player.reset_for_rebirth()

        for language in self.player.languages:
            language.owned = language.cost == 0
            language.income_multiplier = 1.0
        for upgrade in self.player.upgrades:
            upgrade.bought = False
            upgrade.purchased_for.clear()

        self.scene = "world"
        self.player.x = 180
        self.player.y = 260
        self.online_players = self._build_online_players()
        self._base_chest_last = time.time()
        self._freelance_last_payout = time.time()
        self.message = self.t("rebirth_done")
        self._refresh_quests()
        return True

    def program_tick(self) -> None:
        now = time.time()
        dt = max(0.0, min(0.25, now - self._last_tick))
        self._last_tick = now
        earned = (self.player.passive_income() * dt) + self.freelance_income_tick()
        self.player.coins += earned
        self.total_earned += earned

    def freelance_income_tick(self) -> float:
        freelance = next((u for u in self.upgrades if u.name == "Freelance contract"), None)
        if freelance is None or not freelance.bought:
            return 0.0

        now = time.time()
        if now - self._freelance_last_payout < 60:
            return 0.0

        payouts = int((now - self._freelance_last_payout) // 60)
        self._freelance_last_payout += payouts * 60
        payout = 500 * payouts
        self.player.coins += payout
        self.total_earned += payout
        self.message = self.t("freelance_claimed")
        return 0.0

    def claim_base_chest(self) -> bool:
        if not self.player_near_base_chest():
            return False

        now = time.time()
        if now - self._base_chest_last < self.base_chest_respawn:
            return False

        self._base_chest_last = now
        reward = self.base_chest_reward + len(self.player_name) * 5
        self.player.coins += reward
        self.total_earned += reward
        self.message = self.t("base_chest_claimed")
        return True

    def buy_language(self, language: Language) -> bool:
        if self.scene != "base":
            return False
        purchased = self.player.buy_language(language)
        if purchased:
            self.total_earned += language.cost
            self._refresh_quests()
        return purchased

    def buy_upgrade(self, upgrade: Upgrade, language_id: str | None = None) -> bool:
        if self.scene != "base":
            return False

        if upgrade.per_language:
            if language_id is None:
                return False
            language = next((item for item in self.player.languages if item.id == language_id), None)
            if language is None or not language.owned or language_id in upgrade.purchased_for:
                return False

            price = self.upgrade_price(upgrade)
            if self.player.coins < price:
                return False

            self.player.coins -= price
            upgrade.purchased_for.add(language_id)
            language.income_multiplier += upgrade.income_multiplier_bonus
            self.total_earned += price
            self.message = self.t("bought_upgrade", name=f"{upgrade.name} ({language.name})")
            self._refresh_quests()
            return True

        price = self.upgrade_price(upgrade)
        if upgrade.bought or self.player.coins < price:
            return False

        self.player.coins -= price
        upgrade.bought = True
        if upgrade.health_bonus:
            self.player.max_health += upgrade.health_bonus
            self.player.health = min(self.player.max_health, self.player.health + upgrade.health_bonus)
        if upgrade.speed_bonus:
            self.player.speed += upgrade.speed_bonus
        self.total_earned += price
        self._refresh_quests()
        return True

    def attack_opponent(self, opponent: OnlineOpponent) -> str:
        if not opponent.alive:
            return self.t("attack_dead", name=opponent.name)

        damage = self.player.attack_damage()
        opponent.hp -= damage
        self.player.attacks_done += 1
        self.player.damage_done += damage
        self.session_attacks += 1

        if opponent.hp <= 0:
            opponent.alive = False
            reward = opponent.power * 25
            self.player.coins += reward
            self.total_earned += reward
            self.player.games_won += 1
            self._refresh_quests()
            return self.t("attack_win", name=opponent.name, reward=reward)

        counter = max(0, int(opponent.power - max(0, self.player.bonus_attack())))
        if counter:
            self.player.health = max(0, self.player.health - counter)

        self._refresh_quests()
        return self.t("attack_hit", name=opponent.name, damage=damage)

    def claim_quest(self, quest: Quest) -> bool:
        if not quest.done or quest.claimed:
            return False
        quest.claimed = True
        self.player.spend_for_quest(quest.reward)
        self.total_earned += quest.reward
        return True

    def refresh_top_players(self) -> None:
        self.top_players[-1] = {
            "name": self.player_name,
            "coins": int(self.player.coins),
            "rebirths": self.rebirths,
        }
        self.top_players.sort(key=lambda item: (item.get("rebirths", 0), item["coins"]), reverse=True)

    def _refresh_quests(self) -> None:
        self.quests[0].progress = min(self.quests[0].target, int(self.player.clicks))
        self.quests[1].progress = min(
            self.quests[1].target,
            sum(1 for language in self.player.languages if language.owned and language.cost > 0),
        )
        self.quests[2].progress = min(self.quests[2].target, self.player.games_won)

    def sync_quests(self) -> None:
        self._refresh_quests()

