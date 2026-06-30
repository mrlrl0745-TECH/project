from __future__ import annotations

import time
import tkinter as tk
from traceback import print_exception
import customtkinter as ctk

from systems.database import init_db, top_users
from systems.save import save_game, load_game


class GameApp(ctk.CTk):
    def __init__(self, game_state, player_name: str | None = None):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        init_db()
        self.game_state = game_state
        load_game(self.game_state)
        if player_name is not None:
            self.game_state.set_player_name(player_name)

        self.title(self.game_state.t("title"))
        self.geometry("1100x720")
        self.minsize(980, 640)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._keys_down = set()
        self._scene_built_for = None
        self._last_top_refresh = 0.0
        self._last_ui_refresh = 0.0
        self._ui_refresh_interval = 0.15
        self._build_layout()

        self.bind_all("<KeyPress>", self._on_key_press)
        self.bind_all("<KeyRelease>", self._on_key_release)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.after(33, self._tick)
        self.after(120, lambda: self.canvas.focus_set())
        self.after(0, self._show_window)

    def report_callback_exception(self, exc, val, tb):
        print_exception(exc, val, tb)

    def _build_layout(self):
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=18)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=14, pady=14)
        self.sidebar.grid_propagate(False)

        self.world = ctk.CTkFrame(self, corner_radius=18)
        self.world.grid(row=0, column=1, sticky="nsew", padx=(0, 14), pady=14)
        self.world.grid_rowconfigure(0, weight=1)
        self.world.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.sidebar,
            text=self.game_state.t("title"),
            font=("Segoe UI", 22, "bold"),
            justify="center",
        )
        self.title_label.pack(pady=(18, 8))

        self.name_label = ctk.CTkLabel(self.sidebar, text=self.game_state.player_name, font=("Segoe UI", 14, "bold"))
        self.name_label.pack(pady=(0, 10))

        self.language_toggle_button = ctk.CTkButton(self.sidebar, text=self.game_state.t("toggle_language"), command=self._toggle_language)
        self.language_toggle_button.pack(fill="x", padx=16, pady=(4, 8))

        self.rebirth_button = ctk.CTkButton(self.sidebar, text="", command=self._rebirth)
        self.rebirth_button.pack(fill="x", padx=16, pady=(0, 8))

        self.stats_label = ctk.CTkLabel(self.sidebar, text="", justify="left", anchor="w")
        self.stats_label.pack(fill="x", padx=16, pady=8)

        self.message_label = ctk.CTkLabel(self.sidebar, text=self.game_state.message, wraplength=250, justify="left")
        self.message_label.pack(fill="x", padx=16, pady=(4, 12))

        self.program_button = ctk.CTkButton(self.sidebar, text=self.game_state.t("program"), command=self._click_program)
        self.program_button.pack(fill="x", padx=16, pady=6)

        self.save_button = ctk.CTkButton(self.sidebar, text=self.game_state.t("save"), command=lambda: save_game(self.game_state))
        self.save_button.pack(fill="x", padx=16, pady=6)

        self.tabview = ctk.CTkTabview(self.sidebar)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=(14, 10))
        self.tabview.add("Lang")
        self.tabview.add("Upg")
        self.tabview.add("Quest")
        self.tabview.add("Stats")
        self.tabview.add("Arena")

        self.canvas_frame = ctk.CTkFrame(self.world, corner_radius=16)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#101520", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll = tk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", lambda _e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda _e: self.canvas.yview_scroll(1, "units"))
        self.canvas.focus_set()

        self._build_tabs()
        self._build_scene()
        self._update_ui(force=True)

    def _build_tabs(self):
        self.languages_frame = ctk.CTkScrollableFrame(self.tabview.tab("Lang"))
        self.languages_frame.pack(fill="both", expand=True)
        self.upgrades_frame = ctk.CTkScrollableFrame(self.tabview.tab("Upg"))
        self.upgrades_frame.pack(fill="both", expand=True)
        self.quests_frame = ctk.CTkScrollableFrame(self.tabview.tab("Quest"))
        self.quests_frame.pack(fill="both", expand=True)
        self.stats_tab = ctk.CTkScrollableFrame(self.tabview.tab("Stats"))
        self.stats_tab.pack(fill="both", expand=True)
        self.arena_tab = ctk.CTkScrollableFrame(self.tabview.tab("Arena"))
        self.arena_tab.pack(fill="both", expand=True)

        self.language_rows = []
        self.upgrade_rows = []
        self.quest_rows = []
        self.top_player_labels = []
        self.opponent_rows = []

        ctk.CTkLabel(self.languages_frame, text=self.game_state.t("languages"), font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(10, 8), padx=8)
        ctk.CTkLabel(self.languages_frame, text=self.game_state.t("language_tip"), wraplength=230, justify="left").pack(anchor="w", padx=8, pady=(0, 8))
        for language in self.game_state.languages:
            row = self._create_row(self.languages_frame)
            row["language"] = language
            self.language_rows.append(row)

        ctk.CTkLabel(self.upgrades_frame, text=self.game_state.t("upgrades"), font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(10, 8), padx=8)
        ctk.CTkLabel(self.upgrades_frame, text=self.game_state.t("price_tip"), wraplength=230, justify="left").pack(anchor="w", padx=8, pady=(0, 8))
        ctk.CTkLabel(self.upgrades_frame, text=self.game_state.t("language_upgrade_tip"), wraplength=230, justify="left").pack(anchor="w", padx=8, pady=(0, 8))
        for upgrade in self.game_state.upgrades:
            row = self._create_row(self.upgrades_frame)
            row["upgrade"] = upgrade
            self.upgrade_rows.append(row)

        ctk.CTkLabel(self.quests_frame, text=self.game_state.t("quests"), font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(10, 8), padx=8)
        for quest in self.game_state.quests:
            frame = ctk.CTkFrame(self.quests_frame)
            frame.pack(fill="x", padx=8, pady=4)
            label = ctk.CTkLabel(frame, text="", anchor="w", justify="left")
            label.pack(side="left", fill="x", expand=True, padx=8, pady=8)
            button = ctk.CTkButton(frame, text=self.game_state.t("claim"), width=90, command=lambda q=quest: self._claim_quest(q))
            button.pack(side="right", padx=8, pady=8)
            self.quest_rows.append({"quest": quest, "label": label, "button": button})

        self.stats_header = ctk.CTkLabel(self.stats_tab, text=self.game_state.t("stats"), font=("Segoe UI", 18, "bold"))
        self.stats_header.pack(anchor="w", pady=(10, 8), padx=8)
        self.stats_body = ctk.CTkLabel(self.stats_tab, text="", justify="left", anchor="w")
        self.stats_body.pack(fill="x", padx=8, pady=8)
        ctk.CTkLabel(self.stats_tab, text=self.game_state.t("top_players"), font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=8, pady=(10, 6))
        self.top_player_labels = []
        for _ in range(5):
            label = ctk.CTkLabel(self.stats_tab, text="", anchor="w")
            label.pack(fill="x", padx=8, pady=2)
            self.top_player_labels.append(label)

        ctk.CTkLabel(self.arena_tab, text=self.game_state.t("arena"), font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(10, 8), padx=8)
        ctk.CTkLabel(self.arena_tab, text=self.game_state.t("attack_tip"), wraplength=230, justify="left").pack(anchor="w", padx=8, pady=(0, 10))
        for opponent in self.game_state.online_players:
            frame = ctk.CTkFrame(self.arena_tab)
            frame.pack(fill="x", padx=8, pady=4)
            label = ctk.CTkLabel(frame, text="", anchor="w", justify="left")
            label.pack(side="left", fill="x", expand=True, padx=8, pady=8)
            button = ctk.CTkButton(frame, text=self.game_state.t("attack"), width=90, command=lambda o=opponent: self._attack(o))
            button.pack(side="right", padx=8, pady=8)
            self.opponent_rows.append({"opponent": opponent, "label": label, "button": button})

    def _create_row(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=8, pady=4)
        label = ctk.CTkLabel(frame, text="", anchor="w", justify="left")
        label.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        button = ctk.CTkButton(frame, text=self.game_state.t("buy"), width=90)
        button.pack(side="right", padx=8, pady=8)
        return {"frame": frame, "label": label, "button": button}

    def _build_scene(self):
        self.canvas.delete("all")
        self.scene_width = self.game_state.world_width
        self.scene_height = self.game_state.world_height

        if self.game_state.scene == "base":
            self._draw_base_scene()
        else:
            self._draw_world_scene()

        self.player_shadow = self.canvas.create_oval(0, 0, 0, 0, fill="#000000", outline="")
        self.player_shape = self.canvas.create_oval(0, 0, 0, 0, fill="#f59e0b", outline="#fdba74", width=3)
        self.player_label = self.canvas.create_text(0, 0, text=self.game_state.player_name, fill="white", font=("Segoe UI", 11, "bold"))
        self._scene_built_for = self.game_state.scene
        self.canvas.configure(scrollregion=(0, 0, self.scene_width, self.scene_height))
        self._center_view_on_player()
        self._draw_player()

    def _draw_world_scene(self):
        self.canvas.create_rectangle(0, 0, self.scene_width, self.scene_height, fill="#111827", outline="")
        self.canvas.create_rectangle(0, 860, self.scene_width, self.scene_height, fill="#182231", outline="")
        self.canvas.create_oval(100, 120, 280, 300, fill="#1f2937", outline="")
        self.canvas.create_oval(1480, 140, 1680, 340, fill="#0f172a", outline="")
        self.canvas.create_rectangle(1220, 520, 1460, 760, fill="#27364d", outline="#7dd3fc", width=3)
        self.canvas.create_text(1340, 480, text=self.game_state.t("base_title"), fill="#e0f2fe", font=("Segoe UI", 24, "bold"))
        self.canvas.create_rectangle(1280, 620, 1340, 710, fill="#0f172a", outline="#38bdf8", width=3)
        self.canvas.create_text(1310, 660, text="E", fill="#93c5fd", font=("Segoe UI", 26, "bold"))
        self.canvas.create_text(1340, 735, text=self.game_state.t("base_hint"), fill="#cbd5e1", font=("Segoe UI", 11))
        self.canvas.create_text(1310, 585, text=self.game_state.t("base_title"), fill="#93c5fd", font=("Segoe UI", 14, "bold"))

    def _draw_base_scene(self):
        self.canvas.create_rectangle(0, 0, self.scene_width, self.scene_height, fill="#17161f", outline="")
        self.canvas.create_rectangle(0, 820, self.scene_width, self.scene_height, fill="#221c32", outline="")
        self.canvas.create_rectangle(0, 0, self.scene_width, 100, fill="#2b2140", outline="")
        self.canvas.create_text(420, 42, text=self.game_state.t("base_interior"), fill="#f8fafc", font=("Segoe UI", 22, "bold"))

        self.canvas.create_rectangle(60, 160, 260, 450, fill="#372a52", outline="#a78bfa", width=3)
        self.canvas.create_rectangle(320, 160, 520, 450, fill="#372a52", outline="#a78bfa", width=3)
        self.canvas.create_rectangle(580, 160, 920, 450, fill="#1f2937", outline="#38bdf8", width=3)
        self.canvas.create_rectangle(1030, 160, 1360, 450, fill="#1f2937", outline="#38bdf8", width=3)
        self.canvas.create_text(420, 132, text=self.game_state.t("counter"), fill="#bfdbfe", font=("Segoe UI", 16, "bold"))
        self.canvas.create_text(1195, 132, text=self.game_state.t("base_chest"), fill="#fef3c7", font=("Segoe UI", 16, "bold"))

        self.canvas.create_rectangle(1100, 620, 1230, 760, fill="#0f172a", outline="#f59e0b", width=3)
        self.canvas.create_text(1165, 690, text=self.game_state.player_name, fill="#fde68a", font=("Segoe UI", 12, "bold"))
        self.canvas.create_text(1165, 735, text=self.game_state.t("collect"), fill="#d1d5db", font=("Segoe UI", 11))

        self.canvas.create_rectangle(150, 900, 280, 1030, fill="#0f172a", outline="#f59e0b", width=3)
        self.canvas.create_text(215, 965, text=self.game_state.t("exit"), fill="#fde68a", font=("Segoe UI", 16, "bold"))
        self.canvas.create_text(215, 1038, text=self.game_state.t("enter_exit"), fill="#d1d5db", font=("Segoe UI", 11))

        shelf_x = 80
        shelf_y = 190
        for language in self.game_state.languages:
            self.canvas.create_rectangle(shelf_x, shelf_y, shelf_x + 140, shelf_y + 70, fill="#0f172a", outline="#7dd3fc", width=2)
            self.canvas.create_text(shelf_x + 70, shelf_y + 20, text=language.name, fill="#e0f2fe", font=("Segoe UI", 12, "bold"))
            self.canvas.create_text(shelf_x + 70, shelf_y + 48, text=f"{language.income:.1f}/click", fill="#cbd5e1", font=("Segoe UI", 10))
            shelf_x += 170
            if shelf_x > 1280:
                shelf_x = 80
                shelf_y += 100

    def _draw_player(self):
        px, py = self.game_state.player.x, self.game_state.player.y
        self.canvas.coords(self.player_shadow, px - 20, py + 18, px + 20, py + 32)
        self.canvas.coords(self.player_shape, px - 20, py - 20, px + 20, py + 20)
        self.canvas.coords(self.player_label, px, py + 32)

    def _toggle_language(self):
        self.game_state.toggle_ui_language()
        self.title(self.game_state.t("title"))
        self._scene_built_for = None
        self._build_scene()
        self._update_ui(force=True)

    def _show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(400, lambda: self.attributes("-topmost", False))

    def _click_program(self):
        if self.game_state.player.click():
            self.game_state.message = self.game_state.t("program_earned", coins=self.game_state.player.income_per_click())
            self.game_state.sync_quests()
        else:
            self.game_state.message = self.game_state.t("too_fast")
        self._update_ui(force=True)

    def _rebirth(self):
        if self.game_state.rebirth():
            self._scene_built_for = None
            self._build_scene()
        self._update_ui(force=True)

    def _update_ui(self, force: bool = False):
        now = time.monotonic()
        if not force and now - self._last_ui_refresh < self._ui_refresh_interval:
            return
        self._last_ui_refresh = now

        self.title_label.configure(text=self.game_state.t("title"))
        self.language_toggle_button.configure(text=self.game_state.t("toggle_language"))
        self.program_button.configure(text=self.game_state.t("program"))
        self.save_button.configure(text=self.game_state.t("save"))
        self.message_label.configure(text=self.game_state.message)
        self.name_label.configure(text=self.game_state.player_name)

        if self.game_state.can_rebirth():
            self.rebirth_button.configure(text=f"{self.game_state.t('rebirth')} +{self.game_state.rebirths + 1}", state="normal")
        else:
            self.rebirth_button.configure(
                text=f"{self.game_state.t('rebirth')} {int(self.game_state.player.coins)}/{self.game_state.rebirth_threshold}",
                state="disabled",
            )

        self.stats_label.configure(
            text=(
                f"{self.game_state.t('coins')}: {self.game_state.player.coins:.0f}\n"
                f"{self.game_state.t('health')}: {self.game_state.player.health}/{self.game_state.player.max_health}\n"
                f"{self.game_state.t('click_power')}: {self.game_state.player.income_per_click():.0f}\n"
                f"{self.game_state.t('attack_power')}: {self.game_state.player.attack_damage()}\n"
                f"{self.game_state.t('position')}: {int(self.game_state.player.x)}, {int(self.game_state.player.y)}\n"
                f"{self.game_state.t('rebirth')}: {self.game_state.rebirths}"
            )
        )

        self.stats_body.configure(
            text=(
                f"{self.game_state.t('player')}: {self.game_state.player_name}\n"
                f"{self.game_state.t('coins')}: {self.game_state.player.coins:.0f}\n"
                f"{self.game_state.t('health')}: {self.game_state.player.health}/{self.game_state.player.max_health}\n"
                f"{self.game_state.t('click_power')}: {self.game_state.player.income_per_click():.0f}\n"
                f"{self.game_state.t('attack_power')}: {self.game_state.player.attack_damage()}\n"
                f"{self.game_state.t('languages_income')}: {self.game_state.language_income_total():.1f}\n"
                f"{self.game_state.t('attacks')}: {self.game_state.player.attacks_done}\n"
                f"{self.game_state.t('damage_done')}: {self.game_state.player.damage_done}\n"
                f"{self.game_state.t('quests_completed')}: {self.game_state.player.quests_completed}\n"
                f"{self.game_state.t('rebirth')}: {self.game_state.rebirths}"
            )
        )

        if time.time() - self._last_top_refresh > 2:
            self._last_top_refresh = time.time()
            self.game_state.refresh_top_players()
            db_top = [item for item in top_users(3) if item["name"] != self.game_state.player_name]
            combined = []
            seen_names = set()
            for item in db_top + self.game_state.top_players + [{"name": self.game_state.player_name, "coins": int(self.game_state.player.coins), "rebirths": self.game_state.rebirths}]:
                name = item["name"]
                if name in seen_names:
                    continue
                seen_names.add(name)
                combined.append(item)
            combined.sort(key=lambda item: (item.get("rebirths", 0), item["coins"]), reverse=True)
            self._cached_top = combined
        combined = getattr(self, "_cached_top", self.game_state.top_players)

        for index, label in enumerate(self.top_player_labels):
            if index < len(combined):
                item = combined[index]
                label.configure(text=f"{index + 1}. {item['name']} - {item['coins']} {self.game_state.t('coins')} / {item.get('rebirths', 0)} {self.game_state.t('rebirth')}")
            else:
                label.configure(text="")

        for row in self.language_rows:
            language = row["language"]
            row["label"].configure(text=f"{language.name} - {language.cost} {self.game_state.t('coins')} (+{language.income * language.income_multiplier:.1f}/{self.game_state.t('click')})")
            if language.owned:
                row["button"].configure(text=self.game_state.t("owned"), state="disabled")
            elif self.game_state.scene != "base":
                row["button"].configure(text=self.game_state.t("buy"), state="disabled")
            else:
                row["button"].configure(text=self.game_state.t("buy"), state="normal", command=lambda l=language: self._buy_language(l))

        for row in self.upgrade_rows:
            upgrade = row["upgrade"]
            price = self.game_state.upgrade_price(upgrade)
            if upgrade.per_language:
                row["label"].configure(
                    text=f"{upgrade.name} - {price} {self.game_state.t('coins')}\n{self.game_state.t('language_upgrade_tip')}"
                )
                self._update_language_upgrade_controls(row, upgrade)
            else:
                row["label"].configure(
                    text=f"{upgrade.name} - {price} {self.game_state.t('coins')}\n"
                    + " | ".join(
                        part
                        for part in [
                            f"+{upgrade.attack_bonus:g} {self.game_state.t('attack_power').lower()}" if upgrade.attack_bonus else "",
                            f"+{upgrade.health_bonus} HP" if upgrade.health_bonus else "",
                            f"+{upgrade.speed_bonus:.1f} speed" if upgrade.speed_bonus else "",
                            "500 coins/min" if upgrade.name == "Freelance contract" else "",
                        ]
                        if part
                    )
                )
                row["button"].configure(
                    text=self.game_state.t("owned") if upgrade.bought else self.game_state.t("buy"),
                    state="normal" if self.game_state.scene == "base" and not upgrade.bought else "disabled",
                    command=lambda u=upgrade: self._buy_upgrade(u),
                )

        for row in self.quest_rows:
            quest = row["quest"]
            row["label"].configure(text=f"{quest.title}\n{quest.description}\n{quest.progress}/{quest.target} {self.game_state.t('reward')} {quest.reward}")
            if not quest.done or quest.claimed:
                row["button"].configure(text=self.game_state.t("owned"), state="disabled")
            else:
                row["button"].configure(text=self.game_state.t("claim"), state="normal", command=lambda q=quest: self._claim_quest(q))

        for row in self.opponent_rows:
            opponent = row["opponent"]
            status = self.game_state.t("defeated") if not opponent.alive else f"HP {max(0, opponent.hp)}/{opponent.max_hp}"
            row["label"].configure(text=f"{opponent.name} | {self.game_state.t('power')} {opponent.power}\n{status}")
            if opponent.alive:
                row["button"].configure(text=self.game_state.t("attack"), state="normal", command=lambda o=opponent: self._attack(o))
            else:
                row["button"].configure(text=self.game_state.t("owned"), state="disabled")

    def _update_language_upgrade_controls(self, row, upgrade):
        owned_language_ids = tuple(language.id for language in self.game_state.languages if language.owned)
        signature = (
            self.game_state.scene,
            self.game_state.ui_language,
            owned_language_ids,
            tuple(sorted(upgrade.purchased_for)),
        )
        if row.get("control_signature") != signature:
            for child in row["frame"].winfo_children()[1:]:
                child.destroy()

            controls = []
            if self.game_state.scene == "base":
                for language in self.game_state.languages:
                    if not language.owned:
                        continue
                    button = ctk.CTkButton(
                        row["frame"],
                        text=self.game_state.t("buy_for", name=language.name),
                        width=120,
                        command=lambda u=upgrade, lang_id=language.id: self._buy_upgrade_for(u, lang_id),
                    )
                    button.pack(side="right", padx=4, pady=8)
                    controls.append((language.id, language.name, button))
            else:
                placeholder = ctk.CTkLabel(row["frame"], text=self.game_state.t("shop_only"))
                placeholder.pack(side="right", padx=4, pady=8)
                controls.append((None, None, placeholder))

            row["controls"] = controls
            row["control_signature"] = signature

        for language_id, language_name, control in row.get("controls", []):
            if language_id is None:
                control.configure(text=self.game_state.t("shop_only"))
                continue
            if language_id in upgrade.purchased_for:
                control.configure(state="disabled", text=self.game_state.t("owned"))
            else:
                control.configure(state="normal", text=self.game_state.t("buy_for", name=language_name))

    def _buy_language(self, language):
        if self.game_state.buy_language(language):
            self.game_state.message = self.game_state.t("bought_language", name=language.name)
        else:
            self.game_state.message = self.game_state.t("not_enough_language")
        self._update_ui(force=True)

    def _buy_upgrade(self, upgrade):
        if self.game_state.buy_upgrade(upgrade):
            self.game_state.message = self.game_state.t("bought_upgrade", name=upgrade.name)
        else:
            self.game_state.message = self.game_state.t("not_enough_upgrade")
        self._update_ui(force=True)

    def _buy_upgrade_for(self, upgrade, language_id):
        if self.game_state.buy_upgrade(upgrade, language_id=language_id):
            language = next((item for item in self.game_state.player.languages if item.id == language_id), None)
            if language is not None:
                self.game_state.message = self.game_state.t("bought_upgrade", name=f"{upgrade.name} ({language.name})")
        else:
            self.game_state.message = self.game_state.t("not_enough_upgrade")
        self._update_ui(force=True)

    def _claim_quest(self, quest):
        if self.game_state.claim_quest(quest):
            self.game_state.message = self.game_state.t("quest_done", name=quest.title)
        self._update_ui(force=True)

    def _attack(self, opponent):
        self.game_state.message = self.game_state.attack_opponent(opponent)
        self._update_ui(force=True)

    def _rebirth_ready_message(self):
        return self.game_state.t("rebirth_ready") if self.game_state.can_rebirth() else ""

    def _on_key_press(self, event):
        key = event.keysym.lower()
        self._keys_down.add(key)

        if key == "e":
            if self.game_state.scene == "world" and self.game_state.player_near_base():
                if self.game_state.enter_base():
                    self._scene_built_for = None
                    self._build_scene()
                    self._update_ui(force=True)
            elif self.game_state.scene == "base":
                if self.game_state.player_near_base_chest() and self.game_state.claim_base_chest():
                    self._update_ui(force=True)
                elif self.game_state.player_near_base_exit() and self.game_state.exit_base():
                    self._scene_built_for = None
                    self._build_scene()
                    self._update_ui(force=True)

    def _on_key_release(self, event):
        self._keys_down.discard(event.keysym.lower())

    def _on_canvas_resize(self, _event):
        self._center_view_on_player()

    def _on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _center_view_on_player(self):
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        target_x = max(0, min(self.scene_width - width, self.game_state.player.x - width / 2))
        target_y = max(0, min(self.scene_height - height, self.game_state.player.y - height / 2))
        self.canvas.xview_moveto(0 if self.scene_width <= width else target_x / (self.scene_width - width))
        self.canvas.yview_moveto(0 if self.scene_height <= height else target_y / (self.scene_height - height))

    def _tick(self):
        try:
            dx = dy = 0.0
            speed = self.game_state.player.speed
            if "a" in self._keys_down or "left" in self._keys_down:
                dx -= speed
            if "d" in self._keys_down or "right" in self._keys_down:
                dx += speed
            if "w" in self._keys_down or "up" in self._keys_down:
                dy -= speed
            if "s" in self._keys_down or "down" in self._keys_down:
                dy += speed

            if dx or dy:
                self.game_state.move_player(dx, dy)
                if self.game_state.scene == "world" and self.game_state.player_near_base():
                    self.game_state.message = self.game_state.t("enter_base")
                elif self.game_state.scene == "base" and self.game_state.player_near_base_exit():
                    self.game_state.message = self.game_state.t("leave_base")
                elif self.game_state.scene == "base" and self.game_state.player_near_base_chest():
                    self.game_state.message = self.game_state.t("base_chest")

            self.game_state.program_tick()

            if self._scene_built_for != self.game_state.scene:
                self._build_scene()
            else:
                self._draw_player()

            self._center_view_on_player()
            self._update_ui()
        except Exception:
            print_exc()
            self.game_state.message = "Unexpected error. See terminal."
        finally:
            self.after(33, self._tick)

    def _on_close(self):
        save_game(self.game_state)
        self.destroy()
