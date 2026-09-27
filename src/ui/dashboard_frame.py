import customtkinter as ctk
from src.ui.views.dashboard_view import DashboardView
from src.ui.views.transaction_view import TransactionView
from src.ui.views.budget_view import BudgetView


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, user, logout_callback):
        super().__init__(master)
        self.user = user
        self.logout_callback = logout_callback

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()

        # Container for the current view
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(
            row=0, column=1, padx=10, pady=10, sticky="nsew"
        )
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        self.current_view = None
        self.show_dashboard()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            self.sidebar,
            text="ExpenseMate",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkLabel(
            self.sidebar,
            text=f"Welcome, {self.user.username}",
            font=ctk.CTkFont(size=14),
        ).grid(row=1, column=0, padx=20, pady=(0, 20))

        ctk.CTkButton(
            self.sidebar, text="Dashboard", command=self.show_dashboard
        ).grid(row=2, column=0, padx=20, pady=10)
        ctk.CTkButton(
            self.sidebar, text="Transactions", command=self.show_transactions
        ).grid(row=3, column=0, padx=20, pady=10)
        ctk.CTkButton(
            self.sidebar, text="Budgets", command=self.show_budgets
        ).grid(row=4, column=0, padx=20, pady=10)

        ctk.CTkButton(
            self.sidebar,
            text="Logout",
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
            command=self.logout_callback,
        ).grid(row=6, column=0, padx=20, pady=20, sticky="s")

    def _switch_view(self, view_class, **kwargs):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = view_class(self.main_content, self.user, **kwargs)
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def show_dashboard(self):
        self._switch_view(DashboardView)

    def show_transactions(self):
        self._switch_view(TransactionView)

    def show_budgets(self):
        self._switch_view(BudgetView)
