import tkinter as tk


class ErrorDialogUI(tk.Tk):
    def __init__(self, error_message: str = None, master=None, **kw):
        super().__init__(master, **kw)

        self.error_message = tk.Message(self, name="error_message")
        self.error_message.configure(
            background="#a91651",
            cursor="arrow",
            font="TkHeadingFont",
            foreground="#fffcff",
            justify="center",
            relief="flat",
            takefocus=False,
            text=error_message or "Something went wrong, please try again or contact developer",
            width=500)
        self.error_message.place(anchor="center", relx=0.5, rely=0.45, x=0, y=0)

        self.exit_window_btn = tk.Button(self, name="exit_window_btn")
        self.exit_window_btn.configure(
            compound="center",
            cursor="arrow",
            state="active",
            command=self.destroy,
            font="TkDefaultFont",
            foreground="#000000",
            background="#fffcff",
            takefocus=True,
            text='OK',
            width=35)
        self.exit_window_btn.place(
            anchor="center",
            height=30,
            relx=0.5,
            rely=0.75,
            x=0,
            y=0)

        self.configure(
            background="#a91651",
            height=250,
            takefocus=False,
            width=500)
        self.resizable(False, False)
        self.pack_propagate(False)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.mainloop()
