import customtkinter as ctk
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')
class GameApp(ctk.CTk):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.title('Симулятор программиста')
        self.geometry('900x600')
        self.coins_label = ctk.CTkLabel(self, text='0', font=('Arial', 28))
        self.coins_label.pack(pady=20)
        self.after(100, self._tick)
    def _tick(self):
        self.state.player.tick(0.1)
        self.coins_label.configure(text=f'{self.state.player.coins:,.0f}')
        self.after(100, self._tick)

btn = ctk.CTkButton(parent, text='Python — 50', command=lambda: shop.buy(...))
btn.pack(fill='x', padx=10, pady=4)

