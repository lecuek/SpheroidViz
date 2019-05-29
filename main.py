import tkinter as tk
import sim_visu
import time
import CuekUtils
from object_collections import ObjectCollection


def windowPop():
    popup = sim_visu.CreateWindow()
    popup.update()


if __name__ == "__main__":
    window_min_width = "500"
    window_min_height = "281"

    main_window = tk.Tk()
    ObjectCollection.window_collection.append(main_window)
    main_window.minsize(width=window_min_width, height=window_min_height)

    texte = tk.Label(main_window, text="hélo waurld")
    texte.grid(row=0, column=0, sticky="n")
    bouton = tk.Button(main_window, text="Lancer la visualisation", command=windowPop)
    bouton.grid(row=1, column=0)
    main_window.mainloop()