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
config = json.load(open("config.json"))  # loads config.json
scan_queue = queue.Queue()  # Initializes the queue used for the scanning of the folder
#img_folder_path = os.path.realpath(__file__).replace(os.path.basename(__file__), config["Image_folder_name"])
#pngregex = StringManipulation().createregex(config["Name_format"])+config["Image_format"]  # Creates the regex to validate the files

#if not os.path.exists(img_folder_path):
#    print("Didn't find", config["Image_folder_name"], "creating...")
#    os.makedirs(config["Image_folder_name"])

class PopupWindow(Toplevel):  # Window class that works like a popup
    def __init__(self, keyname="", *args, **kwargs):
        print("Creating PopupWindow")
        Toplevel.__init__(self, *args, *kwargs)
        if keyname == "":
            keyname = "Window"+str(len(ObjectCollection.window_collection))
        self.grab_set()
    def stop(self):
        self.grab_release()
        self.destroy()


class VisualizationCanvas(Canvas):  # Canvas used for visualization
    def __init__(self, keyname="", *args, **kwargs):
        '''
        :param str keyname: Name in the collection
        if not specified = Visu_Canvas+lengthofcollection
        '''
        if keyname == "":
            keyname = "Visu_Canvas"+str(len(ObjectCollection.canvas_collection))
        Canvas.__init__(self, *args, **kwargs)
        ObjectCollection.canvas_collection[keyname] = self
        self.bind("<Button-1>", self.changemode)
    def changemode(self, event):
        popup = self.ModeSelectionPopup(self)
        a=popup.lb.get(ACTIVE)
        
    def ChangeImage(self): # Changes the image every slider step
        nom = NameFormat(ObjectCollection.slider_collection['Visu_Scale1'].get())
        try:
            image = ImageTk.PhotoImage(master=masterCanvas, image=Image.open(img_folder_path+nom))
            ObjectCollection.canvas_collection['Visu_Canvas1'].create_image(200, 200, image=image)
            ObjectCollection.canvas_collection['Visu_Canvas1'].image = image
        except:
            print(nom, "doesn't exist")
    def ChangeImage2(self, image):
        pass
    class ModeSelectionPopup(Toplevel):
        #Master should have a getpopupdata method with data as argument
        def __init__(self, master,*args, **kwargs):
            Toplevel.__init__(self, *args, **kwargs)
            self.title("Changement de mode")
            # WIDGETS INIT -----------------------------------------
            
            # Label1
            self.l1 = Label(self, text="Choisissez votre mode de visualisation")
            self.l1.grid(row=0, column=0)
            
            # Listbox1
            self.lb = Listbox(self, selectmode=SINGLE)
            self.lb.insert(1,"Canard")
            self.lb.grid(row=1, column=0)
            
            # Button1
            self.b = Button(self, text="Ok",command=self.destroy)
            self.b.grid(row=2,column=0)

            self.update()
            self.grab_set()
            
            # WIDGETS INIT -----------------------------------------

        


    


class VisuWindow(PopupWindow):
    

    def __init__(self, *args, **kwargs):
        print("Creating visualization window")
        Toplevel.__init__(self, *args, *kwargs)
        self.title("Visualisation")
        self.window_min_width = "400"
        self.window_min_height = "450"
        self.minsize(self.window_min_width, self.window_min_height)
        self.ownedcanvas = []
        self.initwidgets()
    

    def initmodels(self, modelgrid="2x2"):  # Initializes the visualization canvases
        print("Creating Canvas(es)")
        colors = ["blue","green","red","yellow"]
        frame = Frame(self)
        frame.grid(row=0, column=0)
        try:
            dim = re.split(r"x|X", modelgrid)  # Simple regex to process wanted modelgrid
            i = int(dim[0])
            j = int(dim[1])
            k = 0  # to name the canvas
        except Exception as e:
            print(e,modelgrid)
            print("Error, couldn't get model grid exiting window")
            self.destroy()
        for row in range(i):
            for col in range(j):
                c = VisualizationCanvas("Visu_Canvas"+str(k), master=frame,borderwidth=1, bg=colors[k] )
                c.grid(row=row, column=col)
                self.ownedcanvas.append(c)
                k+=1
        print("Created Canvas(es)")


    def initwidgets(self):
        print("Initializing widgets")
        # WIDGET INITIALIZATION------------------------------------------------------------------------
        self.initmodels()
        self.update()  # Affichage de la fenetre pour pouvoir adapter la taille du canvas
        numberofpngs = Dm.getnumberofpng(img_folder_path, pngregex)
        if numberofpngs == -1:  # Bug fix (slider starting at -1 if no image found)
            numberofpngs = 0
        self.slider = Scale(self, from_=0, to=numberofpngs-1, length=self.winfo_reqwidth(), command=self.OnSliderChange, orient=HORIZONTAL)
        ObjectCollection.slider_collection['Visu_Scale1'] = self.slider
        self.slider.grid(row=1, column=0)
        print("Widgets initialized")

        # WIDGET INITIALIZATION------------------------------------------------------------------------
    

    def OnSliderChange(self):
        
        pass


    def Visu_Window(self): 
        print("Visu_Window")
        
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
        self.after(100, AfterCallback)

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

def SliderUpdate(msg=""):  # Updates the slider 
    if msg != "":
        print(msg)
    Dm.svg_to_png(path=img_folder_path)
    numberofpngs = Dm.getnumberofpng(path=img_folder_path, reg=pngregex)
    ObjectCollection.slider_collection['Visu_Scale1'].configure(to=numberofpngs-1)
# GUI INTERACTION ---------------------------------------------------------------------------------
# MAIN --------------------------------------------------------------------------------------------

if __name__ == "__main__":
    window_min_width = "500"    #16/9
    window_min_height = "281"   #

    main_window = Tk()
    ObjectCollection.window_collection['Main'] = main_window
    main_window.minsize(width=window_min_width, height=window_min_height)

    # WIDGET INITIALIZATION------------------------------------------------------------------------

    texte = Label(main_window, text="Par BC")
    texte.grid(row=0, column=0)
    bouton = Button(main_window, text="Lancer la visualisation", command=VisuWindow)
    bouton.grid(row=1, column=0)

    # WIDGET INITIALIZATION------------------------------------------------------------------------

    
    try:
        main_window.mainloop()
    except KeyboardInterrupt:
        print("Mainloop interrupted by keyboard")
