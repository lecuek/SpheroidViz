from tkinter import *
from PIL import Image, ImageTk
import os

def popup():
    window_min_width = "500"
    window_min_height = "500"

    visu_window = Tk()
    canvas = Canvas(visu_window, width="400", height="400")
    canvas.pack()

    visu_window.title("Visualisation")
<<<<<<< HEAD
    # test
=======
    # test 
>>>>>>> master
    img = ImageTk.PhotoImage(master=canvas, image=Image.open("canard.jpg"))
    canvas.create_image(200, 200, tags="canard0", image=img)
    canvas.image = img
    return visu_window