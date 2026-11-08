import customtkinter as ctk
from tkinter import messagebox
from src.controllers.auth_controller import AuthController


class LoginFrame(ctk.CTkFrame):
    """Refactored Login and Registration view communicating strictly via AuthController."""

    def __init__(self, master, on_success_callback, auth_controller=None):
        super().__init__(master)
        self.on_success = on_success_callback
        self.auth_controller = auth_controller or AuthController()

        # Center container
        self.container = ctk.CTkFrame(
            self, width=400, height=500, corner_radius=20
        )
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        self.title = ctk.CTkLabel(
            self.container,
            text="Welcome to ExpenseMate",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.title.pack(pady=(40, 20))

        self.username_entry = ctk.CTkEntry(
            self.container, placeholder_text="Username", width=250, height=40
        )
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(
            self.container,
            placeholder_text="Password",
            show="*",
            width=250,
            height=40,
        )
        self.password_entry.pack(pady=10)

        self.login_btn = ctk.CTkButton(
            self.container,
            text="Login",
            width=250,
            height=40,
            font=ctk.CTkFont(weight="bold"),
            command=self.login,
        )
        self.login_btn.pack(pady=(20, 10))

        self.register_btn = ctk.CTkButton(
            self.container,
            text="Register",
            width=250,
            height=40,
            fg_color="transparent",
            border_width=2,
            command=self.register,
        )
        self.register_btn.pack(pady=(0, 20))

    def login(self):
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()

        result = self.auth_controller.login(u, p)
        if result.is_success:
            self.on_success(result.data)
        else:
            messagebox.showerror("Error", result.error_message)

    def register(self):
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()

        result = self.auth_controller.register(u, p)
        if result.is_success:
            messagebox.showinfo(
                "Success", "Registration successful. Logging in..."
            )
            self.on_success(result.data)
        else:
            messagebox.showerror("Error", result.error_message)
