import tkinter as tk
import database
import sys
from views.main_menu import MainWindow
import cli

def main():
    # Initialize the data files on startup
    database.ensure_data_files()
    
    print("="*40)
    print("State Library")
    print("="*40)
    print("1. Launch GUI (Graphical Interface)")
    print("2. Launch CLI (Command Line Interface)")
    choice = input("\nSelect Mode (1/2): ").strip()

    if choice == "2":
        cli.guest_menu()
    else:
        # Initialize the root window
        root = tk.Tk()
        # Start the Main Menu view
        app = MainWindow(root)
        # Run the application
        root.mainloop()

if __name__ == "__main__":
    main()
