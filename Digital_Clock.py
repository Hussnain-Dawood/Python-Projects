import tkinter as tk # for graphical interface 
from time import strftime

# Create main window
root = tk.Tk()
root.title("Digital Clock")

# Function to update time
def time():
    string = strftime('%I:%M:%S %p\n%A, %B %d, %Y')  # 12-hour format, date, and day name
    label.config(text=string)
    label.after(1000, time)  # Update every 1 second

# Label styling
label = tk.Label(
    root,
    font=("calibri", 40),
    background="darkblue",
    foreground="white",
    padx=20,
    pady=20
)
label.pack(anchor="center")

time()  # Start the clock

root.mainloop()
