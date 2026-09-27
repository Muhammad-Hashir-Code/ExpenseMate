import customtkinter as ctk 
from tkinter import messagebox
from src.logic.services import BudgetService


class BudgetView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user

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
        try:
            cat = self.category.get()
            lim = float(self.limit.get())
            pct = float(self.threshold.get()) / 100.0

            if not cat:
                messagebox.showerror("Error", "Category is required")
                return

            BudgetService.set_budget(self.user.id, cat, lim, pct)
            messagebox.showinfo(
                "Success",
                f"Budget for {cat} saved! You'll be alerted at {pct*100}% usage.",
            )
            self.category.delete(0, "end")
            self.limit.delete(0, "end")
            self.threshold.delete(0, "end")
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric format")
