import customtkinter as ctk
from src.core.config import Config
from src.data.database import init_db
from src.ui.main_window import ExpenseMateApp

if __name__ == "__main__":
    init_db()
    ctk.set_appearance_mode(Config.APPEARANCE_MODE)
    ctk.set_default_color_theme(Config.COLOR_THEME)

    app = ExpenseMateApp()
    app.mainloop()
