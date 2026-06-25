from __future__ import annotations

import customtkinter as ctk


class ShopFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ctk.CTkLabel(self, text="Shop view is handled in the main app.").pack(padx=16, pady=16)
