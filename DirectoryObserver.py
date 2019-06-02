from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import sys
import os
import json
import time
import logging
from tkinter import *
config = json.loads("config.json")
img_folder_path = os.path.realpath(__file__).replace(os.path.basename(__file__),config["Image_folder_name"])
def DirectoryObserver():
    # Code piqué directement de la documentation de Watchdog
    # https://pythonhosted.org/watchdog/quickstart.html#a-simple-example
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = Event()
    observer = Observer()
    observer.schedule(event_handler, img_folder_path, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()