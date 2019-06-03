import cairosvg
import os
import PIL
from PIL import Image


class DataManagement():
    def svg_to_png(self, path, delete=False,outputheight=200,outputwidth=200):

        '''
        Takes a svg file or an entire directory of svg files and 
        converts it to a png and deletes the svg if told to
        :param str path: The path and name of the file path/name.svg
        :param bool delete: If it should delete the source or not, default False
        '''
        if ".svg" not in path:
            files = os.listdir(path)
            for file in files:
                
                if ".svg" not in file:
                    continue  # Reminder: Continue instead of Break bc it completely kills the loop and stops
                else:
                    if file.replace(".svg", ".png") not in files:  # If not already converted
                        print(file.replace(".svg", ".png"), "doesn't exist")
                        print("converting", file)
                        cairosvg.svg2png(
                            url=str(path+"/"+file), scale=0.5,
                            write_to=str(path+"/"+file).replace("svg", "png")
                        )
                if delete:
                    print("deleting", file)
                    os.unlink(path+"/"+file)
        else:
            cairosvg.svg2png(url=path, write_to=str(path).replace("svg", "png"))
            if delete:
                os.unlink(path)

<<<<<<< HEAD
    def getnumberofpng(self, path):  # Returns the number of png files in specified directory
=======
    def getnumberofpng(path):
>>>>>>> dev
        files = os.listdir(path)
        pngfiles = 0
        for file in files:
            if ".png" in file:
                pngfiles += 1
        return pngfiles
        
<<<<<<< HEAD
    def to_png(self): # ??? forgot but keeping it here jic
=======
    def to_png():
>>>>>>> dev
        width = heigh = 300
        path = os.path.realpath(__file__).strip("convert.py")
        print(path)
        files = os.listdir(path)
        i = 0
        for file in files:
            if (".jpg" in file) or (".png" in file) or (".jpeg" in file):
                img = Image.open(path+"/"+file)
                img = img.resize((width, heigh), PIL.Image.ANTIALIAS)
                img.save("canard"+str(i)+".png")
                i += 1
