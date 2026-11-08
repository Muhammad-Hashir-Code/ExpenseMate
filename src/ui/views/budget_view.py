import customtkinter as ctk
from tkinter import messagebox
from src.controllers.budget_controller import BudgetController


class BudgetView(ctk.CTkFrame):
    """Refactored Budget Manager view communicating strictly via BudgetController."""

    def __init__(self, master, user, budget_controller=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.budget_controller = budget_controller or BudgetController()

        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self,
            text="Budget Manager",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        form_frame = ctk.CTkFrame(self, corner_radius=10, width=400)
        form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nw")

        ctk.CTkLabel(
            form_frame,
            text="Set Category Budget",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=15)

        self.category = ctk.CTkEntry(
            form_frame, placeholder_text="Category (e.g. Food)", width=250
        )
        self.category.pack(pady=10, padx=20)

        self.limit = ctk.CTkEntry(
            form_frame,
            placeholder_text="Monthly Limit (e.g. 500.00)",
            width=250,
        )
        self.limit.pack(pady=10, padx=20)

        self.threshold = ctk.CTkEntry(
            form_frame,
            placeholder_text="Alert Threshold % (e.g. 80)",
            width=250,
        )
        self.threshold.pack(pady=10, padx=20)

        ctk.CTkButton(
            form_frame, text="Save Budget", command=self.save_budget, width=250
        ).pack(pady=20, padx=20)

    def save_budget(self):
        cat = self.category.get()
        lim = self.limit.get()
        pct = self.threshold.get()

        result = self.budget_controller.set_budget(
            user_id=self.user.id,
            category=cat,
            limit_input=lim,
            threshold_pct_input=pct,
        )

        if result.is_success:
            b = result.data
            messagebox.showinfo(
                "Success",
                f"Budget for '{b.category}' saved! You'll be alerted at {b.alert_threshold * 100:.0f}% usage.",
            )
            self.category.delete(0, "end")
            self.limit.delete(0, "end")
            self.threshold.delete(0, "end")
        else:
            messagebox.showerror("Validation Error", result.error_message)
