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


def windowPop():
    popup = CreateWindow()
    popup.update()

callback_queue = queue.Queue()
config = json.load(open("config.json"))

img_folder_path = os.path.realpath(__file__).replace(os.path.basename(__file__),config["Image_folder_name"])


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

    numberofpngs = DataManagement.getnumberofpng(img_folder_path)
    if numberofpngs == -1: numberofpngs = 0
    slider = Scale(visu_window, from_=0, to=numberofpngs-1, length=visu_window.winfo_reqwidth(), command=ChangeImage, orient=HORIZONTAL)
    ObjectCollection.slider_collection.append(slider)
    slider.pack()
    button = Button(visu_window,text="Rafraichir",command=SliderUpdate)
    ObjectCollection.button_collection.append(button)
    button.pack()
    try:
        img = ImageTk.PhotoImage(master=canvas, image=Image.open(img_folder_path+NameFormat(0)))
        canvas.create_image(200, 200, image=img)
        canvas.image = img
    except:
        print("Did not find first picture")
    return visu_window


def NameFormat(num):
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
    # Code piqué directement de la documentation de Watchdog
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
    # Fait le changement de l'image à chaque déplacements du slider
    # !! NE PAS OUBLIER DE TROUVER UN MOYEN !!
    # !! QUI PERMETTRAIT DE LE RETROUVER    !!
    # !! SANS L'INDEX                       !!
    # ANCIENNE LIGNE nom = config["Name_format"]+str(list(ObjectCollection.slider_collection)[0].get())+".png"  # "canard" à changer plus tard quand le fichier config sera fait
    nom = NameFormat(ObjectCollection.slider_collection[0].get())
    try:
        image = ImageTk.PhotoImage(master=ObjectCollection.canvas_collection[0], image=Image.open(img_folder_path+nom))
        ObjectCollection.canvas_collection[0].create_image(200, 200, image=image)
        ObjectCollection.canvas_collection[0].image = image
    except:
        print(nom,"doesn't exist")


def SliderUpdate():
    print("Updating slider from SliderUpdate")
    DataManagement.svg_to_png(img_folder_path)
    numberofpngs = DataManagement.getnumberofpng(img_folder_path)
    slider = Scale(
        ObjectCollection.window_collection[1],
        from_=0, to=numberofpngs-1,
        length=ObjectCollection.window_collection[1].winfo_reqwidth(),
        command=ChangeImage,
        orient=HORIZONTAL
    )
    value = ObjectCollection.slider_collection[0].get()
    ObjectCollection.slider_collection[0].destroy()
    ObjectCollection.slider_collection.remove(ObjectCollection.slider_collection[0])
    ObjectCollection.slider_collection.append(slider)
    slider.pack()
    ObjectCollection.window_collection[1].update()

if __name__ == "__main__":
    window_min_width = "500"
    window_min_height = "281"

    main_window = Tk()
    ObjectCollection.window_collection.append(main_window)
    main_window.minsize(width=window_min_width, height=window_min_height)

    texte = Label(main_window, text="")
    texte.pack(side="top",fill="both",expand=True)
    bouton = Button(main_window, text="Lancer la visualisation", command=windowPop)
    bouton.pack(side="top",fill="both",expand=False)
    ObjectCollection.threadings.append(threading.main_thread())
    threading.main_thread()
    main_window.mainloop()
    """path = os.path.realpath(__file__).replace("sim_visu.py", "Images")
    files = os.listdir(path)
    for file in files:
        if [i for i in [".jpg", ".jpeg", ".png"] if i in file]:
            files.remove(file)
    for i in files:
        print(i)"""
