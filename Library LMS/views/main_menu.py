import tkinter as tk
import config
from gui_helpers import styled_button
from views.login_view import LoginWindow
from views.register_view import RegisterWindow
from views.admin_dashboard import AdminDashboard
from views.user_dashboard import UserDashboard

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("State Library")
        self.root.geometry("420x420")
        self.root.configure(bg=config.BG_MAIN)
        self.root.resizable(False, False)
        self._build()

    def _build(self):
        banner = tk.Frame(self.root, bg=config.ACCENT, pady=14)
        banner.pack(fill="x")
        tk.Label(banner, text="State Library",
                 font=("Helvetica", 15, "bold"), bg=config.ACCENT, fg="white").pack()
        tk.Label(banner, text="Book Management System",
                 font=("Helvetica", 11), bg=config.ACCENT, fg="white").pack()

        card = tk.Frame(self.root, bg=config.BG_CARD, padx=40, pady=30)
        card.pack(expand=True)

        tk.Label(card, text="Welcome", font=("Helvetica", 18, "bold"),
                 bg=config.BG_CARD, fg=config.TITLE_FG).pack(pady=(0, 4))
        tk.Label(card, text="Please select an option to continue",
                 font=("Helvetica", 10), bg=config.BG_CARD, fg="grey").pack(pady=(0, 20))

        styled_button(card, "Login",    self.open_login).pack(pady=6)
        styled_button(card, "Register", self.open_register).pack(pady=6)
        styled_button(card, "Exit",     self.root.quit, bg=config.RED_BTN).pack(pady=6)

    def open_login(self):
        LoginWindow(self.root, self.on_login_success)

    def open_register(self):
        RegisterWindow(self.root)

    def on_login_success(self, role, username):
        if role == "admin":
            AdminDashboard(self.root, username)
        else:
            UserDashboard(self.root, username)
