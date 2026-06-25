from __future__ import annotations

import customtkinter as ctk


class StatsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ctk.CTkLabel(self, text="Statistics are shown in the main app.").pack(padx=16, pady=16)
