import tkinter

from util.image_button import ImageButton, ImageButtonType
from util.settings import Settings


class MemoryToolbarHandler:
    def on_save_clicked(self): pass
    def on_open_clicked(self): pass
    def on_upload_clicked(self): pass
    def on_download_clicked(self): pass
    def on_goto_pc_clicked(self): pass
    def on_goto_clicked(self, search_str: str): pass


class MemoryToolbar:
    def __init__(self, settings: Settings, handler: MemoryToolbarHandler):
        self.settings = settings
        self.handler = handler

        # Buttons
        self.open_btn: ImageButton
        self.save_btn: ImageButton
        self.upload_btn: ImageButton
        self.download_btn: ImageButton
        self.goto_pc_btn: ImageButton
        self.goto_button: ImageButton
        self.goto_entry_var: tkinter.StringVar
        self.goto_entry: tkinter.Entry

    def create_frame(self, master) -> tkinter.Frame:
        frame = tkinter.Frame(master)

        self.open_btn = ImageButton(frame, "icons/folder-open-solid.png",
                                    self.handler.on_open_clicked)
        self.open_btn.pack(side="left", padx=5)

        self.save_btn = ImageButton(frame, "icons/save-solid.png", self.handler.on_save_clicked)
        self.save_btn.pack(side="left", padx=5)

        self.upload_btn = ImageButton(frame, "icons/upload-solid.png",
                                      self.handler.on_upload_clicked)
        self.upload_btn.pack(side="left", padx=5)

        self.download_btn = ImageButton(
            frame, "icons/download-solid.png", self.handler.on_download_clicked)
        self.download_btn.pack(side="left", padx=5)

        self.goto_pc_btn = ImageButton(
            frame, "icons/flag-solid.png", self.handler.on_goto_pc_clicked)
        self.goto_pc_btn.pack(side="left", padx=5)

        self.goto_button = ImageButton(
            frame, "icons/search-solid.png", self.__on_goto_button_clicked)
        self.goto_button.pack(side="right", padx=5)

        self.goto_entry_var = tkinter.StringVar(value="0x8000")
        self.goto_entry = tkinter.Entry(frame, textvariable=self.goto_entry_var, width=8)
        self.goto_entry.pack(side="right", padx=5)
        self.goto_entry.bind("<Return>", lambda _: self.__on_goto_button_clicked())

        return frame

    def __on_goto_button_clicked(self):
        self.handler.on_goto_clicked(self.goto_entry_var.get())
