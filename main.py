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

class PopupWindow(Toplevel):  # Window class that works like a popup
    def __init__(self, keyname="", *args, **kwargs):
        print("Creating PopupWindow")
        Toplevel.__init__(self, *args, *kwargs)
        if keyname == "":
            keyname = "Window"+str(len(ObjectCollection.windows))
        ObjectCollection.windows[keyname] = self
        self.grab_set()
    def stop(self):
        self.grab_release()
        self.destroy()


class VisualizationCanvas(Canvas):  # Canvas used for visualization
    def __init__(self, keyname="", size="", *args, **kwargs):
        '''
        :param str keyname: Name in the collection
        :param str size: Size of the canvas ex:("200x200")
        if not specified = Visu_Canvas+lengthofcollection
        '''
        if size != "":
            try:
                dim = re.split(r"x|X", size)  # Simple regex to process wanted modelgrid
                i = int(dim[0])
                j = int(dim[1])
            except Exception as e:
                print("Couldn't process the given size for canvas",e)

        Canvas.__init__(self, *args, **kwargs)
        if keyname == "":
            keyname = "Visu_Canvas"+str(len(ObjectCollection.canvases))
        ObjectCollection.canvases[keyname] = self
        self.bind("<Button-1>", self.changemode)


    def changemode(self, event):
        result = ModeSelectionPopup(self).getchoice()
        if result != "":
            self.configure(background=ObjectCollection.visualization_modes[result].color)
            # Change visualization mode
        else:
            print("Canceled")    



class VisualisationMode():
    def __init__(self, key, value):
        
        self.name = value["Name"]
        self.image_folder_name = value["Image_folder_name"]
        self.name_format = value["Name_format"]
        self.image_format = value["Image_format"]
        self.color = value["color"]
        ObjectCollection.visualization_modes[self.name] = self

    def __str__(self):
        return self.name


    def ChangeImage(self): # Changes the image every slider step
        nom = NameFormat(ObjectCollection.sliders['Visu_Scale1'].get())
        try:
            image = ImageTk.PhotoImage(master=masterCanvas, image=Image.open(img_folder_path+nom))
            ObjectCollection.canvases['Visu_Canvas1'].create_image(200, 200, image=image)
            ObjectCollection.canvases['Visu_Canvas1'].image = image
        except:
            print(nom, "doesn't exist")
    def ChangeImage2(self, image):
        pass


class ModeSelectionPopup(object):
    def __init__(self, parent):
        self.toplevel = Toplevel(parent)
        self.toplevel.title("Changement de mode")
        self.selection = ""
        # WIDGETS INIT -----------------------------------------
        
        # Label1
        self.l1 = Label(self.toplevel, text="Choisissez votre mode de visualisation")
        self.l1.grid(row=0, column=0)
        
        # Listbox1
        self.lb = Listbox(self.toplevel, selectmode=SINGLE)
        numberofvis = ObjectCollection.visualization_modes
        print("Numberof vis------------", numberofvis)

        # Sorts the selection
        self.vislist = []
        for i,vismod in numberofvis.items():
            self.vislist.append([len(self.vislist),str(vismod)])
            #self.lb.insert(i,key)
        self.vislist.sort(reverse=True)
         
        # Inserts in listbox
        for i in self.vislist:
            self.lb.insert(i[0],i[1])
        self.lb.bind("<<ListboxSelect>>", self.onlistboxchange)
        self.lb.grid(row=1, column=0)

        # Button1
        self.b = Button(self.toplevel, text="Ok",command=self.toplevel.destroy)
        self.b.grid(row=2,column=0)
        self.toplevel.update_idletasks()
        self.toplevel.grab_set()
        # WIDGETS INIT -----------------------------------------


    def onlistboxchange(self, event):  # When the user selects an option
        w = event.widget
        index = int(w.curselection()[0])
        self.selection = w.get(index)
        print(self.selection)


    def getchoice(self):  # Returns the selected option
        self.toplevel.wait_window()
        return self.selection

class VisuWindow(PopupWindow):
    

    def __init__(self, *args, **kwargs):
        print("Creating visualization window")
        Toplevel.__init__(self, *args, *kwargs)
        self.canvaslist = []
        self.title("Visualisation")
        self.window_min_width = "400"
        self.window_min_height = "450"
        self.minsize(self.window_min_width, self.window_min_height)
        self.ownedcanvas = []
        self.initwidgets()
    

    def initmodels(self, modelgrid="1x3"):  # Initializes the visualization canvases
        print("Creating Canvas(es)")
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
        ObjectCollection.sliders['Visu_Scale1'] = self.slider
        self.slider.grid(row=1, column=0)
        print("Widgets initialized")

        # WIDGET INITIALIZATION------------------------------------------------------------------------
    

    def OnSliderChange(self,num):
        for canvas in self.canvaslist:
            pass
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
        ObjectCollection.windows['Visu'].after(1000, AfterCallback)
        return
    if value:
        SliderUpdate()
    ObjectCollection.windows['Visu'].after(1000, AfterCallback)
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
    nom = str(config["base"]["Name_format"])
    compt = 0
    for i in nom:
        if i == '$':
            compt += 1
    compt -= len(str(num))
    nom = nom.strip("$")
    nbzero = ""
    for i in range(compt):
        nbzero += "0"
    nom += nbzero+str(num)+config["base"]["Image_format"]
    return nom
# DATA PROCESSING ---------------------------------------------------------------------------------
# GUI INTERACTION ---------------------------------------------------------------------------------
def SliderUpdate(msg=""):  # Updates the slider 
    if msg != "":
        print(msg)
    Dm.svg_to_png(path=img_folder_path)
    numberofpngs = Dm.getnumberofpng(path=img_folder_path, reg=pngregex)
    ObjectCollection.sliders['Visu_Scale1'].configure(to=numberofpngs-1)
# GUI INTERACTION ---------------------------------------------------------------------------------
# MAIN --------------------------------------------------------------------------------------------

def CreateVisuModels():
    #Creation of Visualization mode objects
    i = 0
    for key,value in config["Visualizations"].items():
        print("key---------------",key)
        VisualisationMode(key,value)
        i += 1
        
    print("created",i,"visualization models ")

colors = ["blue","green","red","yellow"]
Dm = DataManagement()
config = json.load(open("config.json"))  # loads config.json
scan_queue = queue.Queue()  # Initializes the queue used for the scanning of the folder
img_folder_path = os.path.realpath(__file__).replace(os.path.basename(__file__), config["base"]["Image_folder_name"])
pngregex = StringManipulation().createregex(config["base"]["Name_format"])+config["base"]["Image_format"]  # Creates the regex to validate the files
if not os.path.exists(img_folder_path):
    print("Didn't find", config["base"]["Image_folder_name"], "creating...")
    os.makedirs(config["base"]["Image_folder_name"])

CreateVisuModels()

if __name__ == "__main__":
    window_min_width = "500"    #16/9
    window_min_height = "281"   #

    main_window = Tk()
    ObjectCollection.windows['Main'] = main_window
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
