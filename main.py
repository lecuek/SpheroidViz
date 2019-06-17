"""
start = time.time()
end = time.time()
print("Time of x: " end-start)
# POUR TESTER LE TEMPS QUE PREND QQCHOSE                
"""

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

print("Starting R, It will take a few seconds")
import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages
import rpy2.robjects.lib.ggplot2 as ggplot2


class PopupWindow(Toplevel):  # Window class that works like a popup (Mostly unused, may remove later)
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
    def __init__(self, keyname="", model=None, size="", label=None,*args, **kwargs):
        '''
        :param str keyname: Name in the collection
        if not specified = Visu_Canvas+lengthofcollection
        :param str size: Size of the canvas ex:("200x200")
        '''
        Canvas.__init__(self, *args, **kwargs)
        self.currentimgnum = 0
        self.previouslyownedmodels = {}
        self.model = model
        self.label = label
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
        
        self.configure(width=self.width, height=self.height)
        if keyname == "":
            keyname = "Visu_Canvas"+str(len(Oc.canvases))
        self.name = keyname
        self.outputpath = config["Canvas_output"]["Output_folder"]+self.name+"/"
        if not os.path.exists(self.outputpath):
            os.makedirs(self.outputpath)
        Oc.canvases[keyname] = self
        self.bind("<Button-3>", self.changemodel)

    def ChangeImage(self, imagename):  # Changes the image
        imagepath = self.outputpath+imagename
        try: 
            #imgsize = str(self.height)+"x"+str(self.width)
            image = ImageTk.PhotoImage(
                master=self, image=Image.open(imagepath))#.resize((self.width,self.height)))
            self.create_image(0, 0, image=image, anchor="nw")
            self.image = image
            return
        except Exception as e:
            print(e)
            print(imagepath, "doesn't exist")
        
    #plotspherattime uptake glucose 0-20
    #plotspherattime nuclear volume 10-20
    #plotspherattime uptake glucose 0-20


    def changemodel(self, event):
        # Change visualization mode
        result = ModeSelectionPopup(self).getchoice()  # Gets selected function and param from popup
        if result != ["",""]:
            visualization_name = result[0]+"-"+result[1]
            if visualization_name not in self.previouslyownedmodels.keys():
                print(visualization_name ,"This combination was not created")
                self.model = VisualizationModel(result[0],result[1])
                self.previouslyownedmodels[visualization_name] = self.model
            else:
                self.model = self.previouslyownedmodels[visualization_name]
            self.label.config(text=self.model.name)
            
        else:
            print("Canceled")


class VisualizationModel(object):
    def __init__(self, function, param):
        """
        param str function: The function to use from the R Script\n
        param str param: The parameter to use from the R Script
        """
        self.function = function
        self.param = param
        self.nameFormat = config["Sortie_principale"]["Name_format"]
        self.imageExtension = config["Sortie_principale"]["Image_extension"]
        self.actualModelOut = []
        self.name = self.function+"-"+self.param
    

    def GetFilenameAtStep(self, timeStep):
        return NameFormat(self.nameFormat, timeStep)+self.imageExtension


class ModeSelectionPopup(object):  # The class used for the popup window when clicking on a Canvas
    def __init__(self, parent):
        self.toplevel = Toplevel(parent)
        self.toplevel.title("Changement de mode")
        self.selection = ["",""]
        # WIDGETS INIT -----------------------------------------

        # Button Frame
        self.frame = Frame(self.toplevel)
        self.frame.grid(row=2, column=0)
        # Label1
        self.l1 = Label(
            self.toplevel, text="Choisissez votre mode de visualisation")
        self.l1.grid(row=0, column=0)

        self.createlistboxes()

        # Ok Button
        self.b = Button(self.frame, text="Ok", command=self.onclickok)
        self.b.grid(row=2, column=0)

        # Cancel Button
        self.cancelbutton = Button(
            self.frame, text="Cancel", command=self.cancel)
        self.cancelbutton.grid(row=2, column=1)

        self.toplevel.update_idletasks()
        self.toplevel.grab_set()
        # WIDGETS INIT -----------------------------------------


    def createlistboxes(self):  # Pretty self explanatory
        # Functions Listbox
        self.functionLb = Listbox(self.toplevel)
        functions = visuconfig["functions"]
        functions.sort()

        # Inserts in listbox
        for i, function in enumerate(functions):
            self.functionLb.insert(i, function)
        #self.functionLb.bind("<<ListboxSelect>>", self.onlistbox1change)
        self.functionLb.grid(row=1, column=0)

        # Params Listbox
        self.paramsLb = Listbox(self.toplevel)
        params = visuconfig["params"]
        
        for j, param in enumerate(params):
            self.paramsLb.insert(j, param)
        # self.paramsLb.bind("<<ListboxSelect>>", self.onlistbox2change)
        self.paramsLb.grid(row=1, column=1)
        

    def cancel(self):  # When Cancel is clicked
        self.selection = ["",""]
        self.toplevel.destroy()

    def onclickok(self):  # When Ok is clicked
        self.selection[0] = self.functionLb.get(ACTIVE)
        self.selection[1] = self.paramsLb.get(ACTIVE)
        self.toplevel.destroy()

    def getchoice(self):  # Returns the selected option
        self.toplevel.wait_window()
        return self.selection


class VisuWindow(Toplevel):  # The visualization window

    def __init__(self, *args, **kwargs):
        print("Creating visualization window")
        Toplevel.__init__(self, *args, *kwargs)
        self.title("Visualization")
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

    def initwidgets(self):  # Initializes widgets
        print("Creating widgets")
        self.mainframe = Frame(self)

        # WIDGET INITIALIZATION------------------------------------------------------------------------
        self.initmodels()
        self.initplaystop()
        self.initrest()
        self.mainframe.grid(row=0, column=0)
        # WIDGET INITIALIZATION------------------------------------------------------------------------
        print("Widgets created")
    
    def createtructemp(self):  # DEBUG FUNCTION: Creates the popup directly at the visu window init
        ModeSelectionPopup(self)
    # WIDGET INITIALIZATION------------------------------------------------------------------------

    def initmodels(self, modelgrid="2x3"):  # Initializes the visualization canvases
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
        

        for row in range(i):
            for col in range(j):
                """if(k > len(modellist)-1):
                    print("Can't create new canvas: not enough models to choose from")
                    break"""
                canvframe = Frame(frame)
                lab = Label(canvframe, text="None")
                lab.grid(row=0, column=0)
                c = VisualizationCanvas(
                    "Visu_Canvas"+str(k),
                    size=config["config"]["Visualization_size"],
                    label=lab,
                    master=canvframe,
                    bg="#66ccff"
                )
                c.grid(row=1, column=0)
                self.ownedcanvas.append(c)
                canvframe.grid(row=row, column=col)
                k += 1
        # CANVAS INITIALIZATION------------------------------------------------------------------------
        print("Created Canvas(es)")
    
    def initplaystop(self):  # Initializes the play/stop functionnality widgets

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

    def initrest(self):  # Initializes the rest of the widgets 

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
        self.slider = MyScale(
            self,
            from_=0,
            to=numberofpngs-1,
            length=self.winfo_reqwidth(),
            command=self.OnSliderStep,
            orient=HORIZONTAL
        )
        Oc.sliders['Visu_Scale1'] = self.slider  # NAMING SLIDER (for easy ctrl+f search)

        self.slider.grid(row=1, column=0)

    # WIDGET INITIALIZATION------------------------------------------------------------------------
    def getsliderobject(self):# Returns the slider
        return self.slider

    def checkbox_get(self):  # Gets the state of the checkbox
        return self.cb_checked.get()

    def play_anim(self):  # Initializes the animation process
        # Input verifications
        self.toend_checkbox.configure(state=DISABLED)
        if self.cb_checked.get():
            self.toend_checkbox.toggle()
            self.cb_checked.set(False)
        
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
        # Parameters for the continue_anim method
        self.slider.set(self._from)
        self.playsliderpos = self._from
        self.playdelay = 100
        self.continue_anim()

    def continue_anim(self):  # Plays the animation
        # Calls itself every x miliseconds and pushes the slider
        if self.playsliderpos > self._to or self.askedstop or self.playsliderpos>self.slider.maximum:
            print("Stopped")
            self.toend_checkbox.configure(state=NORMAL)
            return
        self.slider.set(self.playsliderpos)
        self.playsliderpos += 1
        self.after(self.playdelay,self.continue_anim)
        

    def stop_anim(self):
        # Called when clicking stop
        self.askedstop = True

# environment map nuclear volume


    # When the slider step changes should load the corresponding visualization model
    def OnSliderStep(self, num):
        num = int(num)
        for canvas in self.ownedcanvas:
            if canvas.model is not None:
                filename = canvas.model.GetFilenameAtStep(num)
                # For every previously owned models of this canvas
                if filename not in canvas.model.actualModelOut:
                    r[canvas.model.function](canvas.model.param, num).plot
                    r.ggsave(
                        canvas.outputpath+filename,
                        width=canvas.width/50,
                        height=canvas.height/50,
                        dpi=50,
                        units="in"
                    )
                    canvas.model.actualModelOut.append(filename)
                else:
                    canvas.ChangeImage(filename)
                    continue
                for model in canvas.previouslyownedmodels.values():
                    # If the model is not the actual model possessed by the canvas
                    if (model != canvas.model) and (filename in model.actualModelOut):
                        # Delete the name of the file from the previous outputs of the model
                        # because it's gonna get replaced
                        model.actualModelOut.remove(filename)
                canvas.ChangeImage(filename)

    def Visu_Window(self):  # Will decide later if i put this in __init__
        # Initializes the last components
        thread = threading.Thread(target=ThreadTarget, daemon=True)
        Oc.threadings['Thread_Scan1'] = thread  # NAMING THREAD (ctrl+f s)
        thread.start()
        self.after(100, AfterCallback)


class MyScale(Scale):  # My Scale class (was created to add a "maximum" value but not really necessary since widget.cget() exists)
    def __init__(self, *args, **kwargs):
        Scale.__init__(self, *args, **kwargs)
        try:
            self.maximum = kwargs["to"]
        except:
            self.maximum = 100


def AfterCallback():  # Method calls itself every second to check for instructions in the queue to execute
    try:
        value = scan_queue.get(block=False)
        value()
    except queue.Empty:
        Oc.windows['Visu'].after(500, AfterCallback)
        return
    """if value == "UpdateSlider":
        SliderUpdate()"""
    Oc.windows['Visu'].after(500, AfterCallback)


def ThreadTarget():  # The Target of the second thread
    # Method lists the directory containing the main svg files and launches the conversion
    # if the directory contains more svg than the previous scan
    previousScan = 0
    try:
        while True:
            scan = len(os.listdir(img_folder_path))
            if scan > previousScan:
                Dm.svg_to_png(img_folder_path)
            previousScan = scan
            scan_queue.put(SliderUpdate)
            time.sleep(1)
    except KeyboardInterrupt:
        print("ThreadTarget Keyboard interrupt")
    except Exception as e:
        print("ddddddddddddddddddddddddd",e)
        thread = threading.Thread(target=ThreadTarget, daemon=True)
        thread.start()



def NameFormat(nameformat,num):  # Processes the Name_Format in config to a complete name ex: test$$$ -> test025 
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


def SliderUpdate(msg=""):  # Called to update the slider and change it's maximum 
    visu_window = Oc.windows["Visu"]
    slider = Oc.sliders["Visu_Scale1"]
    if msg != "":
        print(msg)
    #Dm.svg_to_png(path=img_folder_path)
    numberofpngs = Dm.getnumberofpng(path=img_folder_path, reg=pngregex)
    slider.configure(to=numberofpngs-1)
    if visu_window.checkbox_get():  # To set at the end if the checkbox is ON
        slider.set(numberofpngs-1)



def CloseMainWindow(): # Called when closing the main window
    # Made to avoid R causing errors when closing
    r["dev.off"]()
    Oc.windows["Main"].destroy()

if __name__ == "__main__":    

    # Loads config.json
    print("Loading config.json...")
    config = json.load(open("config.json"))  
    visuconfig = json.load(open("visu.json"))
    r = robjects.r
    try:
        r.source("LiveSimulation.R")
    except Exception as e:
        print("Did no find LiveSimulation.R\n", e)

    Dm = DataManagement()
    
    # Initializes the queue used after scanning the folder
    print("Initializing Queue...")
    scan_queue = queue.Queue()

    
    img_folder_path = os.path.realpath(__file__).replace(
        os.path.basename(__file__), config["Sortie_principale"]["Image_folder_name"])

    
    # Creates the regex to validate the files
    pngregex = StringManipulation().createregex(
        config["Sortie_principale"]["Name_format"])+config["Sortie_principale"]["Image_extension"]
    if not os.path.exists(img_folder_path):
        print("Didn't find", config["Sortie_principale"]["Image_folder_name"], "creating...")
        os.makedirs(config["Sortie_principale"]["Image_folder_name"])


    # MAIN WINDOW ---------------------------------------------------------------------------------
    
    window_min_width = "500"  # 16/9
    window_min_height = "281"   #

    window_max_width = "500"   #
    window_max_height = "281"   #
    main_window = Tk()
    main_window.title("SpheroidViz - Visualization app")
    main_window.option_readfile("options")
    main_window.grid_columnconfigure(0, weight=1)
    main_window.grid_rowconfigure(0, weight=1)
    Oc.windows['Main'] = main_window  # NAMING MAIN WINDOW (ctrl+f)
    main_window.bind("WM_DELETE_WINDOW", CloseMainWindow)
    main_window.minsize(width=window_min_width, height=window_min_height)
    main_window.maxsize(width=window_max_width, height=window_max_height)
    # WIDGET INITIALIZATION------------------------------------------------------------------------

    texte = Label(main_window, text="SpheroidViz\nCreated by Benjamin.C")
    texte.grid(row=0, column=0)

    bouton = Button(main_window, text="Open Visualization Window",
                    command=VisuWindow, background="#b3d9ff")
    bouton.grid(row=1, column=0)

    # WIDGET INITIALIZATION------------------------------------------------------------------------
    
    # MAIN WINDOW ---------------------------------------------------------------------------------

    try:
        main_window.mainloop()
    except KeyboardInterrupt:
        print("Mainloop interrupted by keyboard")