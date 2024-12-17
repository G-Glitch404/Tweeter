import json
import time
import threading
import tkinter as tk

from tkinter import ttk
from tkinter import font

from GUI.error_dialog import ErrorDialogUI
from util.reddit_recon import recon
from util.database import Database
from util.utils import path, fingerprint, add_new_bot, remove_bot, get_available_bots, status_manager
from settings import settings
from logger.logger import Logger

logger = Logger('GUI_APP')


class PlaceholderEntry(ttk.Entry):
    def __init__(self, *args, placeholder=None, **kwargs):
        """ a new Entry widget with a placeholder """
        super().__init__(*args, **kwargs)

        self.placeholder_color: str = "#8f8f8f"
        self.placeholder = placeholder
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.insert(0, self.placeholder)
        self.configure(foreground=self.placeholder_color)
        self.bind("<Button-1>", self.clear_placeholder)

    def get(self):
        if super().get() == self.placeholder:
            return ""
        return super().get()

    def __default_get(self):
        return super().get()

    def on_focus_in(self, *args):
        if self.__default_get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(foreground="black")

    def on_focus_out(self, *args):
        if self.__default_get() == "":
            self.insert(0, self.placeholder)
            self.configure(foreground=self.placeholder_color)

    def set_placeholder(self, *args):
        if self.__default_get() == "":
            self.insert(0, self.placeholder)
            self.configure(foreground=self.placeholder_color)

    def clear_placeholder(self, *args):
        if self.__default_get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(foreground="black")


class AutomatorApp(tk.Tk):
    def __init__(self):
        super(AutomatorApp, self).__init__()
        self.resizable(False, False)
        self.title("Automated xTwitter Accounts manager")
        self.geometry("485x820")

        self.status_labels: list[ttk.Label] = []
        self.stop: tuple = ('', False)
        self.active_bots: list[str] = []

        # fonts and styles
        self.font_title: font.Font = font.Font(family="Cairo", size=18, weight="bold")
        self.font_default: font.Font = font.Font(family="Cairo", size=16)
        self.font_hello: font.Font = font.Font(family="Cairo", size=10)
        self.placeholder_font: font.Font = font.Font(family="Cairo", size=14)
        self.messages_font: font.Font = font.Font(family="Cairo", size=10, weight="bold")

        # color templates
        self.text_color: str = '#f0e1e7'
        self.button_bg: str = '#2C2F33'
        self.button_hover: str = '#40444B'
        self.input_bg: str = '#2C2F33'
        self.bg_color: str = "#0c0936"

        # style configurations
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', background=self.button_bg, foreground=self.text_color, font=self.font_default, padding=10, relief='flat', borderwidth=5)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color, font=self.font_default)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.map('TButton', background=[('active', self.button_hover), ('!active', self.button_bg)])

        # create background canvas with a solid dark blue color
        self.canvas = tk.Canvas(self, width=480, height=800, highlightthickness=0, bg=self.bg_color)
        self.canvas.pack(fill='both', expand=True)

        # main frame for buttons and labels
        self.main_frame = ttk.Frame(self.canvas, style='TFrame', padding=10)
        self.canvas.create_window(240, 400, window=self.main_frame)

        # initial window setup
        self.clear_posts_status()
        self.create_main_window()

    def add_title_footer(self):
        ttk.Label(self.main_frame, text=f"Hello, Mr. {settings['USER_NAME']}", font=self.font_hello).grid(row=5, column=0, columnspan=2, pady=(50, 5))
        ttk.Label(self.main_frame, text="Made By Yousif Wael (Glitch_404)", font=self.font_hello).grid(row=6, column=0, columnspan=2)

    def create_main_window(self):
        """ main widget window when app is first opened """
        self.clear_frame()

        ttk.Label(self.main_frame, text="Reddit To xTwitter v1.0 Alpha", font=self.font_title).grid(row=0, column=0, columnspan=2, pady=(10, 20))

        status_frame = ttk.Frame(self.main_frame)
        button_frame = ttk.Frame(self.main_frame)

        status_frame.grid(row=1, column=0, columnspan=2, pady=(10, 40))
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        # status frame
        labels: tuple[str, ...] = ("Active", "Bots count", "Scheduled", "Uploaded", "Failed", "Total")
        labels_status: list[str] = status_manager(checking=True)
        for _id, label in enumerate(zip(labels, labels_status)):
            if label[0] == "Active": label = (label[0], len(self.active_bots))
            if label[0] == "Bots count": label = (label[0], len(get_available_bots()))

            lbl = ttk.Label(status_frame, text=f"{label[0]}: {label[1]}", font=self.font_default)
            lbl.grid(row=_id, column=0, sticky='w', padx=10, pady=5)
            self.status_labels.append(lbl)

        # buttons frame
        ttk.Button(button_frame, text="Manual Scheduling", style='TButton', command=self.open_insert_window).pack(pady=5, fill='x', padx=10)
        ttk.Button(button_frame, text="Auto Reddit to Twitter", style='TButton', command=self.start_auto_work).pack(pady=5, fill='x', padx=10)
        ttk.Button(button_frame, text="Active Bots", style='TButton', command=self.list_active_bots).pack(pady=5, fill='x', padx=10)

        self.add_title_footer()  # recreate title and footer

    def open_insert_window(self):
        """ Widget Window from clicking "Manual Scheduling" button """
        self.clear_frame()

        ttk.Label(self.main_frame, text="Schedule Post", font=self.font_title).grid(row=0, column=0, columnspan=2, pady=40)

        input_frame = ttk.Frame(self.main_frame)
        input_frame.grid(row=1, column=0, columnspan=2, pady=10)

        labels: tuple[str, ...] = ("type", "body", "date", "media path", "username")
        inputs = []

        for _id, label in enumerate(labels):
            ttk.Label(input_frame, text=f"{label}: ".capitalize(), font=self.font_default).grid(row=_id, column=0, sticky='e', padx=5, pady=5)

            match label:
                case "type": placeholder = "e.g. (text, image, video)"
                case "body": placeholder = "Post text"
                case "date": placeholder = "e.g. 2022-01-01 23:21:00"
                case "media path": placeholder = "e.g. media/test.jpg"
                case "username": placeholder = "bot username"
                case _: placeholder = label

            entry = PlaceholderEntry(input_frame, font=self.placeholder_font, placeholder=placeholder)
            entry.grid(row=_id, column=1, padx=10, pady=10, sticky='we')
            inputs.append(entry)

        input_frame.columnconfigure(1, weight=1)

        submit_btn = ttk.Button(
            self.main_frame,
            text="Insert Post",
            style='TButton',
            command=lambda: self.insert_post(tuple(input_.get() for input_ in inputs))
        )
        submit_btn.grid(row=2, column=0, columnspan=2, pady=10, sticky='ew', padx=20)

        back_btn = ttk.Button(self.main_frame, text="Back", style='TButton', command=self.create_main_window)
        back_btn.grid(row=3, column=0, columnspan=2, pady=10, sticky='ew', padx=20)

        self.add_title_footer()  # recreate title and footer

    def stop_auto_work(self, bot_username: str):
        if bot_username not in self.active_bots:
            self.show_message(f'Bot {bot_username} is not Active', 'red', self.messages_font)
            return

        index = self.active_bots.index(bot_username)
        self.active_bots.pop(index)
        self.stop = (bot_username, True)
        self.show_message(f'Deactivated bot username: {bot_username}', 'green', self.messages_font)

    def start_auto_work(self):
        """ Widget Window from clicking "Auto Reddit to Twitter" button """
        def bot_username_entry():
            return inputs[0].get()

        def submit_btn_normal_state():
            submit_btn['text'] = 'Start'
            submit_btn['command'] = self.start_auto_work

        def start(bot_username: str):
            if not bot_username: return

            if bot_username in self.active_bots:  # stop command
                self.stop_auto_work(bot_username)
                self.show_message(f'Stopped bot username: {bot_username}', 'green', self.messages_font)
                remove_active(bot_username)
                return

            subreddits: list[str] = []
            try:
                for bot in get_available_bots():
                    username, info = next(iter(bot.items()))
                    if username != bot_username: continue
                    subreddits: list = subreddit.split(',') if (subreddit := info['subreddit']) and isinstance(subreddit, str) else []
                    break
                else:
                    ErrorDialogUI(f'bot username "{bot_username}" was not found try re-creating it')

            except IndexError:
                ErrorDialogUI(f"can't start auto-run bot username: '{bot_username}' does not exist"); return

            except (AttributeError, KeyError) as e:
                ErrorDialogUI(f"Known error happened try to delete and recreate the bot if not fixed contact developer. Error message: '{e}' "); return

            else:
                if not subreddits:
                    ErrorDialogUI(f"can't start auto-run for bot username: '{bot_username}' No assigned subreddits on creation please re-create the bot"); return
                self.active_bots.append(bot_username_entry())

            finally:
                submit_btn_normal_state()

            submit_btn['text']: str = 'Stop/Start'
            username: str = bot_username_entry()
            stop_bot: bool = False

            self.show_message(f'Started bot username: "{bot_username}" successfully.', 'green', self.messages_font)
            while not stop_bot:
                process = recon(subreddits, username)
                if not process.is_alive(): stop_bot: bool = True; break

                start_time: float = time.perf_counter()
                while time.perf_counter() - start_time <= (60 * 60):  # scan the subreddit every 1 hour
                    time.sleep(0.5)
                    if self.stop[-1] and self.stop[0] == username:
                        stop_bot: bool = True; break

            if stop_bot:    # works as a fail-safe
                submit_btn_normal_state()
                try: remove_active(username)
                except ValueError: pass
                ErrorDialogUI(f"bot username: '{username}' was stopped probably by an error please re-create the bot or check the logs for more details if you don't know what's happening just contact the developer")
                self.show_message(f'bot username: {username} was stopped', 'orange', self.messages_font)
                return

            remove_active(username)  # just a fail-safe

        def load_bots_state():
            with open(path('config', 'last_checkpoint.json'), 'r') as file:
                for bot in json.load(file):
                    self.thread(start, bot)

        def remove_bot_(bot_username: str):
            if bot_username in self.active_bots:
                self.stop_auto_work(bot_username)

            remove_bot(bot_username)
            self.show_message(f'Deleted bot username: {bot_username} Successfully', 'green', self.messages_font)

        remove_active = lambda username: self.active_bots.pop(self.active_bots.index(username))

        self.clear_frame()
        ttk.Label(self.main_frame, text="Create/Start Bot", font=self.font_title).grid(row=0, column=0, columnspan=2, pady=25)

        load_export_frame = ttk.Frame(self.main_frame)
        input_frame: ttk.Frame = ttk.Frame(self.main_frame)
        btns_frame: ttk.Frame = ttk.Frame(self.main_frame)

        input_frame.grid(row=1, column=0, columnspan=2, pady=15)
        load_export_frame.grid(row=2, column=0, columnspan=2, pady=5)
        btns_frame.grid(row=3, column=0, columnspan=2)

        labels: tuple[str, ...] = ("username", "subreddit/s", "API key", "API secret", "access token", "access secret")
        inputs: list[PlaceholderEntry] = []

        # inputs frame
        for _id, label in enumerate(labels):
            ttk.Label(input_frame, text=f"{label}: ".capitalize(), font=self.font_default).grid(row=_id, column=0, sticky='e', padx=5, pady=5)

            match label:
                case "username": placeholder = "enter X bot username"
                case "subreddit/s": placeholder = "subreddit/s for auto-work"
                case "API key": placeholder = "enter X consumer key"
                case "API secret": placeholder = "enter X consumer secret"
                case "access token": placeholder = "enter X access token"
                case "access secret": placeholder = "enter X access secret"
                case _: placeholder = label

            entry = PlaceholderEntry(input_frame, font=self.placeholder_font, placeholder=placeholder)
            entry.grid(row=_id, column=1, padx=5, pady=5, sticky='we')
            inputs.append(entry)

        # load and export buttons frame
        ttk.Button(load_export_frame, text="Load", style='TButton', command=load_bots_state, width=9).grid(row=0, column=0, padx=2, sticky='w')
        ttk.Button(load_export_frame, text="Save", style='TButton', command=self.save_bots_state, width=9).grid(row=0, column=1, padx=2, sticky='e')

        # buttons frame
        create_bot = ttk.Button(btns_frame, text="Create New Bot", style='TButton', command=lambda: self.thread(self.create_new_bot, {k: v for k, v in zip(labels, inputs)}))
        remove_btn = ttk.Button(btns_frame, text="Remove Bot", style='TButton', command=lambda: self.thread(remove_bot_, bot_username_entry()))
        back_btn = ttk.Button(btns_frame, text="Back", style='TButton', command=self.create_main_window)
        submit_btn = ttk.Button(btns_frame, text="Start", style='TButton', command=lambda: self.thread(start, bot_username_entry()))

        for _id, btn in enumerate((create_bot, remove_btn, submit_btn, back_btn)):
            btn.grid(row=_id, column=0, columnspan=2, pady=5, sticky='ew', padx=10, ipadx=60)

        self.add_title_footer()  # recreate title and footer

    def list_active_bots(self):
        """ a widget to list all the currently active working bots """
        def stop_auto_work(username: str):
            self.stop_auto_work(username)
            self.list_active_bots()

        self.clear_frame()
        ttk.Label(self.main_frame, text="Active Bots", font=self.font_title).grid(row=0, column=0, columnspan=2, pady=40)

        active_bots_frame: ttk.Frame = ttk.Frame(self.main_frame)
        active_bots_frame.grid(row=1, column=0, columnspan=2, pady=15)

        if len(self.active_bots) > 0:
            for _id, bot_username in enumerate(self.active_bots):
                ttk.Label(active_bots_frame, text=f"{_id + 1}. {bot_username}", font=self.font_default).grid(row=_id, column=0, pady=5)
                ttk.Button(active_bots_frame, text="Stop", style='TButton', command=lambda: self.thread(stop_auto_work, bot_username)).grid(row=_id, column=1, pady=5, ipadx=10, padx=5)
        else:
            ttk.Label(active_bots_frame, text="No Active Bots Found", font=self.font_default, foreground="red").grid(row=1, column=0, columnspan=2, pady=25)

        ttk.Button(active_bots_frame, text="Back", style='TButton', command=self.create_main_window).grid(row=len(self.active_bots), column=0, columnspan=2, pady=10, ipadx=65)
        self.add_title_footer()

    def show_message(self, text: str, foreground_color: str, font_obj: font.Font = None):
        error_label: ttk.Label = ttk.Label(self.main_frame, text=text, font=font_obj, foreground=foreground_color)
        error_label.grid(row=4, column=0, columnspan=2, pady=15)
        time.sleep(2)
        error_label.destroy()

    def save_bots_state(self):
        with open(path('config', 'last_checkpoint.json'), 'w') as file:
            json.dump(self.active_bots, file, ensure_ascii=False, indent=2)

    def create_new_bot(self, entries: dict[str, ...]):
        entries_text: list = []
        blacklisted_chars: list[str] = ["\n", "@", 'r/', 'r\\', '/', '\\']
        for k, v in entries.items():
            entry_text: str = str(v.get())
            for char in blacklisted_chars:
                entry_text: str = entry_text.replace(char, '')
            entry_text = entry_text.strip()

            if not entry_text and k != 'subreddit/s':
                self.thread(self.show_message, 'Please fill all keys entries', 'red', self.messages_font)
                return
            if k == 'subreddit/s':
                entry_text: list = entry_text.split(',')

            entries_text.append(entry_text)

        add_new_bot(*entries_text)
        self.thread(self.show_message, f'Bot {entries_text[0]} Created Successfully', 'green', self.messages_font)

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def clear_posts_status(self):
        status_manager(checking=True, scheduled=0, uploaded=0, failed=0, total=0)
        self.create_main_window()

    @staticmethod
    def insert_post(inputs: tuple):
        database = Database(settings["POSTS_DATABASE"])
        inputs: tuple = tuple(list(inputs) + [fingerprint(inputs)])

        logger.info(f"inserting schedule: {inputs}")
        database.insert_post(inputs)
        status_manager(False, scheduled=1, total=1)

    @staticmethod
    def thread(func, *args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs).start()


if __name__ == "__main__":
    app = AutomatorApp()
    app.mainloop()
