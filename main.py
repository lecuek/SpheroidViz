"""
start = time.time()
end = time.time()
print("Time of x: ", end-start)
# POUR TESTER LE TEMPS QUE PREND QQCHOSE
# 
# A CHANGER POUR QUE CA SOIT PLACE DANS UN SOUS DOSSIER             
"""
import sys
import rpy2.robjects.lib.ggplot2 as ggplot2
import rpy2.robjects.packages as rpackages
import rpy2.robjects as robjects
import screeninfo
import time
from CuekUtils import *
from object_collections import ObjectCollection as Oc
import queue
import threading
from tkinter import *
from PIL import Image, ImageTk
import os
from math import floor
import math
from math import fabs
import json
import random

print("Starting R, It will take a few seconds")
RANDOMcolors = ["blue","black","brown","red","yellow","green","orange","beige","turquoise","pink"]


class VisualizationCanvas(Canvas):  # Canvas used for visualization
    def __init__(self, keyname="", model=None, size="", label=None, *args, **kwargs):
        '''
        :param str keyname: Name in the collection
        if not specified = Visu_Canvas+lengthofcollection
        :param str size: Size of the canvas ex:("200x200")
        '''
        Canvas.__init__(self, *args, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.currentimgnum = 0
        self.previouslyownedmodels = {}
        self.showbasemodel = False
        self.imagefoldername = config["Main_output"]["Image_folder_name"]
        self.imagepath = "resources/selectamode.png"
        self.model = model
        self.label = label
        if "model" in kwargs:
            self.model = kwargs["model"]

        if size != "":
            try:
                # Simple regex to process wanted canvasgrid
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
        self.bind("<Configure>", self.OnResize)
        self.bind("<Button-3>", self.changemodel)
    
    
    def ChangeImage(self, imagename):  # Changes the image taking the 
        if self.showbasemodel:
            imagepath = self.imagefoldername+imagename
            imagetk = ImageTk.PhotoImage(
                master=self, image=Image.open(imagepath).resize((self.width,self.height),Image.ANTIALIAS)
            )  # .resize((self.width, self.height)))
            self.create_image(self.width/2, self.height/2, image=imagetk, anchor="center")
            self.image = imagetk
            self.imagepath = imagename
            return
        else:
            imagepath = self.outputpath+imagename
        try:
            #imgsize = str(self.height)+"x"+str(self.width)
            if self.model.ratio == -1:
                imagetk = ImageTk.PhotoImage(
                    master=self, image=Image.open(imagepath)
                )  # .resize((self.width, self.height)))
                self.model.ratio = imagetk.width()/imagetk.height()
                """if self.height > self.width:
                    imagetk = imagetk = ImageTk.PhotoImage(
                        master=self, image=Image.open(imagepath).resize((self.width, floor(self.width/self.model.ratio)),Image.ANTIALIAS))
                else:
                    imagetk = imagetk = ImageTk.PhotoImage(
                        master=self, image=Image.open(imagepath).resize((floor(self.height/self.model.ratio),self.height),Image.ANTIALIAS))"""
            # Makes the image's size proportionnal to it's creation size
            if self.height > self.width:
                imagetk = ImageTk.PhotoImage(
                    master=self, image=Image.open(imagepath).resize((self.width, floor(self.width/self.model.ratio))))
            else:
                imagetk = ImageTk.PhotoImage(
                    master=self, image=Image.open(imagepath).resize((floor(self.height/self.model.ratio),self.height)))
            self.create_image(self.width/2, self.height/2, image=imagetk, anchor="center")
            self.image = imagetk
            self.imagepath = imagepath
            return
        except Exception as e:
            print(e)

    def OnResize(self, event):
        # When the canvas is resized (So, when the window is.)
        
        self.width  = int(event.width)
        self.height = int(event.height)
        print(self.width, self.height)
        if self.model == None:
            # Made so the resize is proportionnal
            if self.height > self.width:
                image = ImageTk.PhotoImage(master=self, image=Image.open(self.imagepath).resize((self.width,self.width)))
            else:
                image = ImageTk.PhotoImage(master=self, image=Image.open(self.imagepath).resize((self.height,self.height)))
        else:
            # Made so the resize is proportionnal
            if self.height > self.width:
                image = ImageTk.PhotoImage(
                    master=self,
                    image=Image.open(
                        self.imagepath
                    ).resize(
                        (self.width,floor(self.width*fabs(self.model.ratio)))
                    )
                )
            else:
                image = ImageTk.PhotoImage(master=self, image=Image.open(self.imagepath).resize((floor(self.height*fabs(self.model.ratio)),self.height)))

        self.create_image(self.width/2, self.height/2, image=image, anchor="center")
        self.image = image
    
    def changemodel(self, event):
        # Change visualization mode
        # Gets selected function and param from popup
        result = ModeSelectionPopup(self).getchoice()
        if result != ["", ""]:
            if result == "none":  # When the user chose "None" or the canvas does not have a model already
                self.showbasemodel = False
                self.model = None
                self.label.config(text="None")
                self.image = Oc.images["noimage"]
                self.update()
                return
            if(result == "base"):  # Treating the base model
                self.showbasemodel = True
                self.model = None
                self.label.config(text="Base")
                return
            self.showbasemodel = False
            visualization_name = result[0]+"-"+result[1]
            if visualization_name not in self.previouslyownedmodels.keys():
                print("Chose",visualization_name)
                self.model = VisualizationModel(result[0], result[1])
                self.previouslyownedmodels[visualization_name] = self.model
            else:
                self.model = self.previouslyownedmodels[visualization_name]
            self.label.config(text=self.model.name)

        else:
            print("Canceled")


class VisualizationModel(object):  # The model that will be treated/displayed 
    def __init__(self, function, param):
        """
        param str function: The function to use from the R Script\n
        param str param: The parameter to use from the R Script
        """
        self.function = function
        self.param = param
        self.nameFormat = config["Main_output"]["Name_format"]
        self.imageExtension = config["Main_output"]["Image_extension"]
        self.actualModelOut = []
        self.name = self.function+"-"+self.param
        self.ratio = -1

    def GetFilenameAtStep(self, timeStep):
        return NameFormat(self.nameFormat, timeStep)+self.imageExtension

# The class used for the popup window when clicking on a Canvas
class ModeSelectionPopup(object):
    def __init__(self, parent):
        self.toplevel = Toplevel(parent)
        self.toplevel.title("Changing mode")
        self.toplevel.resizable = (False,False)
        self.selection = ["", ""]
        # WIDGETS INIT -----------------------------------------

        # Button Frame
        self.frame = Frame(self.toplevel)
        self.frame.grid(row=0, column=0)
        self.bottomframe = Frame(self.toplevel)
        self.bottomframe.grid(row=1, column=0)
        # Label1
        self.l1 = Label(
            self.frame,
            text="Select your visualization model"
        )
        self.l1.grid(row=0, column=0)

        self.createlistboxes()

        # Ok Button
        self.b = Button(self.bottomframe,
                        text="Base model", command=self.onclickbase)
        self.b.grid(row=0, column=0, sticky=N+E+W+S)
        self.b = Button(self.bottomframe,
                        text="None", command=self.onclicknone)
        self.b.grid(row=0, column=1, sticky=N+E+W+S)
        self.b = Button(self.bottomframe, text="Ok", command=self.onclickok)
        self.b.grid(row=1, column=0)

        # Cancel Button
        self.cancelbutton = Button(
            self.bottomframe, text="Cancel", command=self.cancel)
        self.cancelbutton.grid(row=1, column=1)

        self.toplevel.update_idletasks()
        self.toplevel.grab_set()
        # WIDGETS INIT -----------------------------------------

    def createlistboxes(self):  # Pretty self explanatory
        # Functions Listbox
        self.functionLb = Listbox(self.frame)
        functions = visuconfig["functions"]
        functions.sort()

        # Inserts in listbox
        for i, function in enumerate(functions):
            self.functionLb.insert(i, function)
        # self.functionLb.bind("<<ListboxSelect>>", self.onlistbox1change)
        self.functionLb.grid(row=1, column=0)

        # Params Listbox
        self.paramsLb = Listbox(self.frame)
        params = visuconfig["params"]
        params.sort()

        for j, param in enumerate(params):
            self.paramsLb.insert(j, param)
        # self.paramsLb.bind("<<ListboxSelect>>", self.onlistbox2change)
        self.paramsLb.grid(row=1, column=1)

    def cancel(self):  # When Cancel is clicked
        self.selection = ["", ""]
        self.toplevel.destroy()

    def onclicknone(self):
        self.selection = "none"
        self.toplevel.destroy()

    def onclickbase(self):
        self.selection = "base"
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
        self.canvasresizestep = 10
        self.title("Visualization")
        self.window_width   = ScreenResolution[0]
        self.window_height  = ScreenResolution[1]
        self.maxsize(self.window_width, self.window_height)
        #self.resizable = (False,False)
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
        self.topframe       = Frame(self)
        self.bottomframe    = Frame(self)
        self.initcanvas()
        self.initplaystop()
        self.initrest()
        self.topframe.pack(side="top",fill="both", expand=True)
        self.bottomframe.pack(side="bottom", fill="x", expand=False)
        
        print("Widgets created")


    def initcanvas(self, canvasgrid="2x2"):  # Initializes the visualization canvases
        print("Creating Canvas(es)")
        
        try:  # try,except to catch any wrongly written size
            # Simple regex to process wanted canvasgrid
            dim = re.split(r"x|X", canvasgrid)
            i = int(dim[0])
            j = int(dim[1])
            k = 0  # to name the canvas
        except Exception as e:
            print(e, canvasgrid)
            print("Error, couldn't get model grid size exiting window")
            self.destroy()

        # Creates the canvases

        self.topframe.grid(sticky="nesw")
        #self.topframe.configure(bg="red")
        for row in range(i):
            self.topframe.grid_rowconfigure(row, weight=1)
            for col in range(j):
                self.topframe.grid_columnconfigure(col, weight=1)
                
                canvframe = Frame(self.topframe)
                canvframe.grid_columnconfigure(0, weight=1)
                canvframe.grid_rowconfigure(1, weight=1)
                canvframe.grid(row=row, column=col, sticky="nsew")
                #canvframe.configure(bg=random.choice(RANDOMcolors))
                lab = Label(canvframe, text="None")
                lab.grid(row=0, column=0)
                c = VisualizationCanvas(
                    "Visu_Canvas"+str(k),
                    #size=config["config"]["Visualization_size"],
                    size = "200x200",
                    label=lab,
                    master=canvframe,
                    #bg="#66ccff",
                    highlightthickness=0
                )
                c.grid(row=1, column=0, sticky="nesw")
                noimage = Oc.images["noimage"]
                c.image = noimage
                c.update()
                self.ownedcanvas.append(c)
                k += 1
        # CANVAS INITIALIZATION------------------------------------------------------------------------
        print("Created Canvas(es)")




    def initplaystop(self):  # Initializes the play/stop functionnality widgets
        self.playframe = Frame(self.bottomframe)
        self.playframe.grid(row=1, column=0, sticky="nesw")
        self.playframe.grid_columnconfigure(6, weight=1)


        self.playbutton = Button(
            self.playframe, text="Play", command=self.play_anim)
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

        self.stopbutton = Button(
            self.playframe, text="Stop", command=self.stop_anim)
        self.stopbutton.grid(row=0, column=5)
        Oc.button_collection.add(self.stopbutton)


    def initrest(self):  # Initializes the rest of the widgets

        # CHECKBOX (Keep slider at last index)
        self.toend_checkbox = Checkbutton(
            self.playframe,
            variable=self.cb_checked,
            onvalue=True,
            offvalue=False,
            text="Keep slider at end",
            command=SliderUpdate
        )
        Oc.checkboxes["Visu_Checkbox" +
                      str(len(Oc.checkboxes))] = self.toend_checkbox
        self.toend_checkbox.grid(row=0, column=7)

        # SCALE
        self.update()  # Update to be able to get the window size
        numberofpngs = Dm.getnumberofpng(img_folder_path, pngregex)

        # Bug fix (slider starting at -1 if no image found)
        if numberofpngs == -1:
            numberofpngs = 1
        self.slider = MyScale(
            self.bottomframe,
            from_=0,
            to=numberofpngs-1,
            length=self.winfo_reqwidth(),
            command=self.OnSliderStep,
            orient=HORIZONTAL
        )
        # NAMING SLIDER (for easy ctrl+f search)
        Oc.sliders['Visu_Scale1'] = self.slider
        self.bottomframe.grid_rowconfigure(0, weight=1)
        self.bottomframe.grid_columnconfigure(0, weight=1)
        self.slider.grid(row=0, column=0, sticky="nesw")

    def getsliderobject(self):  # Returns the slider
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
        if self.entryto_text.get() == "":
            self._to = int(self.slider.cget("to"))
            print(self._to)
        if self.entryfrom_text.get() == "":
            self._from = 0
        else:
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
                print("Something went wrong\n", e)
        # Parameters for the continue_anim method
        self.slider.set(self._from)
        self.playsliderpos = self._from
        self.playdelay = 100
        self.continue_anim()

    def continue_anim(self):  # Plays the animation
        # Calls itself every x miliseconds and pushes the slider
        if self.playsliderpos > self._to or self.askedstop or self.playsliderpos > self.slider.maximum:
            print("Stopped")
            self.toend_checkbox.configure(state=NORMAL)
            return
        self.slider.set(self.playsliderpos)
        self.playsliderpos += 1
        self.after(self.playdelay, self.continue_anim)

    def stop_anim(self):
        # Called when clicking stop
        self.askedstop = True

    def OnSliderStep(self, num):
        # 
        num = int(num)
        for canvas in self.ownedcanvas:
            if canvas.model is not None:
                filename = canvas.model.GetFilenameAtStep(num)
                # For every previously owned models of this canvas
                if filename not in canvas.model.actualModelOut:
                    r[canvas.model.function](canvas.model.param, num).plot
                    r.ggsave(
                        canvas.outputpath+filename,
                        width=10,
                        height=10,
                        dpi=100,
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
            elif canvas.showbasemodel:
                canvas.ChangeImage(NameFormat(config["Main_output"]["Name_format"], num)+config["Main_output"]["Image_extension"])

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
        Oc.windows['Visu'].after(400, AfterCallback)
        return
    Oc.windows['Visu'].after(400, AfterCallback)


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
        print(e)
        thread = threading.Thread(target=ThreadTarget, daemon=True)
        thread.start()


# Processes the Name_Format in config to a complete name ex: test$$$ -> test025
def NameFormat(nameformat, num):
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
    # Dm.svg_to_png(path=img_folder_path)
    numberofpngs = Dm.getnumberofpng(path=img_folder_path, reg=pngregex)
    slider.configure(to=numberofpngs-1)
    if visu_window.checkbox_get():  # To set at the end if the checkbox is ON
        slider.set(numberofpngs-1)


def CloseMainWindow():  # Called when closing the main window
    # Made to avoid R causing errors when closing
    try:
        r["dev.off"]()
        Oc.windows["Main"].destroy()
    except:
        Oc.windows["Main"].destroy()


if __name__ == "__main__":

    monitors = screeninfo.get_monitors()
    
    global ScreenResolution
    ScreenResolution = (monitors[0].width,monitors[0].height)
    
    print("Screen Resolution is ", ScreenResolution)
    
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
        os.path.basename(__file__), config["Main_output"]["Image_folder_name"])

    # Creates the regex to validate the files
    pngregex = StringManipulation().createregex(
        config["Main_output"]["Name_format"])+config["Main_output"]["Image_extension"]
    if not os.path.exists(img_folder_path):
        print("Didn't find", config["Main_output"]
              ["Image_folder_name"], "creating...")
        os.makedirs(config["Main_output"]["Image_folder_name"])

    
    window_width = "500"  # 16/9
    window_height = "281"   #
    canvsize = config["config"]["Visualization_size"]
    canvaswidth = int(canvsize.split("x")[0])
    canvasheight= int(canvsize.split("x")[1])
    main_window = Tk()
    Oc.images["noimage"] = ImageTk.PhotoImage(master=main_window,image=Image.open("resources/selectamode.png").resize((canvaswidth,canvasheight)))
    main_window.title("SpheroidViz - Visualization app")
    main_window.option_readfile("options")
    main_window.grid_columnconfigure(0, weight=1)
    main_window.grid_rowconfigure(0, weight=1)
    Oc.windows['Main'] = main_window  # NAMING MAIN WINDOW (ctrl+f)
    main_window.bind("WM_DELETE_WINDOW", CloseMainWindow)
    main_window.minsize(width=window_width, height=window_height)
    main_window.resizable = (False,False)

    texte = Label(main_window, text="SpheroidViz\nCreated by Benjamin.C")
    texte.grid(row=0, column=0)

    bouton = Button(main_window, text="Open Visualization Window",
                    command=VisuWindow, background="#b3d9ff")
    bouton.grid(row=1, column=0)

    try:
        main_window.mainloop()
    except KeyboardInterrupt:
        print("Mainloop interrupted by keyboard")