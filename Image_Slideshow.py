import tkinter as tk              # Import Tkinter for GUI
from itertools import cycle       # Import cycle to loop images infinitely
from PIL import Image, ImageTk    # Import Pillow for image handling

# Create the main application window
root = tk.Tk()
root.title("Image Slider Show")   # Set the title of the window

# List of image paths (local images)
image_path = [
    r'D:\New folder\Commerence\Shopify\Project 1\IMG-20240905-WA0010.jpg',
    r'D:\New folder\Commerence\Shopify\Project 1\IMG-20240905-WA0011.jpg',
    r'D:\New folder\Commerence\Shopify\Project 1\IMG-20240905-WA0013.jpg'
]

# Resize dimensions for all images (width, height)
image_size = (500, 500)

# Open each image, resize it, and store in a list
images = [Image.open(path).resize(image_size) for path in image_path]

# Convert each PIL image into a Tkinter-compatible image (PhotoImage)
photo_images = [ImageTk.PhotoImage(image) for image in images]

# Create an infinite cycle object to loop through the images
slideshow = cycle(photo_images)

# Label widget to display the current image
label = tk.Label(root)
label.pack()

# Function to update the image on the label
def update_image():
    img = next(slideshow)          # Get the next image from cycle
    label.config(image=img)        # Set the image on the label
    # Call update_image() again after 3000 milliseconds (3 seconds)
    root.after(3000, update_image) 

# Function to start the slideshow
def start_slideshow():
    update_image()                 # Begin showing images

# Button to start slideshow when clicked
play_button = tk.Button(root, text='Play SlideShow', command=start_slideshow)
play_button.pack()

# Start the Tkinter event loop (keeps window running)
root.mainloop()
