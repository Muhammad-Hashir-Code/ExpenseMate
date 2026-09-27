import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.logic.services import TransactionService


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        title = ctk.CTkLabel(
            self, text="Overview", font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        # Summary Cards
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nw")

        self.lbl_balance = ctk.StringVar()
        self.lbl_income = ctk.StringVar()
        self.lbl_expense = ctk.StringVar()

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
        txs = TransactionService.get_transactions(self.user.id)

        income = sum(t.amount for t in txs if t.type == "income")
        expense = sum(t.amount for t in txs if t.type == "expense")
        bal = income - expense

        self.lbl_balance.set(f"${bal:.2f}")
        self.lbl_income.set(f"${income:.2f}")
        self.lbl_expense.set(f"${expense:.2f}")

        self._draw_chart(txs)

    def _draw_chart(self, txs):
        # Update Chart
        for w in self.chart_frame.winfo_children():
            w.destroy()

        expenses_by_cat = {}
        for t in txs:
            if t.type == "expense":
                expenses_by_cat[t.category] = (
                    expenses_by_cat.get(t.category, 0) + t.amount
                )

        if not expenses_by_cat:
            l = ctk.CTkLabel(
                self.chart_frame,
                text="No expenses to chart yet.",
                text_color="gray",
            )
            l.place(relx=0.5, rely=0.5, anchor="center")
            return

        # Draw Matplotlib Pie Chart
        fig, ax = plt.subplots(figsize=(6, 4), facecolor="#2b2b2b")
        ax.set_facecolor("#2b2b2b")

        labels = list(expenses_by_cat.keys())
        sizes = list(expenses_by_cat.values())

        # modern styling
        ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            textprops={"color": "w"},
            colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#c2c2f0"],
        )

        ax.set_title("Expenses by Category", color="white")

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
