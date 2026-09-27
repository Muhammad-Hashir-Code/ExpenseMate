import customtkinter as ctk
from tkinter import messagebox
from src.logic.services import AuthService


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_success_callback):
        super().__init__(master)
        self.on_success = on_success_callback

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
        if not u or not p:
            messagebox.showerror("Error", "Please fill all fields")
            return

        user = AuthService.login(u, p)
        if user:
            self.on_success(user)
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def register(self):
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()
        if not u or not p:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            user = AuthService.register(u, p)
            messagebox.showinfo(
                "Success", "Registration successful. Logging in..."
            )
            self.on_success(user)
        except ValueError:
            messagebox.showerror("Error", "Username already exists")
