import pandas as pd
from datetime import datetime
import database

class User:
    """Base user class."""
    def __init__(self, username: str, password: str, email: str):
        self.username = username
        self.password = password
        self.email    = email
        self.role     = "user"

    def __repr__(self):
        return f"<User {self.username}>"

    @staticmethod
    def register(username: str, password: str, email: str):
        """Register a new regular user. Returns (True, msg) or (False, error)."""
        users = database.load_users()
        if username.strip() == "":
            return False, "Username cannot be empty."
        if username in users["username"].values:
            return False, "Username already exists."
        if "@" not in email or "." not in email:
            return False, "Please enter a valid email address."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."

        new_row = pd.DataFrame([{
            "username": username, "password": password,
            "email": email,       "role":     "user"
        }])
        users = pd.concat([users, new_row], ignore_index=True)
        database.save_users(users)
        return True, "Registration successful!"

    @staticmethod
    def login(username: str, password: str):
        """Returns (role, msg) on success, (None, error) on failure."""
        users = database.load_users()
        match = users[(users["username"] == username) & (users["password"] == password)]
        if match.empty:
            return None, "Invalid credentials."
        role = match.iloc[0]["role"]
        return role, f"Welcome {username}!"

    @staticmethod
    def search_books(query: str):
        """Search books by name, id, or type. Returns a DataFrame."""
        books = database.load_books()
        if not query:
            return books
        return books[
            books["book_name"].str.contains(query, case=False) |
            books["book_id"].str.contains(query, case=False) |
            books["book_type"].str.contains(query, case=False)
        ]

    def borrow_book(self, book_id: str, borrow_date: str, return_date: str):
        books  = database.load_books()
        borrow = database.load_borrowings()

        row = books[books["book_id"] == book_id]
        if row.empty:
            return False, "Book ID not found."
        if row.iloc[0]["status"] != "available":
            return False, "This book is currently not available."

        try:
            bd = datetime.strptime(borrow_date, "%Y-%m-%d").date()
            rd = datetime.strptime(return_date, "%Y-%m-%d").date()
            today = datetime.now().date()
        except ValueError:
            return False, "Date format must be YYYY-MM-DD."
        
        if bd < today:
            return False, "Borrow date cannot be in the past."
        if rd <= bd:
            return False, "Return date must be after borrow date."

        books.loc[books["book_id"] == book_id, "status"] = "borrowed"
        database.save_books(books)

        new_borrow = pd.DataFrame([{
            "username":    self.username,
            "book_id":     book_id,
            "borrow_date": borrow_date,
            "return_date": return_date
        }])
        borrow = pd.concat([borrow, new_borrow], ignore_index=True)
        database.save_borrowings(borrow)
        return True, f"Book '{row.iloc[0]['book_name']}' borrowed successfully!"

class AdminUser(User):
    """Inherits User; extends with admin capabilities."""
    def __init__(self, username, password, email):
        super().__init__(username, password, email)
        self.role = "admin"

    def add_book(self, book_id, book_name, book_type, daily_fine_rate):
        books = database.load_books()
        book_id = book_id.strip().upper()
        if book_id == "":
            return False, "Book ID cannot be empty."
        if book_id in books["book_id"].values:
            return False, "Book ID already exists."
        try:
            rate = float(daily_fine_rate)
            if rate < 0:
                raise ValueError
        except ValueError:
            return False, "Daily fine rate must be a positive number."

        new_book = pd.DataFrame([{
            "book_id":         book_id,
            "book_name":       book_name,
            "book_type":       book_type,
            "daily_fine_rate": rate,
            "status":          "available"
        }])
        books = pd.concat([books, new_book], ignore_index=True)
        database.save_books(books)
        return True, f"Book '{book_name}' added successfully!"

    def remove_book(self, book_id):
        books = database.load_books()
        if book_id not in books["book_id"].values:
            return False, "Book ID not found."
        row = books[books["book_id"] == book_id].iloc[0]
        if row["status"] == "borrowed":
            return False, "Cannot remove a book that is currently borrowed."
        books = books[books["book_id"] != book_id]
        database.save_books(books)
        return True, f"Book '{book_id}' removed."

    def modify_book(self, book_id, new_type, new_rate):
        books = database.load_books()
        if book_id not in books["book_id"].values:
            return False, "Book ID not found."
        try:
            rate = float(new_rate)
            if rate < 0:
                raise ValueError
        except ValueError:
            return False, "Daily fine rate must be a positive number."
        books.loc[books["book_id"] == book_id, "book_type"]       = new_type
        books.loc[books["book_id"] == book_id, "daily_fine_rate"] = rate
        database.save_books(books)
        return True, "Book updated successfully!"

    def view_all_borrowings(self):
        return database.load_borrowings()
