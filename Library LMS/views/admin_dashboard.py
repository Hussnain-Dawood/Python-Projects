import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import config
import database
from gui_helpers import styled_button, labeled_entry, build_treeview
from models import AdminUser
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AdminDashboard(tk.Toplevel):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.username = username
        self.title("Admin Dashboard")
        self.geometry("440x500")
        self.configure(bg=config.BG_CARD)
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        tk.Frame(self, bg=config.ACCENT, height=6).pack(fill="x")
        tk.Label(self, text="Admin Dashboard", font=("Helvetica", 18, "bold"),
                 bg=config.BG_CARD, fg=config.TITLE_FG).pack(pady=(20, 4))
        tk.Label(self, text=f"Logged in as  {self.username}",
                 font=("Helvetica", 10), bg=config.BG_CARD, fg="grey").pack(pady=(0, 20))

        inner = tk.Frame(self, bg=config.BG_CARD, padx=50)
        inner.pack()

        buttons = [
            ("Add Book",          self.add_book,        config.BTN_BG),
            ("Remove Book",       self.remove_book,     config.RED_BTN),
            ("Modify Book",        self.modify_book,     "#8E44AD"),
            ("View All Books",     self.view_all_books,  config.BTN_BG),
            ("View All Borrowings",self.view_borrowings, config.BTN_BG),
            ("View All Users",     self.view_users,      "#16A085"),
            ("View Analytics",     self.view_analytics,  config.ACCENT),
        ]
        for label, cmd, color in buttons:
            styled_button(inner, label, cmd, bg=color, width=30).pack(pady=5)

        styled_button(inner, "Logout", self.destroy,
                      bg="#555555", width=30).pack(pady=(15, 5))

    def add_book(self):
        win = tk.Toplevel(self)
        win.title("Add Book")
        win.geometry("380x360")
        win.configure(bg=config.BG_CARD)
        win.grab_set()
        tk.Frame(win, bg=config.GREEN_BTN, height=5).pack(fill="x")
        tk.Label(win, text="Add New Book", font=config.FONT_HEAD,
                 bg=config.BG_CARD, fg=config.TITLE_FG).pack(pady=14)
        inner = tk.Frame(win, bg=config.BG_CARD, padx=30)
        inner.pack(fill="x")
        frm_id,   eid   = labeled_entry(inner, "Book ID (e.g. B020):")
        frm_name, ename = labeled_entry(inner, "Book Name:")
        for f in (frm_id, frm_name): f.pack(fill="x", pady=3)
        tk.Label(inner, text="Book Type:", bg=config.BG_CARD, fg=config.TITLE_FG,
                 font=config.FONT_BODY, anchor="w").pack(fill="x", pady=(6, 1))
        type_var = tk.StringVar(value="Fiction")
        ttk.Combobox(inner, textvariable=type_var, values=["Fiction", "Non-Fiction"],
                     state="readonly", font=config.FONT_BODY).pack(fill="x", ipady=4)
        frm_rate, erate = labeled_entry(inner, "Daily Fine Rate ($):")
        frm_rate.pack(fill="x", pady=3)
        def submit():
            admin = AdminUser(self.username, "", "")
            ok, msg = admin.add_book(eid.get().strip(), ename.get().strip(),
                                    type_var.get(), erate.get().strip())
            if ok: messagebox.showinfo("Success", msg, parent=win); win.destroy()
            else: messagebox.showerror("Error", msg, parent=win)
        styled_button(inner, "Add Book", submit, bg=config.GREEN_BTN, width=28).pack(pady=14)

    def remove_book(self):
        book_id = simpledialog.askstring("Remove Book", "Enter Book ID to remove:", parent=self)
        if not book_id: return
        admin = AdminUser(self.username, "", "")
        ok, msg = admin.remove_book(book_id.strip().upper())
        if ok: messagebox.showinfo("Removed", msg, parent=self)
        else: messagebox.showerror("Error", msg, parent=self)

    def modify_book(self):
        book_id = simpledialog.askstring("Modify Book", "Enter Book ID to modify:", parent=self)
        if not book_id: return
        books = database.load_books()
        row = books[books["book_id"] == book_id.strip().upper()]
        if row.empty: messagebox.showerror("Error", "Book ID not found.", parent=self); return
        win = tk.Toplevel(self)
        win.title("Modify Book")
        win.geometry("380x280")
        win.configure(bg=config.BG_CARD)
        win.grab_set()
        tk.Frame(win, bg="#8E44AD", height=5).pack(fill="x")
        tk.Label(win, text=f"Modify: {row.iloc[0]['book_name']}",
                 font=config.FONT_HEAD, bg=config.BG_CARD, fg=config.TITLE_FG, wraplength=340).pack(pady=14)
        inner = tk.Frame(win, bg=config.BG_CARD, padx=30)
        inner.pack(fill="x")
        tk.Label(inner, text="Book Type:", bg=config.BG_CARD, fg=config.TITLE_FG,
                 font=config.FONT_BODY, anchor="w").pack(fill="x", pady=(0, 1))
        type_var = tk.StringVar(value=row.iloc[0]["book_type"])
        ttk.Combobox(inner, textvariable=type_var, values=["Fiction", "Non-Fiction"],
                     state="readonly", font=config.FONT_BODY).pack(fill="x", ipady=4)
        frm_rate, erate = labeled_entry(inner, "New Daily Fine Rate ($):")
        erate.insert(0, str(row.iloc[0]["daily_fine_rate"]))
        frm_rate.pack(fill="x", pady=8)
        def submit():
            admin = AdminUser(self.username, "", "")
            ok, msg = admin.modify_book(book_id.strip().upper(), type_var.get(), erate.get().strip())
            if ok: messagebox.showinfo("Updated", msg, parent=win); win.destroy()
            else: messagebox.showerror("Error", msg, parent=win)
        styled_button(inner, "Save Changes", submit, bg="#8E44AD", width=28).pack(pady=10)

    def view_all_books(self):
        win = tk.Toplevel(self)
        win.title("All Books")
        win.geometry("820x440")
        win.configure(bg=config.BG_PANEL)
        win.grab_set()
        tk.Label(win, text="All Books", font=config.FONT_TITLE, bg=config.BG_PANEL, fg=config.TITLE_FG).pack(pady=(10, 2))
        search_frm = tk.Frame(win, bg=config.BG_PANEL)
        search_frm.pack(fill="x", padx=10, pady=5)
        tk.Label(search_frm, text="Search:", bg=config.BG_PANEL, font=config.FONT_BODY).pack(side="left", padx=5)
        search_ent = tk.Entry(search_frm, font=config.FONT_BODY)
        search_ent.pack(side="left", fill="x", expand=True, padx=5)
        cols  = ("book_id", "book_name", "book_type", "daily_fine_rate", "status")
        heads = ("Book ID",  "Book Name",  "Type",       "Fine / Day ($)",  "Status")
        widths = (80, 220, 100, 110, 90)
        tree = build_treeview(win, cols, heads, widths)
        def refresh_tree(query=""):
            for item in tree.get_children(): tree.delete(item)
            books = database.load_books()
            if query:
                books = books[books["book_name"].str.contains(query, case=False) |
                              books["book_id"].str.contains(query, case=False) |
                              books["book_type"].str.contains(query, case=False)]
            for i, (_, r) in enumerate(books.iterrows()):
                tag = "even" if i % 2 == 0 else "odd"
                tree.insert("", "end", values=(r["book_id"], r["book_name"], r["book_type"],
                                               f"${float(r['daily_fine_rate']):.2f}", r["status"]), tags=(tag,))
            status_lbl.config(text=f"Showing {len(books)} books")
        search_ent.bind("<KeyRelease>", lambda e: refresh_tree(search_ent.get().strip()))
        status_lbl = tk.Label(win, text="", bg=config.BG_PANEL, fg="grey", font=("Helvetica", 9))
        status_lbl.pack(pady=4)
        refresh_tree()

    def view_borrowings(self):
        win = tk.Toplevel(self)
        win.title("All Borrowings")
        win.geometry("700x420")
        win.configure(bg=config.BG_PANEL)
        win.grab_set()
        tk.Label(win, text="All Borrowings", font=config.FONT_TITLE, bg=config.BG_PANEL, fg=config.TITLE_FG).pack(pady=10)
        cols  = ("username", "book_id", "borrow_date", "return_date")
        heads = ("Username",  "Book ID",  "Borrow Date",  "Return Date")
        widths = (150, 100, 150, 150)
        tree = build_treeview(win, cols, heads, widths)
        borrow = database.load_borrowings()
        for i, (_, r) in enumerate(borrow.iterrows()):
            tag = "even" if i % 2 == 0 else "odd"
            tree.insert("", "end", values=(r["username"], r["book_id"], r["borrow_date"], r["return_date"]), tags=(tag,))
        tk.Label(win, text=f"Total: {len(borrow)} borrowing records", bg=config.BG_PANEL, fg="grey", font=("Helvetica", 9)).pack(pady=4)

    def view_users(self):
        win = tk.Toplevel(self)
        win.title("All Users")
        win.geometry("600x380")
        win.configure(bg=config.BG_PANEL)
        win.grab_set()
        tk.Label(win, text="All Users", font=config.FONT_TITLE, bg=config.BG_PANEL, fg=config.TITLE_FG).pack(pady=10)
        cols  = ("username", "email", "role")
        heads = ("Username",  "Email",  "Role")
        widths = (150, 300, 100)
        tree = build_treeview(win, cols, heads, widths)
        users = database.load_users()
        for i, (_, r) in enumerate(users.iterrows()):
            tag = "even" if i % 2 == 0 else "odd"
            tree.insert("", "end", values=(r["username"], r["email"], r["role"]), tags=(tag,))

    def view_analytics(self):
        win = tk.Toplevel(self)
        win.title("Library Analytics")
        win.geometry("500x550")
        win.configure(bg=config.BG_PANEL)
        win.grab_set()
        tk.Label(win, text="Library Analytics", font=config.FONT_TITLE, bg=config.BG_PANEL, fg=config.TITLE_FG).pack(pady=15)
        users = database.load_users()
        books = database.load_books()
        borrow = database.load_borrowings()
        total_users = len(users)
        total_books = len(books)
        borrowed_count = len(books[books["status"] == "borrowed"])
        available_count = total_books - borrowed_count
        total_fines = 0
        for _, r in borrow.iterrows():
            book_row = books[books["book_id"] == r["book_id"]]
            if not book_row.empty:
                rate = float(book_row.iloc[0]["daily_fine_rate"])
                try:
                    bd = datetime.strptime(str(r["borrow_date"])[:10], "%Y-%m-%d").date()
                    rd = datetime.strptime(str(r["return_date"])[:10], "%Y-%m-%d").date()
                    total_fines += (rd - bd).days * rate
                except: pass
        card = tk.Frame(win, bg=config.BG_CARD, padx=15, pady=15, relief="solid", bd=1)
        card.pack(pady=10, padx=20, fill="x")
        stats = [("Total Registered Users", total_users), ("Total Books in Library", total_books),
                 ("Books Currently Borrowed", borrowed_count), ("Books Available", available_count),
                 ("Estimated Total Fee Revenue", f"${total_fines:.2f}")]
        for lbl, val in stats:
            f = tk.Frame(card, bg=config.BG_CARD)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=lbl, bg=config.BG_CARD, font=config.FONT_BODY).pack(side="left")
            tk.Label(f, text=str(val), bg=config.BG_CARD, font=config.FONT_HEAD, fg=config.ACCENT).pack(side="right")
        
        if borrow.empty:
            tk.Label(win, text="No borrowing data available.", bg=config.BG_PANEL, font=config.FONT_BODY).pack()
        
        def show_chart():
            chart_win = tk.Toplevel(win)
            chart_win.title("Book Type Distribution")
            chart_win.geometry("400x400")
            
            # Data for pie chart
            type_counts = books["book_type"].value_counts()
            
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', startangle=140, colors=['#3498DB', '#E67E22'])
            ax.set_title("Library Book Types Distribution")
            
            canvas = FigureCanvasTkAgg(fig, master=chart_win)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        styled_button(win, "Show Distribution Chart", show_chart, bg="#2980B9", width=25).pack(pady=5)
        styled_button(win, "Close", win.destroy, bg="#555555", width=15).pack(pady=10)
