import tkinter as tk
import sim_visu
window_min_width = "500"
window_min_height = "281"
window_collection = []

main_window = tk.Tk()
window_collection.append(main_window)
main_window.minsize(width=window_min_width, height=window_min_height)


def windowPop():
    popup = sim_visu.popup()
    window_collection.append(popup)
    popup.mainloop()


bouton = tk.Button(main_window, text="Lancer la visualisation", command=windowPop, anchor="w")
bouton.pack()
main_window.mainloop()