import os

# ─────────────────────────────────────────────
#  PATHS
# ─────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DATA_DIR      = os.path.join(BASE_DIR, "data")
USERS_FILE    = os.path.join(DATA_DIR, "users.xlsx")
BOOKS_FILE    = os.path.join(DATA_DIR, "books.xlsx")
BORROW_FILE   = os.path.join(DATA_DIR, "borrowings.xlsx")

# ─────────────────────────────────────────────
#  STYLE CONSTANTS (UI)
# ─────────────────────────────────────────────
BG_MAIN   = "#1B3A4B"   # Deep navy / teal background
BG_CARD   = "#FFFFFF"   # Card / frame white
BG_PANEL  = "#F0F4F8"   # Light panel
ACCENT    = "#E87722"   # CIM orange
BTN_FG    = "#FFFFFF"
BTN_BG    = "#2E6DA4"
BTN_HOV   = "#1A4F80"
RED_BTN   = "#C0392B"
GREEN_BTN = "#27AE60"
TITLE_FG  = "#1B3A4B"

FONT_TITLE = ("Helvetica", 16, "bold")
FONT_HEAD  = ("Helvetica", 12, "bold")
FONT_BODY  = ("Helvetica", 11)
FONT_BTN   = ("Helvetica", 11)
