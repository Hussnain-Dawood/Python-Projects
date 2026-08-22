import os
from datetime import datetime, date
import database
from models import User, AdminUser

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    print("\n" + "="*40)
    print(f"{title.center(40)}")
    print("="*40)

def guest_menu():
    while True:
        print_header("Western Library - CLI Mode")
        print("1. Login")
        print("2. Register")
        print("0. Quit")
        choice = input("\nSelect an option: ")

        if choice == "1":
            login_screen()
        elif choice == "2":
            register_screen()
        elif choice == "0":
            break
        else:
            print("Invalid option. Press Enter to continue.")
            input()

def login_screen():
    print_header("Login")
    username = input("Username: ")
    password = input("Password: ")
    role, msg = User.login(username, password)
    if role:
        print(f"\nSuccess: {msg}")
        input("Press Enter to enter dashboard...")
        if role == "admin":
            admin_menu(username)
        else:
            user_menu(username)
    else:
        print(f"\nError: {msg}")
        input("Press Enter to try again.")

def register_screen():
    print_header("Register New User")
    username = input("Username: ")
    email = input("Email: ")
    password = input("Password: ")
    ok, msg = User.register(username, password, email)
    if ok:
        print(f"\nSuccess: {msg}")
    else:
        print(f"\nError: {msg}")
    input("Press Enter to continue.")

def admin_menu(username):
    admin = AdminUser(username, "", "")
    while True:
        print_header(f"Admin Dashboard ({username})")
        print("1. Add New Book")
        print("2. Remove Book")
        print("3. Modify Book")
        print("4. View All Books")
        print("5. View All Borrowings")
        print("6. View Analytics")
        print("7. View All Users")
        print("0. Logout")
        choice = input("\nSelect an option: ")

        if choice == "1":
            bid = input("Book ID: ")
            name = input("Book Name: ")
            btype = input("Type (Fiction/Non-Fiction): ")
            rate = input("Daily Fine Rate ($): ")
            ok, msg = admin.add_book(bid, name, btype, rate)
            print(f"\n{msg}"); input()
        elif choice == "2":
            bid = input("Enter Book ID to remove: ")
            ok, msg = admin.remove_book(bid.upper())
            print(f"\n{msg}"); input()
        elif choice == "3":
            bid = input("Enter Book ID to modify: ")
            btype = input("New Type (Fiction/Non-Fiction): ")
            rate = input("New Daily Fine Rate ($): ")
            ok, msg = admin.modify_book(bid.upper(), btype, rate)
            print(f"\n{msg}"); input()
        elif choice == "4":
            books = database.load_books()
            print("\n" + books.to_string(index=False))
            input("\nPress Enter to return.")
        elif choice == "5":
            borrow = database.load_borrowings()
            print("\n" + borrow.to_string(index=False))
            input("\nPress Enter to return.")
        elif choice == "6":
            view_analytics()
        elif choice == "7":
            users = database.load_users()
            print("\n" + users.to_string(index=False))
            input("\nPress Enter to return.")
        elif choice == "0":
            break

def user_menu(username):
    user_obj = User(username, "", "")
    while True:
        print_header(f"User Dashboard ({username})")
        print("1. View/Search Available Books")
        print("2. Borrow a Book")
        print("3. My Borrowings")
        print("0. Logout")
        choice = input("\nSelect an option: ")

        if choice == "1":
            q = input("Enter search query (leave blank to see all): ")
            books = User.search_books(q)
            avail = books[books["status"] == "available"]
            print("\n" + avail.to_string(index=False))
            input("\nPress Enter to return.")
        elif choice == "2":
            bid = input("Book ID: ")
            bd = input("Borrow Date (YYYY-MM-DD) [Default Today]: ")
            if not bd: bd = date.today().strftime("%Y-%m-%d")
            rd = input("Return Date (YYYY-MM-DD): ")
            ok, msg = user_obj.borrow_book(bid.upper(), bd, rd)
            print(f"\n{msg}"); input()
        elif choice == "3":
            borrow = database.load_borrowings()
            mine = borrow[borrow["username"] == username]
            print("\n" + mine.to_string(index=False))
            input("\nPress Enter to return.")
        elif choice == "0":
            break

def view_analytics():
    print_header("Library Analytics")
    books = database.load_books()
    users = database.load_users()
    borrow = database.load_borrowings()
    
    print(f"Total Users: {len(users)}")
    print(f"Total Books: {len(books)}")
    print(f"Borrowed:    {len(books[books['status']=='borrowed'])}")
    print(f"Available:   {len(books[books['status']=='available'])}")
    
    if not borrow.empty:
        print("\nTop 3 Borrowed Books:")
        top = borrow['book_id'].value_counts().head(3)
        print(top.to_string())
    
    input("\nPress Enter to return.")

if __name__ == "__main__":
    database.ensure_data_files()
    guest_menu()
