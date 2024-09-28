#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "xTwitter Bot Manager.ui"
RESOURCE_PATHS = [PROJECT_PATH]


class TkGUIUI:
    def __init__(self, master=None):
        self.builder = pygubu.Builder()
        self.builder.add_resource_paths(RESOURCE_PATHS)
        self.builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow: tk.Tk = self.builder.get_object("root", master)
        self.builder.connect_callbacks(self)
        self.max_chars = 0

    def run(self):
        self.mainwindow.mainloop()

    def make_post(self, event=None):
        pass


if __name__ == "__main__":
    app = TkGUIUI()
    app.run()
