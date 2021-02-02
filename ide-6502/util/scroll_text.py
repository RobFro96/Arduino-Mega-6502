import tkinter


class ScrollText:
    def __init__(self, master, font, wrap="word"):
        self.frame = tkinter.Frame(master)
        self.frame.grid_propagate(0)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.textfield = tkinter.Text(self.frame, font=font, wrap=wrap)
        self.textfield.grid(row=0, column=0, sticky="nsew")
        self.textfield.config(state="disabled")

        self.scrollbar = tkinter.ttk.Scrollbar(self.frame, command=self.textfield.yview)
        self.scrollbar.grid(row=0, column=1, sticky="nsew")
        self.textfield["yscrollcommand"] = self.scrollbar.set

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def tag_config(self, *args, **kwargs):
        self.textfield.tag_config(*args, **kwargs)

    def add_content(self, *args, **kwargs):
        self.textfield.config(state="normal")
        self.textfield.insert("end", *args, **kwargs)
        self.textfield.config(state="disabled")
        self.textfield.see("end")
