from tkinter import *
from PIL import Image
import os
window_min_width = "500"
window_min_height = "500"

visu_window = Tk()

visu_window.title("Visualisation")
#test
img = PhotoImage(Image.open("canard.jpg"))
panel = Label(visu_window, image=img)
panel.pack(side="bottom", fill="both", expand="yes")
visu_window.mainloop()

