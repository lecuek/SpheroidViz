from tkinter import *
from object_collections import ObjectCollection
from PIL import Image, ImageTk
import os
import CuekUtils
import time
import threading

path = os.path.realpath(__file__).replace("sim_visu.py", "Images")
def CreateWindow():
    window_min_width = "400"
    window_min_height = "450"

    visu_window = Tk()
    visu_window.minsize(window_min_width, window_min_height)
    ObjectCollection.window_collection.append(visu_window)

    canvas = Canvas(visu_window, width="400", height="400")
    ObjectCollection.canvas_collection.append(canvas)
    canvas.pack()  # Création du Canvas

    visu_window.update()
    visu_window.update_idletasks()
    visu_window.title("Visualisation")  # Affichage de la fenêtre pour pouvoir adapter la taille du canvas

    path = os.path.realpath(__file__).replace("sim_visu.py", "Images")
    numberofpngs = CuekUtils.DataManagement.getnumberofpng(path)
    slider = Scale(visu_window, from_=0, to=numberofpngs-1, length=visu_window.winfo_reqwidth(), command=ChangeImage, orient=HORIZONTAL)
    ObjectCollection.slider_collection.append(slider)
    slider.pack()
    img = ImageTk.PhotoImage(master=canvas, image=Image.open(path+"/canard0.png"))
    canvas.create_image(200, 200, tags="canard0", image=img)
    canvas.image = img
    return visu_window


def ChangeImage(num):
    # Cette ligne choppe le slider depuis la collection créé le nom avec sa valeur
    # !! NE PAS OUBLIER DE TROUVER UN MOYEN !!
    # !! QUI PERMETTRAIT DE LE RETROUVER    !!
    # !! SANS L'INDEX                       !!
    nom = "canard"+str(list(ObjectCollection.slider_collection)[0].get())+".png"  # "canard" à changer plus tard quand le fichier config sera fait
    image = ImageTk.PhotoImage(master=ObjectCollection.canvas_collection[0], image=Image.open(path+"/"+nom))
    ObjectCollection.canvas_collection[0].create_image(200, 200, image=image)
    ObjectCollection.canvas_collection[0].image = image
    print(nom)


def SliderUpdate():
    path = os.path.realpath(__file__).replace("sim_visu.py", "Images")
    files = os.listdir(path)
    for file in files:
        if [i for i in [".jpg", ".jpeg", ".png"] if i in file]:
            files.remove(file)
    for i in files:
        print(i)
""" Don't touch
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