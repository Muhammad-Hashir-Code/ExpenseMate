import customtkinter as ctk
from src.ui.main_window import ExpenseMateApp

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = ExpenseMateApp()
    app.mainloop()
