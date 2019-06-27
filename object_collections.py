class DictPlus(dict):
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
    windows = DictPlus("Window")
    sliders = DictPlus("Slider")
    canvases = DictPlus("Canvas")
    threadings = DictPlus("Thread")
    button_collection = DictPlus("Button")
    visualization_modes = DictPlus("Mode")
    checkboxes = DictPlus("Checkbox")
    textinputs = DictPlus("TextInput")
    images = DictPlus("image")

