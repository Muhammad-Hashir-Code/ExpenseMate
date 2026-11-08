import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.controllers.transaction_controller import TransactionController


class DashboardView(ctk.CTkFrame):
    """Refactored Overview view consuming aggregated metrics from TransactionController."""

    def __init__(self, master, user, tx_controller=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.tx_controller = tx_controller or TransactionController()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        title = ctk.CTkLabel(
            self, text="Overview", font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        # Summary Cards
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nw")

        self.lbl_balance = ctk.StringVar(value="$0.00")
        self.lbl_income = ctk.StringVar(value="$0.00")
        self.lbl_expense = ctk.StringVar(value="$0.00")

        self._create_card(
            self.cards_frame, "Total Balance", self.lbl_balance, 0
        )
        self._create_card(self.cards_frame, "Total Income", self.lbl_income, 1)
        self._create_card(
            self.cards_frame, "Total Expense", self.lbl_expense, 2
        )

        # Chart frame
        self.chart_frame = ctk.CTkFrame(self, corner_radius=10)
        self.chart_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

        self.refresh_data()

    def _create_card(self, parent, title, string_var, col):
        card = ctk.CTkFrame(parent, width=220, height=100, corner_radius=10)
        card.grid(row=0, column=col, padx=10, pady=10)
        card.grid_propagate(False)

        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14))
        lbl_title.pack(pady=(15, 5))

        lbl_amt = ctk.CTkLabel(
            card,
            textvariable=string_var,
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        lbl_amt.pack()

    def refresh_data(self):
        # Fetch financial summary from controller
        summary_res = self.tx_controller.get_dashboard_summary(self.user.id)
        if summary_res.is_success:
            summary = summary_res.data
            self.lbl_balance.set(f"${summary['balance']:.2f}")
            self.lbl_income.set(f"${summary['income']:.2f}")
            self.lbl_expense.set(f"${summary['expense']:.2f}")

        # Fetch category chart data from controller
        chart_res = self.tx_controller.get_category_chart_data(self.user.id)
        expenses_by_cat = chart_res.data if chart_res.is_success else {}
        self._draw_chart(expenses_by_cat)

    def _draw_chart(self, expenses_by_cat):
        for w in self.chart_frame.winfo_children():
            w.destroy()

        if not expenses_by_cat:
            label = ctk.CTkLabel(
                self.chart_frame,
                text="No expenses to chart yet.",
                text_color="gray",
            )
            label.place(relx=0.5, rely=0.5, anchor="center")
            return

        fig, ax = plt.subplots(figsize=(6, 4), facecolor="#2b2b2b")
        ax.set_facecolor("#2b2b2b")

        labels = list(expenses_by_cat.keys())
        sizes = list(expenses_by_cat.values())

        ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            textprops={"color": "w"},
            colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#c2c2f0", "#ffb3e6"],
        )
        ax.set_title("Expenses by Category", color="white")

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
