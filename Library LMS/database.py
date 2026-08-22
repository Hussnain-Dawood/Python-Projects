import pandas as pd
import os
import config

def ensure_data_files():
    """Create data directory and empty Excel files if they don't exist."""
    os.makedirs(config.DATA_DIR, exist_ok=True)

    if not os.path.exists(config.USERS_FILE):
        df = pd.DataFrame(columns=["username", "password", "email", "role"])
        admin_row = pd.DataFrame([{
            "username": "admin", "password": "admin123",
            "email": "admin@westernlibrary.com", "role": "admin"
        }])
        df = pd.concat([df, admin_row], ignore_index=True)
        df.to_excel(config.USERS_FILE, index=False)

    if not os.path.exists(config.BOOKS_FILE):
        pd.DataFrame(columns=["book_id", "book_name", "book_type",
                               "daily_fine_rate", "status"]).to_excel(config.BOOKS_FILE, index=False)

    if not os.path.exists(config.BORROW_FILE):
        pd.DataFrame(columns=["username", "book_id",
                               "borrow_date", "return_date"]).to_excel(config.BORROW_FILE, index=False)

def load_users():
    return pd.read_excel(config.USERS_FILE, dtype=str)

def save_users(df):
    df.to_excel(config.USERS_FILE, index=False)

def load_books():
    df = pd.read_excel(config.BOOKS_FILE, dtype=str)
    df["daily_fine_rate"] = pd.to_numeric(df["daily_fine_rate"], errors="coerce")
    return df

def save_books(df):
    df.to_excel(config.BOOKS_FILE, index=False)

def load_borrowings():
    return pd.read_excel(config.BORROW_FILE, dtype=str)

def save_borrowings(df):
    df.to_excel(config.BORROW_FILE, index=False)
