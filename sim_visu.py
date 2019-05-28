from tkinter import *
from main import collections
from PIL import Image, ImageTk
import os
import CuekUtils
import time
import threading


def CreateWindow():
    window_min_width = "500"
    window_min_height = "500"

    visu_window = Tk()

    canvas = Canvas(visu_window, width="400", height="400")
    canvas.pack()
    visu_window.update()
    visu_window.update_idletasks()
    visu_window.title("Visualisation")
    path = os.path.realpath(__file__).replace("sim_visu.py", "Images")
    numberofpngs = CuekUtils.DataManagement.getnumberofpng(path)
    slider = Scale(visu_window, from_=0, to=numberofpngs, length=visu_window.winfo_reqwidth(), command=ChangeImage, orient=HORIZONTAL)
    main.object_collection.append(slider)
    slider.pack()
    # img = ImageTk.PhotoImage(master=canvas, image=Image.open("canard.jpg"))
    # canvas.create_image(200, 200, tags="canard0", image=img)
    # canvas.image = img
    return visu_window


def ChangeImage(num):
    nom = "canard"+str(list(main.object_collection)[1].get())  # "canard" à changer plus tard quand le fichier config sera fait
    print(nom)


def SliderUpdate():
    path = os.path.realpath(__file__).replace("sim_visu.py", "Images")
    files = os.listdir(path)
    for file in files:
        if [i for i in [".jpg", ".jpeg", ".png"] if i in file]:
            files.remove(file)
    for i in files:
        print(i)
# pragma region OLD
"""
class RepeatEvery(threading.Thread):
    def __init__(self, interval, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self.interval = interval
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.runable = True

    def run(self):
        while self.runable:
            self.func(*self.args, **self.kwargs)
            time.sleep(self.interval)

    def stop(self):
        self.runable = False
thread = RepeatEvery(3, SliderUpdate)
thread.start()
thread.join(21)
thread.stop
"""
# pragma endregion