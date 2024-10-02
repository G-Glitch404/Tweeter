import time
import threading
import tkinter as tk

from tkinter import ttk
from tkinter import font

from util.reddit_recon import recon
from util.database import Database
from util.utils import fingerprint
from settings import settings
from logger.logger import Logger

logger = Logger('GUI_APP')


class PlaceholderEntry(ttk.Entry):
    def __init__(self, *args, placeholder=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder_color: str = "#8f8f8f"
        self.placeholder = placeholder
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.insert(0, self.placeholder)
        self.configure(foreground=self.placeholder_color)
        self.bind("<Button-1>", self.clear_placeholder)

    def on_focus_in(self, *args):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(foreground="black")

    def on_focus_out(self, *args):
        if self.get() == "":
            self.insert(0, self.placeholder)
            self.configure(foreground=self.placeholder_color)

    def clear_placeholder(self, *args):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(foreground="black")


class AutomatorApp(tk.Tk):
    def __init__(self):
        super(AutomatorApp, self).__init__()
        self.resizable(False, False)
        self.title("Automated xTwitter Accounts manager")
        self.geometry("480x800")

        self.status_labels = []
        self.stop_auto_work = False

        # Fonts and styles
        self.font_title: font.Font = font.Font(family="Cairo", size=18, weight="bold")
        self.font_default: font.Font = font.Font(family="Cairo", size=16)
        self.font_hello: font.Font = font.Font(family="Cairo", size=10)
        self.placeholder_font: font.Font = font.Font(family="Cairo", size=14)

        # Color settings
        self.text_color: str = '#f0e1e7'
        self.button_bg: str = '#2C2F33'
        self.button_hover: str = '#40444B'
        self.input_bg: str = '#2C2F33'
        self.bg_color: str = "#0c0936"

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', background=self.button_bg, foreground=self.text_color, font=self.font_default, padding=10, relief='flat', borderwidth=5)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color, font=self.font_default)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.map('TButton', background=[('active', self.button_hover), ('!active', self.button_bg)])

        # Create background canvas with a solid dark blue color
        self.canvas = tk.Canvas(self, width=480, height=800, highlightthickness=0, bg=self.bg_color)
        self.canvas.pack(fill='both', expand=True)

        # Main frame for buttons and labels
        self.main_frame = ttk.Frame(self.canvas, style='TFrame', padding=10)
        self.canvas.create_window(240, 400, window=self.main_frame)

        # Initial window setup
        self.create_main_window()
        self.database_status()

    def create_main_window(self):
        self.clear_frame()

        # Title label
        ttk.Label(self.main_frame, text="Reddit To xTwitter v1.0 Beta", font=self.font_title).grid(row=0, column=0, columnspan=2, pady=(10, 20))

        # Status labels
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=1, column=0, columnspan=2, pady=(20, 40))

        for i in range(6):
            lbl = ttk.Label(status_frame, text=f"Status {i + 1}: Idle", font=self.font_default)
            lbl.grid(row=i, column=0, sticky='w', padx=10, pady=5)
            self.status_labels.append(lbl)

        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Manual Scheduling", style='TButton', command=self.open_insert_window).pack(pady=10, fill='x', padx=10)
        ttk.Button(button_frame, text="Auto Reddit to Twitter", style='TButton', command=self.start_auto_work).pack(pady=10, fill='x', padx=10)

        # Add title and footer labels to every window
        self.add_title_footer()

    def add_title_footer(self):
        ttk.Label(self.main_frame, text="Hello, Mr. Glitch_404", font=self.font_hello).grid(row=4, column=0, columnspan=2, pady=(50, 10))
        ttk.Label(self.main_frame, text="Made By Yousif Wael (Glitch_404)", font=self.font_hello).grid(row=5, column=0, columnspan=2)

    def open_insert_window(self):
        self.clear_frame()

        ttk.Label(self.main_frame, text="Schedule Post", font=self.font_title).grid(row=0, column=0, columnspan=2, pady=40)

        input_frame = ttk.Frame(self.main_frame)
        input_frame.grid(row=1, column=0, columnspan=2, pady=10)

        labels = ["Type", "Body", "Date", "media path", "username"]
        inputs = []

        for i, label in enumerate(labels):
            lbl = ttk.Label(input_frame, text=f"{label}:", font=self.font_default)
            lbl.grid(row=i, column=0, sticky='e', padx=5, pady=5)

            match label:
                case "Type": placeholder = "e.g. (text, image, video)"
                case "Body": placeholder = "Post text"
                case "Date": placeholder = "e.g. 2022-01-01 23:21:00"
                case "media path": placeholder = "e.g. media/test.jpg"
                case "username": placeholder = "bot username"
                case _: placeholder = label

            entry = PlaceholderEntry(input_frame, font=self.placeholder_font, placeholder=placeholder)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky='we')
            inputs.append(entry)

        input_frame.columnconfigure(1, weight=1)

        submit_btn = ttk.Button(self.main_frame, text="Insert Post", style='TButton', command=lambda: self.insert_post(inputs))
        submit_btn.grid(row=2, column=0, columnspan=2, pady=10, sticky='ew', padx=20)

        back_btn = ttk.Button(self.main_frame, text="Back", style='TButton', command=self.create_main_window)
        back_btn.grid(row=3, column=0, columnspan=2, pady=10, sticky='ew', padx=20)

        # Recreate title and footer
        self.add_title_footer()

    @staticmethod
    def insert_post(inputs: list):
        database = Database(settings["POSTS_DATABASE"])
        inputs: tuple = tuple(inputs + [fingerprint(tuple(inputs))])
        database.insert_post(inputs)

    def start_auto_work(self):
        while not self.stop_auto_work:
            for subreddit_ in settings['RECON_SUBREDDITS']:
                recon(subreddit_, 'NewDayNewComic')
            time.sleep(60 * 60)

    def database_status(self):
        raise NotImplementedError("Not implemented yet")

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = AutomatorApp()
    app.mainloop()
