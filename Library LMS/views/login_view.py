import tkinter as tk
from tkinter import messagebox
import config
from gui_helpers import labeled_entry, styled_button
from models import User

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.title("Login")
        self.geometry("360x320")
        self.configure(bg=config.BG_CARD)
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        tk.Frame(self, bg=config.ACCENT, height=6).pack(fill="x")

        tk.Label(self, text="Login", font=config.FONT_TITLE,
                 bg=config.BG_CARD, fg=config.TITLE_FG).pack(pady=(20, 4))
        tk.Label(self, text="Enter your credentials",
                 font=("Helvetica", 10), bg=config.BG_CARD, fg="grey").pack(pady=(0, 14))

        inner = tk.Frame(self, bg=config.BG_CARD, padx=30)
        inner.pack(fill="x")

        frm_u, self.ent_user = labeled_entry(inner, "Username:")
        frm_u.pack(fill="x", pady=4)

        frm_p, self.ent_pass = labeled_entry(inner, "Password:", show="*")
        frm_p.pack(fill="x", pady=4)

        self.ent_pass.bind("<Return>", lambda e: self._login())
        styled_button(inner, "Login", self._login, width=30).pack(pady=16)

    def _login(self):
        uname = self.ent_user.get().strip()
        pwd   = self.ent_pass.get().strip()
        role, msg = User.login(uname, pwd)
        if role is None:
            messagebox.showerror("Login Failed", msg, parent=self)
        else:
            messagebox.showinfo("Login Success", msg, parent=self)
            self.destroy()
            self.on_success(role, uname)
