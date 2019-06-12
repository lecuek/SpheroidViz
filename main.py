import time
from CuekUtils import *
from object_collections import ObjectCollection as Oc
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
            keyname = "Window"+str(len(Oc.windows))
        Oc.windows[keyname] = self
        self.grab_set()

    def stop(self):
        self.grab_release()
        self.destroy()


class VisualizationCanvas(Canvas):  # Canvas used for visualization
    def __init__(self, keyname="", model=None, size="", *args, **kwargs):
        '''
        :param str keyname: Name in the collection
        if not specified = Visu_Canvas+lengthofcollection
        :param str size: Size of the canvas ex:("200x200")
        '''
        Canvas.__init__(self, *args, **kwargs)
        self.currentimgnum = 0
        self.model = model
        if "model" in kwargs:
            self.model = kwargs["model"]

        if size != "":
            try:
                # Simple regex to process wanted modelgrid
                dim = re.split(r"x|X", size)
                self.width = int(dim[0])
                self.height = int(dim[1])
            except Exception as e:
                self.width = self.height = 200
                print("Couldn't process the given size for canvas", e)
                print("Setting default 200x200px")
        
        self.configure(width=self.width, height=self.height, bg=self.model.color)
        if keyname == "":
            keyname = "Visu_Canvas"+str(len(Oc.canvases))
        Oc.canvases[keyname] = self
        self.bind("<Button-3>", self.changemode)

    def ChangeImage(self, num):  # Changes the image
        """
        param int num: image number in directory 
        """
        self.currentimgnum = num
        imagepath = (self.model.image_folder_name
        + NameFormat(self.model.name_format,num)
        + self.model.image_format)
        try: 
            imgsize = str(self.height)+"x"+str(self.width)
            image = ImageTk.PhotoImage(
                master=self, image=Image.open(imagepath).resize((self.width,self.height),Image.ANTIALIAS))
            self.create_image(0, 0, image=image, anchor="nw")
            self.image = image
        except Exception as e:
            print(e)
            print(imagepath, "doesn't exist")

    def changemode(self, event):
        # Change visualization mode
        result = ModeSelectionPopup(self).getchoice()
        if result != "":
            self.model = Oc.visualization_modes[result]
            self.ChangeImage(self.currentimgnum)
        else:
            print("Canceled")


class VisualisationMode(object):
    def __init__(self, key, values):

        self.name = values["Name"]
        self.image_folder_name = values["Image_folder_name"]
        self.name_format = values["Name_format"]
        self.image_format = values["Image_format"]
        self.color = values["color"]
        self.isShown = True
        Oc.visualization_modes[self.name] = self

    def __str__(self):
        return self.name

    def getcolor(self):
        return self.color


class ModeSelectionPopup(object):
    def __init__(self, parent):
        self.toplevel = Toplevel(parent)
        self.toplevel.title("Changement de mode")
        self.selection = ""
        # WIDGETS INIT -----------------------------------------

        # Button Frame
        self.frame = Frame(self.toplevel)
        self.frame.grid(row=2, column=0)
        # Label1
        self.l1 = Label(
            self.toplevel, text="Choisissez votre mode de visualisation")
        self.l1.grid(row=0, column=0)

        # Listbox1
        self.lb = Listbox(self.toplevel, selectmode=SINGLE)
        numberofvis = Oc.visualization_modes

        # Sorts the selection
        self.vislist = []
        for vismod in numberofvis.values():
            self.vislist.append(str(vismod))
        self.vislist.sort()

        # Inserts in listbox
        for i, vis in enumerate(self.vislist):
            self.lb.insert(i, vis)
        self.lb.bind("<<ListboxSelect>>", self.onlistboxchange)
        self.lb.grid(row=1, column=0)

        # Ok Button
        self.b = Button(self.frame, text="Ok", command=self.toplevel.destroy)
        self.b.grid(row=2, column=0)

        # Cancel Button
        self.cancelbutton = Button(
            self.frame, text="Cancel", command=self.cancel)
        self.cancelbutton.grid(row=2, column=1)

        self.toplevel.update_idletasks()
        self.toplevel.grab_set()
        # WIDGETS INIT -----------------------------------------

    def cancel(self):
        self.selection = ""
        self.toplevel.destroy()

    def onlistboxchange(self, event):  # Whenever the user selects an option
        w = event.widget
        index = int(w.curselection()[0])
        self.selection = w.get(index)

    def getchoice(self):  # Returns the selected option
        self.toplevel.wait_window()
        return self.selection


class VisuWindow(Toplevel):

    def __init__(self, *args, **kwargs):
        print("Creating visualization window")
        Toplevel.__init__(self, *args, *kwargs)
        self.title("Visualisation")
        self.window_min_width = "400"
        self.window_min_height = "450"
        self.minsize(self.window_min_width, self.window_min_height)
        self.cb_checked = BooleanVar()
        self.cb_checked.set(False)
        self.ownedcanvas = []
        self.askedstop = False
        self.initwidgets()
        self.Visu_Window()
        Oc.windows["Visu"] = self  # NAMING VISU WINDOW
        self.grab_set()

    def initwidgets(self):
        print("Creating widgets")
        self.mainframe = Frame(self)

        # WIDGET INITIALIZATION------------------------------------------------------------------------
        self.initmodels()
        self.initplaystop()
        self.initrest()
        self.mainframe.grid(row=0, column=0)
        # WIDGET INITIALIZATION------------------------------------------------------------------------
        print("Widgets created")
    
    # WIDGET INITIALIZATION------------------------------------------------------------------------

    def initmodels(self, modelgrid="2x2"):  # Initializes the visualization canvases
        # CANVAS INITIALIZATION------------------------------------------------------------------------
        print("Creating Canvas(es)")
        frame = Frame(self)
        frame.grid(row=0, column=0)
        try:  # try,except to catch any wrongly written size
            # Simple regex to process wanted modelgrid
            dim = re.split(r"x|X", modelgrid)
            i = int(dim[0])
            j = int(dim[1])
            k = 0  # to name the canvas
        except Exception as e:
            print(e, modelgrid)
            print("Error, couldn't get model grid size exiting window")
            self.destroy()

        # Creates the canvases and adds the corresponding visualization models to it
        # list made to order the apparition of the canvases
        modellist = []
        for key in Oc.visualization_modes.keys():
            modellist.append(key)
        modellist.sort()

        for row in range(i):
            for col in range(j):
                if(k > len(modellist)-1):
                    print("Can't create new canvas: not enough models to choose from")
                    break

                c = VisualizationCanvas(
                    "Visu_Canvas"+str(k),
                    size=config["config"]["Visualization_size"],
                    master=frame,
                    borderwidth=1,
                    model=Oc.visualization_modes[modellist[k]]
                )

                c.grid(row=row, column=col)
                self.ownedcanvas.append(c)
                k += 1
        # CANVAS INITIALIZATION------------------------------------------------------------------------
        print("Created Canvas(es)")
    def initplaystop(self):
        self.playframe = Frame(self)
        self.playframe.grid(row=3, column=0)

        self.playbutton = Button(self.playframe, text="Play", command=self.play_anim)
        self.playbutton.grid(row=0, column=0)
        Oc.button_collection.add(self.playbutton)

        self.textfrom = Label(self.playframe, text=" From:")
        self.textfrom.grid(row=0, column=1)
        
        self.entryfrom_text = StringVar()
        self.entryfrom = Entry(
            self.playframe,
            textvariable=self.entryfrom_text
        )
        self.entryfrom.grid(row=0, column=2)

        self.textto = Label(self.playframe, text=" To:")
        self.textto.grid(row=0, column=3)

        self.entryto_text = StringVar()
        self.entryto = Entry(
            self.playframe,
            textvariable=self.entryto_text
        )
        self.entryto.grid(row=0, column=4)

        self.stopbutton = Button(self.playframe, text="Stop", command=self.stop_anim)
        self.stopbutton.grid(row=1)
        Oc.button_collection.add(self.stopbutton)

    def initrest(self):
        self.rightframe = Frame(self)
        self.rightframe.grid(row=0, column=1)

         # CHECKBOX (Keep slider at last index)
        self.toend_checkbox = Checkbutton(
            self.rightframe,
            variable=self.cb_checked,
            onvalue=True,
            offvalue=False,
            text="Keep slider at end",
            command=SliderUpdate
        )
        Oc.checkboxes["Visu_Checkbox"+str(len(Oc.checkboxes))] = self.toend_checkbox
        self.toend_checkbox.grid(row=0, column=0)

        # SCALE
        self.update()  # Update to be able to get the window size
        numberofpngs = Dm.getnumberofpng(img_folder_path, pngregex)
        
        if numberofpngs == -1:  # Bug fix (slider starting at -1 if no image found)
            numberofpngs = 1
        self.slider = Scale(
            self,
            from_=0,
            to=numberofpngs-1,
            length=self.winfo_reqwidth(),
            command=self.OnSliderChange,
            orient=HORIZONTAL
        )
        Oc.sliders['Visu_Scale1'] = self.slider  # NAMING SLIDER (for easy ctrl+f search)

        self.slider.grid(row=1, column=0)

    # WIDGET INITIALIZATION------------------------------------------------------------------------
    def getsliderobject(self):
        return self.slider

    def checkbox_get(self):
        #Gets the state of the checkbox
        return self.cb_checked.get()

    def play_anim(self):
        # Input verifications
        if self.cb_checked:
            self.toend_checkbox.toggle()
            self.toend_checkbox.configure(state=DISABLED)

        self.askedstop = False
        try:
            try:
                self._from = int(self.entryfrom_text.get())
            except Exception as e:
                print(e)
                return
            try:
                self._to = int(self.entryto_text.get())
            except Exception as e:
                print(e)
                return
        except Exception as e:
            print("Something went wrong\n",e)
        self.slider.set(self._from)
        # Slidermax: to limit the play function to go to the max of the slider
        # self.slidermax = self.slider // Waiting for answers on Stackoverflow
        self.playsliderpos = self._from
        self.playdelay = 100
        self.continue_anim()

    def continue_anim(self):
        if self.playsliderpos > self._to or self.askedstop:
            self.toend_checkbox.configure(state=NORMAL)
            return
        self.slider.set(self.playsliderpos)
        self.playsliderpos += 1
        self.after(self.playdelay,self.continue_anim)
        

    def stop_anim(self):
        self.askedstop = True

    # When the slider step changes should load the corresponding visualization model
    def OnSliderChange(self, num):
        # Idea on how to do it:
        # Create a method on the Canvas to load the image with the model's image_folder_name etc and the method NameFormat
        for canvas in self.ownedcanvas:
            canvas.ChangeImage(self.slider.get())

    def Visu_Window(self):  # Will decide later if i put this in __init__
        thread = threading.Thread(target=ThreadTarget, daemon=True)
        Oc.threadings['Thread_Scan1'] = thread  # NAMING THREAD (ctrl+f s)
        thread.start()
        self.after(100, AfterCallback)


def AfterCallback():
    # Method calls itself every second to check for instructions in the queue to execute
    try:
        value = scan_queue.get(block=False)
    except queue.Empty:
        Oc.windows['Visu'].after(500, AfterCallback)
        return
    if value == "UpdateSlider":
        SliderUpdate()
    Oc.windows['Visu'].after(500, AfterCallback)
# For Threading -----------------------------------------------------------------------------------
# This part is reserved to actions executed from secondary threads


def ThreadTarget():
    # Method lists the directory containing the main svg files and launches the conversion
    # if the directory contains more svg than the previous scan
    previousScan = 0
    try:
        while True:
            scan = len(os.listdir(img_folder_path))
            if scan > previousScan:
                Dm.svg_to_png(img_folder_path)
            previousScan = scan
            scan_queue.put("UpdateSlider")
            time.sleep(1)
    except KeyboardInterrupt:
        print("ThreadTarget Keyboard interrupt")
# For Threading -----------------------------------------------------------------------------------
# DATA PROCESSING ---------------------------------------------------------------------------------

def NameFormat(nameformat,num):  # process le format du nom dans le fichier json pour remplacer les $
    nom = nameformat
    compt = 0
    for i in nom:
        if i == '$':
            compt += 1
    compt -= len(str(num))
    nom = nom.strip("$")
    nbzero = ""
    for i in range(compt):
        nbzero += "0"
    nom += nbzero+str(num)
    return nom

# DATA PROCESSING ---------------------------------------------------------------------------------
# GUI INTERACTION ---------------------------------------------------------------------------------


def SliderUpdate(msg=""):  # Updates the slider
    visu_window = Oc.windows["Visu"]
    slider = Oc.sliders["Visu_Scale1"]
    if msg != "":
        print(msg)
    Dm.svg_to_png(path=img_folder_path)
    numberofpngs = Dm.getnumberofpng(path=img_folder_path, reg=pngregex)
    slider.configure(to=numberofpngs-1)
    if visu_window.checkbox_get():  # To set at the end if the checkbox is ON
        slider.set(numberofpngs-1)
# GUI INTERACTION ---------------------------------------------------------------------------------

# MAIN --------------------------------------------------------------------------------------------

def CreateVisuModels():
    # Creation of Visualization mode objects
    i = 0
    for key, value in config["Visualizations"].items():
        try:
            VisualisationMode(key, value)
            i += 1
        except:
            print("Model",key,"could not be created")

    print("created", i, "visualization models ")


colors = ["blue", "green", "red", "yellow",
          "white", "black", "pink"]  # Debug colors
Dm = DataManagement()
config = json.load(open("config.json"))  # loads config.json
# Initializes the queue used for the scanning of the folder
scan_queue = queue.Queue()

img_folder_path = os.path.realpath(__file__).replace(
    os.path.basename(__file__), config["base"]["Image_folder_name"])

# Creates the regex to validate the files
pngregex = StringManipulation().createregex(
    config["base"]["Name_format"])+config["base"]["Image_format"]
if not os.path.exists(img_folder_path):
    print("Didn't find", config["base"]["Image_folder_name"], "creating...")
    os.makedirs(config["base"]["Image_folder_name"])

# Initializes the visualization models
CreateVisuModels()

if __name__ == "__main__":
    window_min_width = "500"  # 16/9
    window_min_height = "281"   #

    window_max_width = "500"   #
    window_max_height = "281"   #

    main_window = Tk()
    main_window.option_readfile("options")
    main_window.grid_columnconfigure(0, weight=1)
    main_window.grid_rowconfigure(0, weight=1)
    Oc.windows['Main'] = main_window  # NAMING MAIN WINDOW (ctrl+f)
    main_window.minsize(width=window_min_width, height=window_min_height)
    main_window.maxsize(width=window_max_width, height=window_max_height)

    # WIDGET INITIALIZATION------------------------------------------------------------------------

    texte = Label(main_window, text="SpheroidViz")
    texte.grid(row=0, column=0)

    bouton = Button(main_window, text="Lancer la visualisation",
                    command=VisuWindow, background="#b3d9ff")
    bouton.grid(row=1, column=0)

    # WIDGET INITIALIZATION------------------------------------------------------------------------

    try:
        main_window.mainloop()
    except KeyboardInterrupt:
        print("Mainloop interrupted by keyboard")