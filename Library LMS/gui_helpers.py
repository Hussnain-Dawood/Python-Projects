import tkinter as tk
from tkinter import ttk
import config

def styled_button(parent, text, command, bg=config.BTN_BG, fg=config.BTN_FG,
                  width=22, pady=8, font=config.FONT_BTN):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, font=font,
        activebackground=config.BTN_HOV, activeforeground=config.BTN_FG,
        relief="flat", cursor="hand2",
        width=width, pady=pady, bd=0
    )
    # Hover effect
    btn.bind("<Enter>", lambda e: btn.config(bg=config.BTN_HOV if bg == config.BTN_BG else bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn

def labeled_entry(parent, label_text, show=None):
    frm = tk.Frame(parent, bg=config.BG_CARD)
    tk.Label(frm, text=label_text, bg=config.BG_CARD, fg=config.TITLE_FG,
             font=config.FONT_BODY, anchor="w").pack(fill="x", pady=(6, 1))
    ent = tk.Entry(frm, font=config.FONT_BODY, relief="solid", bd=1,
                   show=show if show else "")
    ent.pack(fill="x", ipady=5)
    return frm, ent

def build_treeview(parent, columns, headings, col_widths):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    background=config.BG_CARD, foreground=config.TITLE_FG,
                    rowheight=26, fieldbackground=config.BG_CARD,
                    font=("Helvetica", 10))
    style.configure("Treeview.Heading",
                    background=config.BG_MAIN, foreground="white",
                    font=("Helvetica", 10, "bold"))
    style.map("Treeview", background=[("selected", config.ACCENT)])

    frm = tk.Frame(parent, bg=config.BG_PANEL)
    frm.pack(fill="both", expand=True, padx=10, pady=5)

    vsb = ttk.Scrollbar(frm, orient="vertical")
    hsb = ttk.Scrollbar(frm, orient="horizontal")
    tree = ttk.Treeview(frm, columns=columns, show="headings",
                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    vsb.pack(side="right",  fill="y")
    hsb.pack(side="bottom", fill="x")
    tree.pack(fill="both", expand=True)

    for col, head, w in zip(columns, headings, col_widths):
        tree.heading(col, text=head)
        tree.column(col, width=w, anchor="center")

    tree.tag_configure("odd",  background="#EAF2FB")
    tree.tag_configure("even", background=config.BG_CARD)
    return tree
