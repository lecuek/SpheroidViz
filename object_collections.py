class DictPlus(dict):
    def __init__(self, _typename, *args, **kwargs):
        dict.__init__(self, *args, *kwargs)
        self.type = str(_typename)

    def add(self, _object):
        self[self.type+"_"+str(len(self))] = _object

class ObjectCollection:
    windows = DictPlus("Window")
    sliders = DictPlus("Slider")
    canvases = DictPlus("Canvas")
    threadings = DictPlus("Thread")
    button_collection = DictPlus("Button")
    visualization_modes = DictPlus("Mode")
    checkboxes = DictPlus("Checkbox")
    textinputs = DictPlus("TextInput")

