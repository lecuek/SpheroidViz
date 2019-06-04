import time
from CuekUtils import *
from object_collections import ObjectCollection
import queue
import threading
from tkinter import *
from PIL import Image, ImageTk
import os
import json
import sys
import logging

Dm = DataManagement()

def windowPop():
    popup = CreateWindow()
    popup.grab_set()
    popup.protocol("WM_DELETE_WINDOW",popup.stop)
    popup.update()

config = json.load(open("config.json"))  # loads config.json
scan_queue = queue.Queue()  # Initializes the queue used for the scanning of the folder
img_folder_path = os.path.realpath(__file__).replace(os.path.basename(__file__), config["Image_folder_name"])

pngregex = StringManipulation().createregex(config["Name_format"])+config["Image_format"]  # Creates the regex to validate the files

if not os.path.exists(img_folder_path):
    print("Didn't find", config["Image_folder_name"], "creating...")
    os.makedirs(config["Image_folder_name"])
class WindowPlus(Toplevel):
    def __init__(self, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)
        self.grab_set()
    def stop(self):
        self.grab_release()
        self.destroy()

def CreateWindow():
    window_min_width = "400"
    window_min_height = "450"

    visu_window = WindowPlus()

    visu_window.minsize(window_min_width, window_min_height)
    ObjectCollection.window_collection['Visu'] = visu_window

    # WIDGET INITIALIZATION------------------------------------------------------------------------

    canvas = Canvas(visu_window, width="400", height="400")
    ObjectCollection.canvas_collection['Visu_Canvas1'] = canvas
    canvas.pack()  # Creation du Canvas
    visu_window.update()
    visu_window.update_idletasks()
    visu_window.title("Visualisation")  # Affichage de la fenetre pour pouvoir adapter la taille du canvas
    numberofpngs = Dm.getnumberofpng(img_folder_path,pngregex)
    if numberofpngs == -1:  # Bug fix (slider commençait à -1 si il n'y a pas d'image)
        numberofpngs = 0
    slider = Scale(visu_window, from_=0, to=numberofpngs-1, length=visu_window.winfo_reqwidth(), command=ChangeImage, orient=HORIZONTAL)
    ObjectCollection.slider_collection['Visu_Scale1'] = slider
    slider.pack()

    # WIDGET INITIALIZATION------------------------------------------------------------------------

    thread = threading.Thread(target=ThreadTarget)
    thread.daemon = True
    ObjectCollection.threadings['Thread_Scan1'] = thread
    thread.start()

    try:
        img = ImageTk.PhotoImage(master=canvas, image=Image.open(img_folder_path+NameFormat(0)))
        canvas.create_image(200, 200, image=img)
        canvas.image = img
    except:
        print("Did not find first picture")
    visu_window.after(100, AfterCallback)
    return visu_window

# For Threading -----------------------------------------------------------------------------------

def AfterCallback():
    try:
        value = scan_queue.get(block=False)
    except queue.Empty:
        print("Queue Empty")
        ObjectCollection.window_collection['Visu'].after(1000, AfterCallback)
        return
    if value:
        SliderUpdate()
    ObjectCollection.window_collection['Visu'].after(1000, AfterCallback)
def ThreadTarget():
    previousScan = 0
    try:
        while True:
            scan = len(os.listdir(img_folder_path))
            if scan > previousScan:
                Dm.svg_to_png(img_folder_path)
            previousScan = scan
            scan_queue.put(True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("ThreadTarget Keyboard interrupt")

# For Threading -----------------------------------------------------------------------------------

# DATA PROCESSING ---------------------------------------------------------------------------------

def NameFormat(num):  # process le format du nom dans le fichier json pour remplacer les $
    nom = str(config["Name_format"])
    compt = 0
    for i in nom:
        if i == '$':
            compt += 1
    compt -= len(str(num))
    nom = nom.strip("$")
    nbzero = ""
    for i in range(compt):
        nbzero += "0"
    nom += nbzero+str(num)+config["Image_format"]
    return nom

# DATA PROCESSING ---------------------------------------------------------------------------------
# GUI INTERACTION ---------------------------------------------------------------------------------

def ChangeImage(num):
    # Changes the image every slider step
    nom = NameFormat(ObjectCollection.slider_collection['Visu_Scale1'].get())
    try:
        image = ImageTk.PhotoImage(master=ObjectCollection.canvas_collection['Visu_Canvas1'], image=Image.open(img_folder_path+nom))
        ObjectCollection.canvas_collection['Visu_Canvas1'].create_image(200, 200, image=image)
        ObjectCollection.canvas_collection['Visu_Canvas1'].image = image
    except:
        print(nom, "doesn't exist")


def SliderUpdate(msg=""):  # Updates the slider 
    if msg != "":
        print(msg)
    Dm.svg_to_png(path=img_folder_path)
    numberofpngs = Dm.getnumberofpng(path=img_folder_path,reg=pngregex)
    ObjectCollection.slider_collection['Visu_Scale1'].configure(to=numberofpngs-1)

# GUI INTERACTION ---------------------------------------------------------------------------------
# MAIN --------------------------------------------------------------------------------------------

if __name__ == "__main__":
    window_min_width = "500"
    window_min_height = "281"

    main_window = Tk()
    ObjectCollection.window_collection['Main'] = main_window
    main_window.minsize(width=window_min_width, height=window_min_height)

    # WIDGET INITIALIZATION------------------------------------------------------------------------

    texte = Label(main_window, text="")
    texte.pack(side="top", fill="both", expand=True)
    bouton = Button(main_window, text="Lancer la visualisation", command=windowPop)
    bouton.pack(side="top", fill="both", expand=False)

    # WIDGET INITIALIZATION------------------------------------------------------------------------

    
    try:
        main_window.mainloop()
    except KeyboardInterrupt:
        print("Mainloop interrupted by keyboard")
