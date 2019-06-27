class DictPlus(dict):
<<<<<<< HEAD
    """Extends the dictionnary class
    Args:
        _type (str): The type of the objects that will be contained in the dictionnary.
        Is used when .add() is called.
    """
    def __init__(self, _type, *args, **kwargs):
        dict.__init__(self, *args, *kwargs)
        self.type = str(_type)

    def add(self, _object):
        """Adds the object to the dict with a key like: 'type_X' X being the lenght of the dict
            _object (any): the object to add to the dict.
        """
        self[self.type+"_"+str(len(self))] = _object

class ObjectCollection:
    """Class containing the collections.
    """
=======
    def __init__(self, _typename, *args, **kwargs):
        dict.__init__(self, *args, *kwargs)
        self.type = str(_typename)

    def add(self, _object):
        self[self.type+"_"+str(len(self))] = _object

class ObjectCollection:
>>>>>>> e484a4fa87c0cc8dbf0503b82976fdd746251fda
    windows = DictPlus("Window")
    sliders = DictPlus("Slider")
    canvases = DictPlus("Canvas")
    threadings = DictPlus("Thread")
    button_collection = DictPlus("Button")
    visualization_modes = DictPlus("Mode")
    checkboxes = DictPlus("Checkbox")
    textinputs = DictPlus("TextInput")
    images = DictPlus("image")

