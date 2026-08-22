import tkinter as tk
from tkinter import messagebox
import config
from gui_helpers import labeled_entry, styled_button
from models import User

class RegisterWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Register")
        self.geometry("380x400")
        self.configure(bg=config.BG_CARD)
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        tk.Frame(self, bg=config.GREEN_BTN, height=6).pack(fill="x")
        tk.Label(self, text="Register", font=config.FONT_TITLE,
                 bg=config.BG_CARD, fg=config.TITLE_FG).pack(pady=(20, 4))
        tk.Label(self, text="Create a new account",
                 font=("Helvetica", 10), bg=config.BG_CARD, fg="grey").pack(pady=(0, 10))

        inner = tk.Frame(self, bg=config.BG_CARD, padx=30)
        inner.pack(fill="x")

        frm_u, self.ent_user  = labeled_entry(inner, "Username:")
        frm_u.pack(fill="x", pady=3)
        frm_e, self.ent_email = labeled_entry(inner, "Email:")
        frm_e.pack(fill="x", pady=3)
        frm_p, self.ent_pass  = labeled_entry(inner, "Password:", show="*")
        frm_p.pack(fill="x", pady=3)
        frm_c, self.ent_conf  = labeled_entry(inner, "Confirm Password:", show="*")
        frm_c.pack(fill="x", pady=3)

        styled_button(inner, "Register", self.on_register_click,
                      bg=config.GREEN_BTN, width=30).pack(pady=16)

    def on_register_click(self):
        u  = self.ent_user.get().strip()
        e  = self.ent_email.get().strip()
        p  = self.ent_pass.get().strip()
        cp = self.ent_conf.get().strip()
        if p != cp:
            messagebox.showerror("Error", "Passwords do not match.", parent=self)
            return
        ok, msg = User.register(u, p, e)
        if ok:
            messagebox.showinfo("Success", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Registration Failed", msg, parent=self)
