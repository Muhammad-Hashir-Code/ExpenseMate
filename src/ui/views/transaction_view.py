import customtkinter as ctk
from tkinter import messagebox, filedialog
import datetime
from src.logic.services import TransactionService


class TransactionView(ctk.CTkFrame):
    def __init__(self, master, user, on_refresh=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.on_refresh = on_refresh
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self, text="Transactions", font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(
            row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nw"
        )

        self._build_form()
        self._build_list()
        self.refresh_list()

    def _build_form(self):
        form_frame = ctk.CTkFrame(self, width=300, corner_radius=10)
        form_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nw")

        ctk.CTkLabel(
            form_frame,
            text="Add New Transaction",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=15)

        self.type_var = ctk.StringVar(value="expense")
        ctk.CTkSegmentedButton(
            form_frame, values=["expense", "income"], variable=self.type_var
        ).pack(pady=10, padx=20, fill="x")

        self.amount = ctk.CTkEntry(
            form_frame, placeholder_text="Amount (e.g. 50.00)"
        )
        self.amount.pack(pady=10, padx=20, fill="x")

        self.date = ctk.CTkEntry(
            form_frame, placeholder_text="Date (YYYY-MM-DD)"
        )
        self.date.insert(0, datetime.date.today().isoformat())
        self.date.pack(pady=10, padx=20, fill="x")

        self.category = ctk.CTkEntry(
            form_frame, placeholder_text="Category (e.g. Food)"
        )
        self.category.pack(pady=10, padx=20, fill="x")

        self.currency_var = ctk.StringVar(value="USD")
        self.currency = ctk.CTkComboBox(
            form_frame,
            values=["USD", "EUR", "GBP", "PKR", "INR"],
            variable=self.currency_var,
        )
        self.currency.pack(pady=10, padx=20, fill="x")

        self.desc = ctk.CTkEntry(form_frame, placeholder_text="Description")
        self.desc.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(
            form_frame, text="Add Transaction", command=self.add_tx
        ).pack(pady=20, padx=20, fill="x")

        # CSV Buttons
        csv_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        csv_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(
            csv_frame, text="Import CSV", width=120, command=self.import_csv
        ).pack(side="left", padx=(0, 5))
        ctk.CTkButton(
            csv_frame, text="Export CSV", width=120, command=self.export_csv
        ).pack(side="right", padx=(5, 0))

    def _build_list(self):
        self.list_frame = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.list_frame.grid(
            row=1, column=1, padx=(0, 20), pady=0, sticky="nsew"
        )

    def add_tx(self):
        try:
            amt = float(self.amount.get())
            dt = self.date.get()
            cat = self.category.get()
            desc = self.desc.get()
            t_type = self.type_var.get()
            curr = self.currency_var.get()

            if not cat:
                messagebox.showerror("Error", "Category is required")
                return

            _, alert = TransactionService.add_transaction(
                self.user.id, t_type, amt, dt, cat, desc, curr
            )
            if alert:
                messagebox.showwarning("Budget Alert!", alert)

            self.refresh_list()
            if self.on_refresh:
                self.on_refresh()
            self.amount.delete(0, "end")
            self.category.delete(0, "end")
            self.desc.delete(0, "end")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount format")

    def refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        txs = TransactionService.get_transactions(self.user.id)
        for t in txs:
            color = "#E74C3C" if t.type == "expense" else "#2ECC71"
            sign = "-" if t.type == "expense" else "+"

            item = ctk.CTkFrame(self.list_frame, height=50, corner_radius=5)
            item.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(
                item,
                text=f"{t.date} | {t.category}",
                font=ctk.CTkFont(weight="bold"),
            ).pack(side="left", padx=15)
            ctk.CTkLabel(item, text=t.description, text_color="gray").pack(
                side="left", padx=15
            )
            ctk.CTkLabel(
                item,
                text=f"{sign}{t.amount:.2f} {t.currency}",
                text_color=color,
                font=ctk.CTkFont(weight="bold"),
            ).pack(side="right", padx=15)

    def import_csv(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if filepath:
            from src.logic.services import CSVService

            count = CSVService.import_transactions(self.user.id, filepath)
            messagebox.showinfo("Success", f"Imported {count} transactions!")
            self.refresh_list()
            if self.on_refresh:
                self.on_refresh()

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV Files", "*.csv")]
        )
        if filepath:
            from src.logic.services import CSVService

            CSVService.export_transactions(self.user.id, filepath)
            messagebox.showinfo(
                "Success", "Transactions exported successfully!"
            )
