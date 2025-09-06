import tkinter as tk                     # Import tkinter module for GUI
from tkinter import filedialog, messagebox  # Import file dialogs (open/save) and message boxes

# Function to create a new file
def new_file():
    text.delete(1.0, tk.END)             # Delete all text from position 1.0 (start) to END (last)

# Function to open an existing file
def open_file():
    filepath = filedialog.askopenfilename(  # Open file dialog to select a file
        defaultextension=".txt",            # Default extension is .txt
        filetypes=[("Text Files", "*.txt")] # Only show .txt files
    )
    if filepath:                            # If user selected a file
        with open(filepath, "r") as file:   # Open the file in read mode
            text.delete(1.0, tk.END)        # Clear current text area
            text.insert(tk.END, file.read())# Insert file content into text area

# Function to save the current file
def save_file():
    filepath = filedialog.asksaveasfilename( # Open save dialog box
        defaultextension=".txt",             # Default extension is .txt
        filetypes=[("Text Files", "*.txt")]  # Save only as .txt files
    )
    if filepath:                             # If user chose a location
        with open(filepath, "w") as file:    # Open file in write mode
            file.write(text.get(1.0, "end-1c")) # Write text (exclude last extra newline)
            messagebox.showinfo("Info", "File saved successfully!")  # Show success message

# Main application window
root = tk.Tk()                              # Create main window
root.title("Simple Text Editor")            # Set window title
root.geometry("800x600")                    # Set window size (width=800, height=600)

# Menu bar
menu = tk.Menu(root)                        # Create menu bar
root.config(menu=menu)                      # Attach menu bar to main window

# File menu
file_menu = tk.Menu(menu, tearoff=False)    # Create "File" menu, disable tear-off option
menu.add_cascade(label="File", menu=file_menu) # Add File menu to menu bar
file_menu.add_command(label="New", command=new_file)   # Add "New" option
file_menu.add_command(label="Open", command=open_file) # Add "Open" option
file_menu.add_command(label="Save", command=save_file) # Add "Save" option
file_menu.add_separator()                   # Add a separator line
file_menu.add_command(label="Exit", command=root.quit) # Add "Exit" option to close app

# Text area for editing
text = tk.Text(root,                       # Create text widget
               wrap=tk.WORD,               # Wrap text by words (not by characters)
               font=("Helvetica", 12),     # Set font style and size
               fg="blue")                  # Set text color to blue
text.pack(expand=tk.YES, fill=tk.BOTH)     # Expand text area to fit window, both directions

# Start the GUI loop
root.mainloop()                            # Run the application until user exits
