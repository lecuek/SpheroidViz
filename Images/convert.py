import PIL
from PIL import Image
import os
width = heigh = 300
path = os.path.realpath(__file__).strip("convert.py")
print(path)
files = os.listdir(path)
i = 0
for file in files:
    if (".jpg" in file) or (".png" in file) or (".jpeg" in file):
        img = Image.open(path+"/"+file)
        img = img.resize((width, heigh), PIL.Image.ANTIALIAS)
        img.save("canard"+str(i)+".jpg")
        i += 1