import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog
from src.core.config import Config
from src.controllers.transaction_controller import TransactionController


class TransactionView(ctk.CTkFrame):
    """Refactored Transaction view communicating strictly via TransactionController."""

    def __init__(self, master, user, on_refresh=None, tx_controller=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.on_refresh = on_refresh
        self.tx_controller = tx_controller or TransactionController()

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
        form_frame = ctk.CTkFrame(self, width=320, corner_radius=10)
        form_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nw")

        ctk.CTkLabel(
            form_frame,
            text="Add New Transaction",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=15)

        self.type_var = ctk.StringVar(value="expense")
        ctk.CTkSegmentedButton(
            form_frame, values=["expense", "income"], variable=self.type_var
        ).pack(pady=8, padx=20, fill="x")

        self.amount = ctk.CTkEntry(
            form_frame, placeholder_text="Amount (e.g. 50.00)"
        )
        self.amount.pack(pady=8, padx=20, fill="x")

        self.date = ctk.CTkEntry(
            form_frame, placeholder_text="Date (YYYY-MM-DD)"
        )
        self.date.insert(0, datetime.date.today().isoformat())
        self.date.pack(pady=8, padx=20, fill="x")

        self.category = ctk.CTkEntry(
            form_frame, placeholder_text="Category (e.g. Food)"
        )
        self.category.pack(pady=8, padx=20, fill="x")

        # Currency Dropdown
        self.currency_var = ctk.StringVar(value=Config.DEFAULT_CURRENCY)
        self.currency = ctk.CTkComboBox(
            form_frame,
            values=Config.SUPPORTED_CURRENCIES,
            variable=self.currency_var,
        )
        self.currency.pack(pady=8, padx=20, fill="x")

        # Payment Method Dropdown (from Migration Part A)
        self.payment_var = ctk.StringVar(value=Config.DEFAULT_PAYMENT_METHOD)
        self.payment_method = ctk.CTkComboBox(
            form_frame,
            values=Config.SUPPORTED_PAYMENT_METHODS,
            variable=self.payment_var,
        )
        self.payment_method.pack(pady=8, padx=20, fill="x")

        self.desc = ctk.CTkEntry(form_frame, placeholder_text="Description / Notes")
        self.desc.pack(pady=8, padx=20, fill="x")

        ctk.CTkButton(
            form_frame, text="Add Transaction", command=self.add_tx
        ).pack(pady=15, padx=20, fill="x")

        # CSV Actions
        csv_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        csv_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(
            csv_frame, text="Import CSV", width=125, command=self.import_csv
        ).pack(side="left", padx=(0, 5))
        ctk.CTkButton(
            csv_frame, text="Export CSV", width=125, command=self.export_csv
        ).pack(side="right", padx=(5, 0))

    def _build_list(self):
        self.list_frame = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.list_frame.grid(
            row=1, column=1, padx=(0, 20), pady=0, sticky="nsew"
        )

    def add_tx(self):
        result = self.tx_controller.create_transaction(
            user_id=self.user.id,
            t_type=self.type_var.get(),
            amount_input=self.amount.get(),
            date_input=self.date.get(),
            category=self.category.get(),
            description=self.desc.get(),
            currency=self.currency_var.get(),
            payment_method=self.payment_var.get(),
        )

        if not result.is_success:
            messagebox.showerror("Validation Error", result.error_message)
            return

        tx, alert = result.data
        if alert:
            messagebox.showwarning("Budget Alert!", alert)

        self.refresh_list()
        if self.on_refresh:
            self.on_refresh()

        self.amount.delete(0, "end")
        self.category.delete(0, "end")
        self.desc.delete(0, "end")

    def refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        result = self.tx_controller.get_transactions(self.user.id)
        if not result.is_success:
            messagebox.showerror("Error", result.error_message)
            return

        txs = result.data
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

            pay_method = getattr(t, "payment_method", "Cash")
            desc_text = f"{t.description} ({pay_method})" if t.description else f"({pay_method})"
            ctk.CTkLabel(item, text=desc_text, text_color="gray").pack(
                side="left", padx=10
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
            res = self.tx_controller.import_csv(self.user.id, filepath)
            if res.is_success:
                import_res = res.data
                msg = f"Imported {import_res.imported_count} of {import_res.total_rows} transactions."
                if import_res.skipped_count > 0:
                    msg += f"\nSkipped {import_res.skipped_count} invalid rows."
                messagebox.showinfo("Import Complete", msg)
                self.refresh_list()
                if self.on_refresh:
                    self.on_refresh()
            else:
                messagebox.showerror("Import Error", res.error_message)

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV Files", "*.csv")]
        )
        if filepath:
            res = self.tx_controller.export_csv(self.user.id, filepath)
            if res.is_success:
                messagebox.showinfo(
                    "Success", f"Exported {res.data} transactions successfully!"
                )
            else:
                messagebox.showerror("Export Error", res.error_message)
