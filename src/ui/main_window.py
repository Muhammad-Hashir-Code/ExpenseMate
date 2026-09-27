import customtkinter as ctk
from src.ui.login_frame import LoginFrame
from src.ui.dashboard_frame import DashboardFrame


class ExpenseMateApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ExpenseMate - Personal Expense Manager")
        self.geometry("1000x700")
        self.minsize(800, 600)

        self.current_user = None
        self.show_login()

    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.login_frame = LoginFrame(self, self.on_login_success)
        self.login_frame.pack(fill="both", expand=True)

    def on_login_success(self, user):
        self.current_user = user
        self.show_dashboard()

    def show_dashboard(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.dashboard_frame = DashboardFrame(
            self, self.current_user, self.logout
        )
        self.dashboard_frame.pack(fill="both", expand=True)

    def logout(self):
        self.current_user = None
        self.show_login()
