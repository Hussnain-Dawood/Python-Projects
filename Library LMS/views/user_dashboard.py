import tkinter as tk
from tkinter import messagebox
import config
import database
from gui_helpers import styled_button, build_treeview, labeled_entry
from models import User
from datetime import datetime, date

class UserDashboard(tk.Toplevel):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.username = username
        self.user_obj = User(username, "", "")
        self.title("User Dashboard")
        self.geometry("440x420")
        self.configure(bg=config.BG_CARD)
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        tk.Frame(self, bg=config.BTN_BG, height=6).pack(fill="x")
        tk.Label(self, text="My Library", font=("Helvetica", 18, "bold"),
                 bg=config.BG_CARD, fg=config.TITLE_FG).pack(pady=(20, 4))
        tk.Label(self, text=f"Welcome back, {self.username}!",
                 font=("Helvetica", 10), bg=config.BG_CARD, fg="grey").pack(pady=(0, 20))

        inner = tk.Frame(self, bg=config.BG_CARD, padx=50)
        inner.pack()

        buttons = [
            ("View Available Books", self.view_books,     config.BTN_BG),
            ("Borrow a Book",        self.borrow_book,    config.GREEN_BTN),
            ("My Borrowings",        self.my_borrowings,  "#8E44AD"),
        ]
        for label, cmd, color in buttons:
            styled_button(inner, label, cmd, bg=color, width=30).pack(pady=6)

        styled_button(inner, "Logout", self.destroy,
                      bg="#555555", width=30).pack(pady=(20, 5))

    def view_books(self):
        win = tk.Toplevel(self)
        win.title("Available Books")
        win.geometry("760x400")
        win.configure(bg=config.BG_PANEL)
        win.grab_set()
        tk.Label(win, text="Available Books", font=config.FONT_TITLE, bg=config.BG_PANEL, fg=config.TITLE_FG).pack(pady=(10, 2))
        search_frm = tk.Frame(win, bg=config.BG_PANEL)
        search_frm.pack(fill="x", padx=10, pady=5)
        tk.Label(search_frm, text="Search:", bg=config.BG_PANEL, font=config.FONT_BODY).pack(side="left", padx=5)
        search_ent = tk.Entry(search_frm, font=config.FONT_BODY)
        search_ent.pack(side="left", fill="x", expand=True, padx=5)
        cols  = ("book_id", "book_name", "book_type", "daily_fine_rate")
        heads = ("Book ID",  "Book Name",  "Type",       "Fine / Day ($)")
        widths = (80, 260, 110, 110)
        tree = build_treeview(win, cols, heads, widths)
        def refresh_tree(query=""):
            for item in tree.get_children(): tree.delete(item)
            books = database.load_books()
            avail = books[books["status"] == "available"]
            if query:
                avail = avail[avail["book_name"].str.contains(query, case=False) |
                              avail["book_id"].str.contains(query, case=False) |
                              avail["book_type"].str.contains(query, case=False)]
            for i, (_, r) in enumerate(avail.iterrows()):
                tag = "even" if i % 2 == 0 else "odd"
                tree.insert("", "end", values=(r["book_id"], r["book_name"], r["book_type"],
                                               f"${float(r['daily_fine_rate']):.2f}"), tags=(tag,))
            status_lbl.config(text=f"{len(avail)} book(s) available")
        search_ent.bind("<KeyRelease>", lambda e: refresh_tree(search_ent.get().strip()))
        status_lbl = tk.Label(win, text="", bg=config.BG_PANEL, fg="grey", font=("Helvetica", 9))
        status_lbl.pack(pady=4)
        refresh_tree()

    def borrow_book(self):
        win = tk.Toplevel(self)
        win.title("Borrow a Book")
        win.geometry("380x340")
        win.configure(bg=config.BG_CARD)
        win.grab_set()
        tk.Frame(win, bg=config.GREEN_BTN, height=5).pack(fill="x")
        tk.Label(win, text="Borrow a Book", font=config.FONT_HEAD, bg=config.BG_CARD, fg=config.TITLE_FG).pack(pady=14)
        inner = tk.Frame(win, bg=config.BG_CARD, padx=30)
        inner.pack(fill="x")
        frm_id, eid     = labeled_entry(inner, "Book ID:")
        frm_bd, ebd     = labeled_entry(inner, "Borrow Date (YYYY-MM-DD):")
        frm_rd, erd     = labeled_entry(inner, "Return Date (YYYY-MM-DD):")
        ebd.insert(0, date.today().strftime("%Y-%m-%d"))
        for f in (frm_id, frm_bd, frm_rd): f.pack(fill="x", pady=3)
        def submit():
            ok, msg = self.user_obj.borrow_book(eid.get().strip().upper(), ebd.get().strip(), erd.get().strip())
            if ok: messagebox.showinfo("Success", msg, parent=win); win.destroy()
            else: messagebox.showerror("Error", msg, parent=win)
        styled_button(inner, "Confirm Borrow", submit, bg=config.GREEN_BTN, width=28).pack(pady=14)

    def my_borrowings(self):
        win = tk.Toplevel(self)
        win.title("My Borrowings")
        win.geometry("700x380")
        win.configure(bg=config.BG_PANEL)
        win.grab_set()
        tk.Label(win, text="My Borrowings", font=config.FONT_TITLE, bg=config.BG_PANEL, fg=config.TITLE_FG).pack(pady=10)
        cols  = ("book_id", "book_name", "borrow_date", "return_date", "fine_est")
        heads = ("Book ID",  "Book Name",  "Borrow Date",  "Return Date",  "Est. Fine ($)")
        widths = (80, 200, 120, 120, 100)
        tree = build_treeview(win, cols, heads, widths)
        borrow = database.load_borrowings()
        books  = database.load_books()
        mine   = borrow[borrow["username"] == self.username]
        for i, (_, r) in enumerate(mine.iterrows()):
            tag = "even" if i % 2 == 0 else "odd"
            book_row = books[books["book_id"] == r["book_id"]]
            bname = book_row.iloc[0]["book_name"] if not book_row.empty else "Unknown"
            rate  = float(book_row.iloc[0]["daily_fine_rate"]) if not book_row.empty else 0
            try:
                bd = datetime.strptime(str(r["borrow_date"])[:10], "%Y-%m-%d").date()
                rd = datetime.strptime(str(r["return_date"])[:10], "%Y-%m-%d").date()
                fine = f"${(rd - bd).days * rate:.2f}"
            except: fine = "N/A"
            tree.insert("", "end", values=(r["book_id"], bname, str(r["borrow_date"])[:10],
                                           str(r["return_date"])[:10], fine), tags=(tag,))
        tk.Label(win, text=f"Total: {len(mine)} borrowing(s)", bg=config.BG_PANEL, fg="grey", font=("Helvetica", 9)).pack(pady=4)
