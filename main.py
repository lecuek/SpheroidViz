import time
from CuekUtils import *
from object_collections import ObjectCollection
import queue
import threading
from tkinter import *
from object_collections import ObjectCollection
from PIL import Image, ImageTk
import os
import json
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import sys
import logging


class KillableThread(threading.Thread):
    def stop(self):
        self._stop


def windowPop():
    popup = CreateWindow()
    popup.update()

config = json.load(open("config.json"))
scan_queue = queue.Queue()
img_folder_path = os.path.realpath(__file__).replace(os.path.basename(__file__), config["Image_folder_name"])


def CreateWindow():
    window_min_width = "400"
    window_min_height = "450"

    visu_window = Tk()
    visu_window.minsize(window_min_width, window_min_height)
    ObjectCollection.window_collection.append(visu_window)

    # WIDGET INITIALIZATION-----------------------------------------------

    canvas = Canvas(visu_window, width="400", height="400")
    ObjectCollection.canvas_collection.append(canvas)
    canvas.pack()  # Creation du Canvas
    visu_window.update()
    visu_window.update_idletasks()
    visu_window.title("Visualisation")  # Affichage de la fenetre pour pouvoir adapter la taille du canvas
    numberofpngs = DataManagement.getnumberofpng(img_folder_path)
    if numberofpngs == -1:  # Bug fix (slider commençait à -1 si il n'y a pas d'image)
        numberofpngs = 0
    slider = Scale(visu_window, from_=0, to=numberofpngs-1, length=visu_window.winfo_reqwidth(), command=ChangeImage, orient=HORIZONTAL)
    ObjectCollection.slider_collection.append(slider)
    slider.pack()
    button = Button(visu_window, text="Rafraichir", command=SliderUpdate)
    ObjectCollection.button_collection.append(button)
    button.pack()

    # WIDGET INITIALIZATION-----------------------------------------------

    thread = threading.Thread(target=ThreadTarget)
    ObjectCollection.threadings.append(thread)
    thread.start()

    try:
        img = ImageTk.PhotoImage(master=canvas, image=Image.open(img_folder_path+NameFormat(0)))
        canvas.create_image(200, 200, image=img)
        canvas.image = img
    except:
        print("Did not find first picture")
    visu_window.after(100, AfterCallback)    
    return visu_window


def AfterCallback():
    try:
        value = scan_queue.get(block=False)
    except queue.Empty:
        ObjectCollection.window_collection[1].after(1000, AfterCallback)
    if value:
        SliderUpdate("After")
    ObjectCollection.window_collection[1].after(1000, AfterCallback)


def ThreadTarget():
    previousScan = 0
    try:
        while True:
            scan = len(os.listdir(img_folder_path))
            if scan > previousScan:
                DataManagement.svg_to_png(img_folder_path)
            previousScan = scan
            scan_queue.put(True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("INTERRUPTION PAR LE CLAVIER LOL")


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


def DirectoryObserver():
    # Code pique directement de la documentation de Watchdog
    # https://pythonhosted.org/watchdog/quickstart.html#a-simple-example
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = Event()
    observer = Observer()
    observer.schedule(event_handler, img_folder_path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def ChangeImage(num):
    # Changes the image every slider step
    # !! DON'T FORGET TO CHANGE THE WAY I REFER TO OBJECTS ASAP !!
    nom = NameFormat(ObjectCollection.slider_collection[0].get())
    try:
        image = ImageTk.PhotoImage(master=ObjectCollection.canvas_collection[0], image=Image.open(img_folder_path+nom))
        ObjectCollection.canvas_collection[0].create_image(200, 200, image=image)
        ObjectCollection.canvas_collection[0].image = image
    except:
        print(nom, "doesn't exist")


def SliderUpdate(msg=""):  # Updates the slider 
    if msg != "":
        print(msg)
    DataManagement.svg_to_png(img_folder_path)
    numberofpngs = DataManagement.getnumberofpng(img_folder_path)
    ObjectCollection.slider_collection[0].configure(to=numberofpngs-1)


def on_closing():
    for thread in ObjectCollection.threadings


if __name__ == "__main__":
    window_min_width = "500"
    window_min_height = "281"

    main_window = Tk()
    ObjectCollection.window_collection.append(main_window)
    main_window.minsize(width=window_min_width, height=window_min_height)

    # WIDGET INITIALIZATION-----------------------------------------------

    texte = Label(main_window, text="")
    texte.pack(side="top", fill="both", expand=True)
    bouton = Button(main_window, text="Lancer la visualisation", command=windowPop)
    bouton.pack(side="top", fill="both", expand=False)

    # WIDGET INITIALIZATION-----------------------------------------------

    ObjectCollection.threadings.append(threading.main_thread())
    threading.main_thread()
    # main_window.protocol("WM_DELETE_WINDOW",) """ POUR CLEAN QUAND LA FENETRE FERME A TERMINER """
    try:
        main_window.mainloop()
    except KeyboardInterrupt:
        print("Mainloop interrupted by keyboard")
        for thread in ObjectCollection.threadings:
            thread
            thread._stop()
            ObjectCollection.threadings.remove(thread)
            continue
        exit()
