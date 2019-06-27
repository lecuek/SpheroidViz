# -*- coding: utf-8 -*-
import sys
import rpy2.robjects.lib.ggplot2 as ggplot2
import rpy2.robjects.packages as rpackages
import rpy2.robjects as robjects
import screeninfo
import time
from Utils import *
import subprocess
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


class VisualizationCanvas(Canvas):  
    """This class is the class used to create de Canvases that displays the created models.
    """
    def __init__(self, keyname="", model=None, size="", label=None, *args, **kwargs):
        """
        Args:
            keyname (str, optional): Key name in the collection
            if not specified = Visu_Canvas+lengthofcollection
            
            size (str, optional): Size of the canvas ex:("200x200")
            (mostly obsolete since it scales with the window)
        """
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
        self.baseratio = 1
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
        self.bind("<Button-3>", self.ChangeModel)
    
    
    def ChangeImage(self, imagename):  
        """Changes the image displayed on the canvas
        Args:
            imagename (str): The name of the image to display
        """
        try:
            if self.showbasemodel:
                imagepath = self.imagefoldername+imagename
                if self.height > self.width:
                    imagetk = ImageTk.PhotoImage(
                        master=self, image=Image.open(imagepath).resize(( self.width, floor( self.width/self.baseratio) ) )
                    )
                else:
                    imagetk = ImageTk.PhotoImage(
                        master=self, image=Image.open(imagepath).resize((floor( self.height/self.baseratio), self.height) )
                    )
                self.create_image(self.width/2, self.height/2, image=imagetk, anchor="center")
                self.image = imagetk
                self.imagepath = imagepath
                return
            else:
                imagepath = self.outputpath+imagename
            if self.model.ratio == -1:
                imagetk = ImageTk.PhotoImage(
                    master=self, image=Image.open(imagepath)
                )
                self.model.ratio = imagetk.width()/imagetk.height()
                
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
        """When the canvas is resized, resizes the image inside the canvas to fit """
        self.width  = int(event.width)
        self.height = int(event.height)
        if self.model == None: # No need to calculate the ratio since we know "selectamode.png" is completely square
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
                    # fabs() used to avoid negative numbers
                    image=Image.open(self.imagepath).resize((self.width,floor(self.width*fabs(self.model.ratio))))  
                )
            else:
                image = ImageTk.PhotoImage(master=self, image=Image.open(self.imagepath).resize((floor(self.height*fabs(self.model.ratio)),self.height)))

        self.create_image(self.width/2, self.height/2, image=image, anchor="center")
        self.image = image
    
    def ChangeModel(self, event):
        """Change visualization mode
        Gets selected function and param from the ModeSelectionPopup"""
        result = ModeSelectionPopup(self).GetChoice()
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
                
                # To get the dimensions of the base model (must have output the first one obviously)
                try:
                    basewidth ,baseheight = Image.open(NameFormat(config["Main_output"]["Name_format"],0)).size
                    self.baseratio = (basewidth/baseheight)
                except:
                    self.baseratio = 1
                # --
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


class VisualizationModel(object):  
    """The model that will be treated/displayed"""
    def __init__(self, function, param):
        """
        Args:
            function (str): The function to use from the R Script\n
            param (str): The parameter to use from the R Script
        """
        self.function = function
        self.param = param
        self.nameFormat = config["Main_output"]["Name_format"]
        self.imageExtension = config["Main_output"]["Image_extension"]
        self.actualModelOut = []
        self.name = self.function+"-"+self.param
        self.ratio = -1

    def GetFilenameAtStep(self, timeStep):
        """
        Returns:
            The filename at given step (int) as str
        """
        return NameFormat(self.nameFormat, timeStep)+self.imageExtension


class ModeSelectionPopup(object):
    """The class used for the popup window when clicking on a Canvas
    Args:
        parent (Widget): The widget used as the parent (should be the one invoking it)
    Note: 
        Have to define a parent to the toplevel so when the TopLevel gets destroyed
        the 'ModeSelectionPopup' object still keeps the data selected.
    """
    def __init__(self, parent):
        self.toplevel = Toplevel(parent)
        self.toplevel.title("Changing mode")
        self.toplevel.resizable(False,False)
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

        self.CreateListboxes()

        # Ok Button
        self.b = Button(self.bottomframe,
                        text="Base model", command=self.OnClickBase)
        self.b.grid(row=0, column=0, sticky=N+E+W+S)
        self.b = Button(self.bottomframe,
                        text="None", command=self.OnClickNone)
        self.b.grid(row=0, column=1, sticky=N+E+W+S)
        self.b = Button(self.bottomframe, text="Ok", command=self.OnClickOk)
        self.b.grid(row=1, column=0)

        # Cancel Button
        self.cancelbutton = Button(
            self.bottomframe, text="Cancel", command=self.OnClickCancel)
        self.cancelbutton.grid(row=1, column=1)

        self.toplevel.update_idletasks()
        self.toplevel.grab_set()
        # WIDGETS INIT -----------------------------------------

    def CreateListboxes(self):  # Pretty self explanatory
        """Simply creates the listboxes to select the function and parameter"""
        # Functions Listbox
        self.functionLb = Listbox(self.frame,exportselection=False)
        functions = visuconfig["functions"]
        functions.sort()

        # Inserts in listbox
        for i, function in enumerate(functions):
            self.functionLb.insert(i, function)
        # self.functionLb.bind("<<ListboxSelect>>", self.onlistbox1change)
        self.functionLb.grid(row=1, column=0)

        # Params Listbox
        self.paramsLb = Listbox(self.frame,exportselection=False)
        params = visuconfig["params"]
        params.sort()

        for j, param in enumerate(params):
            self.paramsLb.insert(j, param)
        # self.paramsLb.bind("<<ListboxSelect>>", self.onlistbox2change)
        self.paramsLb.grid(row=1, column=1)

    def OnClickCancel(self):  
        """When Cancel is clicked"""
        self.selection = ["", ""]
        self.toplevel.destroy()

    def OnClickNone(self):
        """When None is clicked"""
        self.selection = "none"
        self.toplevel.destroy()

    def OnClickBase(self):
        """When Base is clicked"""
        self.selection = "base"
        self.toplevel.destroy()

    def OnClickOk(self):
        """When Ok is clicked"""
        self.selection[0] = self.functionLb.get(ACTIVE)
        self.selection[1] = self.paramsLb.get(ACTIVE)
        self.toplevel.destroy()

    def GetChoice(self):
        """Returns the selected option"""
        self.toplevel.wait_window()
        return self.selection


class LaunchSimuPopup(object):
    """Popup window to start the simulation"""
    def __init__(self, parent, *args, **kwargs):
        self.toplevel = Toplevel(parent)
        self.toplevel.resizable(False, False)
        self.toplevel.minsize(width=282, height=100)
        self.toplevel.grab_set()
        self.toplevel.bind("WM_DELETE_WINDOW", self.OnClickCancel)
        self.toplevel.title("Start simulation")
        self.mainframe = Frame(self.toplevel)
        self.mainframe.pack(fill=BOTH)
        self.reg = re.compile(r"^(\w|\d)+$")
        self.valid = True
        self.clearVar = BooleanVar()
        self.selection = ["",False]
        self.textvar = StringVar()
        self.textvar.trace("w",lambda name, index, mode, var=self.textvar: self.OnType(var))
        self.entry = Entry(self.mainframe, textvariable=self.textvar)


        self.label = Label(self.mainframe, text="Name of the simulation\n (no spaces)")
        self.label.pack(side=TOP)
        self.entry.pack(fill=X,side=TOP)
        self.checkbox = Checkbutton(self.mainframe, text="Clear", onvalue=True, offvalue=False, variable=self.clearVar)
        self.checkbox.pack(side=TOP)

        self.entry.insert(0, "NewModel")

        self.buttonframe = Frame(self.mainframe)
        self.buttonframe.pack(side=BOTTOM)
        self.okbutton = Button(self.buttonframe, text="Ok", command=self.OnClickOk)
        self.okbutton.grid(row=0, column=0)

        self.cancelbutton = Button(self.buttonframe, text="Cancel", command=self.OnClickCancel)
        self.cancelbutton.grid(row=0, column=1)
    
    def OnClickOk(self):
        """When Ok is clicked"""
        if self.valid:
            self.selection[0] = self.textvar.get()
            self.selection[1] = self.clearVar.get()
            self.toplevel.destroy()
    
    def GetChoice(self):
        """Returns the text in the entry"""
        self.toplevel.wait_window()
        return self.selection

    def OnClickCancel(self):
        """When Cancel is clicked"""
        self.selection = ""
        self.toplevel.destroy()
    
    def OnType(self, var):
        """When typing in the Entry box"""
        if re.match(self.reg, var.get()):
            self.valid = True
            self.entry.config(bg="green")
        else:
            self.valid = False
            self.entry.config(bg="red")


class VisuWindow(Toplevel):  
    """The visualization window"""
    def __init__(self, *args, **kwargs):
        print("Creating visualization window")
        self.canvgridsize = kwargs["canvgridsize"]
        del kwargs["canvgridsize"] # If not deleted from the list causes errors with Tkinter
        Toplevel.__init__(self, *args, *kwargs)
        self.title("Visualization")
        self.width   = ScreenResolution[0]
        self.height  = ScreenResolution[1]
        self.maxsize(self.width, self.height)
        self.cb_checked = BooleanVar()
        self.cb_checked.set(False)
        self.ownedcanvas = []
        self.askedstop = False
        self.initwidgets()
        Oc.windows["Visu"] = self  # NAMING VISU WINDOW
        self.grab_set()
        thread = threading.Thread(target=ThreadTarget, daemon=True)
        Oc.threadings['Thread_Scan1'] = thread  # NAMING THREAD (ctrl+f s)
        thread.start()
        self.after(100, QueueCheck)

    def initwidgets(self):  
        """ Initializes widgets"""
        print("Creating widgets..")
        self.topframe       = Frame(self, bg="#6200EE")
        self.bottomframe    = Frame(self)
        self.initcanvas(self.canvgridsize)
        self.initplaystop()
        self.initrest()
        self.topframe.pack(side="top",fill="both", expand=True)
        self.bottomframe.pack(side="bottom", fill="x", expand=False)


    def initcanvas(self, canvasgrid):  
        """Initializes the visualization canvases"""
        print("Creating Canvas(es)..")
        
        try:  # try,except to catch any wrongly written size
            # Simple regex to process wanted canvasgrid
            dim = re.split(r"x|X", canvasgrid)
            i = int(dim[0])
            j = int(dim[1])
            k = 0  # to name the canvas
        except Exception as e:
            print(e, canvasgrid)
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




    def initplaystop(self):  
        """ Initializes the play/stop functionnality widgets"""
        self.playframe = Frame(self.bottomframe)
        self.playframe.grid(row=1, column=0, sticky="nesw")

        self.playbutton = Button(
            self.playframe, text="Play", command=self.play_anim)
        self.playbutton.grid(row=0, column=0)

        self.stopbutton = Button(
            self.playframe, text="Stop", command=self.stop_anim)
        self.stopbutton.grid(row=0, column=1)
        Oc.button_collection.add(self.stopbutton)
        
        Oc.button_collection.add(self.playbutton)

        self.textfrom = Label(self.playframe, text=" From:")
        self.textfrom.grid(row=0, column=2)

        self.entryfrom_text = StringVar()
        self.entryfrom = Entry(
            self.playframe,
            textvariable=self.entryfrom_text
        )
        self.entryfrom.grid(row=0, column=3)

        self.textto = Label(self.playframe, text=" To:")
        self.textto.grid(row=0, column=4)
        

        self.entryto_text = StringVar()
        self.entryto = Entry(
            self.playframe,
            textvariable=self.entryto_text
        )
        self.entryto.grid(row=0, column=5)

        self.textspeed = Label(self.playframe, text="Speed (ms)")
        self.textspeed.grid(row=0, column=6)
        self.entryspeed_text = StringVar()
        self.entryspeed = Entry(
            self.playframe,
            textvariable=self.entryspeed_text
        )
        self.entryspeed.insert(0,"100")
        
        self.entryspeed.grid(row=0, column=7)


    def initrest(self):
        """Initializes the rest of the widgets
        """
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
        self.toend_checkbox.grid(row=0, column=8)
        
        # Start simulation
        self.simubutton = Button(self.playframe, text="Start simulation", command=self.StartSimulation)
        self.simubutton.grid(row=0, column=9)
        
        # SCALE
        self.update()  # Update to be able to get the window size
        numberofpngs = Dm.getnumberofpng(img_folder_path, pngregex)

        # Bug fix (slider starting at -1 if no image found)
        if numberofpngs == -1:
            numberofpngs = 1
        self.slider = Scale(
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

    def StartSimulation(self):
        
        choice = LaunchSimuPopup(self).GetChoice()
        if type(choice) is str:
            return
        if choice[1]:
            choice[1] = "-clear"
        else:
            choice[1] = ""
        runcommand = "/bin/bash ./run.sh " + str(choice[1]) + " " + str(choice[0])
        subprocess.call(["x-terminal-emulator","-e", runcommand])
            
    def checkbox_get(self):
        """Gets the state of the checkbox
        Returns:
            (bool)
        """
        return self.cb_checked.get()

    def play_anim(self):
        """Initializes the animation process
        Input verifications"""
        self.toend_checkbox.configure(state=DISABLED)
        if self.cb_checked.get():
            self.toend_checkbox.toggle()
            self.cb_checked.set(False)

        self.askedstop = False
        _from = self.entryfrom_text.get()
        to = self.entryto_text.get()
        speed = self.entryspeed_text.get()

    
        if _from != "":
            try:
                self._from = int(_from)
            except Exception as e:
                print("From:",e)
                self._from = 0
        else:
            self._from = 0
        if to != "":
            try:
                self.to = int(to)
            except Exception as e:
                print("To:",e)
                self.to = 0
        else:
            self.to = self.slider.cget("to")
        if speed != "":
            try:
                self.speed = int(speed)
            except Exception as e:
                print("Speed:",e)
                self.speed = 100
                    
        
        # Parameters for the continue_anim method
        self.slider.set(self._from)
        self.playsliderpos = self._from
        self.continue_anim()

    def continue_anim(self):  
        """ Plays the animation
        Calls itself every x miliseconds and pushes the slider"""
        if self.playsliderpos > self.to or self.askedstop or self.playsliderpos > self.slider.cget("to"):
            self.slider.set(self._from)
            self.toend_checkbox.configure(state=NORMAL)
            return
        self.slider.set(self.playsliderpos)
        self.playsliderpos += 1
        self.after(self.speed, self.continue_anim)

    def stop_anim(self):
        """Called when clicking the stop button"""
        self.askedstop = True

    def OnSliderStep(self, num):
        """
        Whenever the slider gets moved
        param int num: the number the event passes (the slider's actual value)
        """
        num = int(num)
        for canvas in self.ownedcanvas:
            if canvas.model is not None:
                filename = canvas.model.GetFilenameAtStep(num)
                # For every previously owned models of this canvas
                if filename not in canvas.model.actualModelOut:
                    r[canvas.model.function](canvas.model.param, num)
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
                canvas.ChangeImage(NameFormat(name_format, num)+image_extension)


class MainWindow(Tk):
    """The Main window of the app"""
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, *kwargs)
        window_width = "500"  # 16/9
        window_height = "281"   #
        Oc.images["noimage"] = ImageTk.PhotoImage(master=self,image=Image.open("resources/selectamode.png").resize((canvaswidth,canvasheight),Image.ANTIALIAS))
        self.title("SpheroidViz - Visualization app")
        self.option_readfile("options")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        Oc.windows['Main'] = self  # NAMING MAIN WINDOW (ctrl+f)
        self.minsize(width=window_width, height=window_height)
        self.resizable(False,False)
        self.visuwindow = None
        self.validsize = True

        self.text = Label(self, text="SpheroidViz\nCreated by Benjamin.C")
        #self.text.grid(row=0, column=0,sticky="n")
        self.text.pack(side=BOTTOM, fill=X)
        self.var_regex = re.compile(r"^[1-9]+x[1-9]+$")

        self.canvasgrid_frame = Frame(self)
        self.canvasgrid_frame.pack(side=TOP)

        self.bouton = Button(self.canvasgrid_frame, text="Open Visualization Window",
                        command=self.createvisuwindow, background="#b3d9ff")
        self.bouton.pack(side=BOTTOM)
        # The Label 
        self.canvasgrid_text = Label(self.canvasgrid_frame, text="Enter grid dimensions:")
        self.canvasgrid_text.pack(side=TOP, fill=Y)

        # The StringVar where there is the input text
        self.canvasgrid_var = StringVar()
        self.canvasgrid_var.trace("w",lambda name, index, mode, var=self.canvasgrid_var: self.ontype(var))

        # The input box 
        self.canvasgrid_entry = Entry(self.canvasgrid_frame, textvariable=self.canvasgrid_var)
        self.canvasgrid_entry.pack()
        self.canvasgrid_entry.insert(0, config["config"]["Canvas_grid"])
        
    def ontype(self, var):
        """
        Veryfies if the size given is valid. Called when typing.
        """
        regmatch = self.var_regex.match(var.get())
        if regmatch:
            self.validsize = True
            self.canvasgrid_entry.config(bg="green")
        else:
            self.validsize = False
            self.canvasgrid_entry.config(bg="red")
            
    def createvisuwindow(self):
        """
        Called when the button in the main window is clicked.
        Creates the Visualization window if size is valid.
        """
        if self.validsize:
            self.visuwindow = VisuWindow(self, canvgridsize=self.canvasgrid_var.get())
            self.visuwindow.grab_set()
            self.visuwindow.wait_window()
            self.destroy()


def QueueCheck():
    """Method calls itself every second to check for instructions in the queue to execute"""
    try:
        value = scan_queue.get(block=False)
        value()
    except queue.Empty:
        Oc.windows['Visu'].after(400, QueueCheck)
        return
    Oc.windows['Visu'].after(400, QueueCheck)


def ThreadTarget():  
    """The Target of the second thread
    Method lists the directory containing the main svg files and launches the conversion
    if the directory contains more svg than the previous scan"""
    try:
        while True:
            Dm.svg_to_png(img_folder_path)
            scan_queue.put(SliderUpdate)
            time.sleep(1)
    except KeyboardInterrupt:
        print("ThreadTarget Keyboard interrupt")
    except Exception as e:
        print(e)
        thread = threading.Thread(target=ThreadTarget, daemon=True)
        thread.start()


def NameFormat(nameformat, num):
    """Processes the Name_Format in config to a complete name ex: test$$$ -> test025
    Args:
        nameformat (str): The string value of the name to format
        num (int): The value replacing the '$'s in nameformat
    """
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


def SliderUpdate(msg=""):  
    """Called to update the slider and change it's maximum
    Args:
        msg (str, optionnal): Used for debug purposes
    """
    visu_window = Oc.windows["Visu"]
    slider = Oc.sliders["Visu_Scale1"]
    if msg != "":
        print(msg)
    # Dm.svg_to_png(path=img_folder_path)
    numberofpngs = Dm.getnumberofpng(path=img_folder_path, reg=pngregex)
    slider.configure(to=numberofpngs-1)
    if visu_window.checkbox_get():  # To set at the end if the checkbox is ON
        slider.set(numberofpngs-1)




if __name__ == "__main__":

    monitors = screeninfo.get_monitors()
    
    global ScreenResolution
    ScreenResolution = (monitors[0].width,monitors[0].height)
    
    print("Screen Resolution is ", ScreenResolution)
    
    # Loads config.json
    print("Loading config.json...")
    global config
    global visuconfig
    config = json.load(open("config.json"))
    visuconfig = config["visu"]
    r = robjects.r
    try:
        r.source(config["r script source"])
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
    
    image_extension = config["Main_output"]["Image_extension"]
    name_format = config["Main_output"]["Name_format"]
    canvsize = config["config"]["Visualization_size"]
    canvaswidth = int(canvsize.split("x")[0])
    canvasheight= int(canvsize.split("x")[1])
    main_window = MainWindow()
    main_window.mainloop()