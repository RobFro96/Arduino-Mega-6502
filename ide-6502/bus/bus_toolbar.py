import tkinter

from util.image_button import ImageButton, ImageButtonType
from util.settings import Settings


class BusToolbarHandler:
    def on_reset_clicked(self): pass
    def on_auto_reset_clicked(self): pass
    def on_auto_assemble(self): pass
    def on_step_clicked(self): pass
    def on_play_changed(self, is_active: bool): pass
    def on_show_memory_browser_clicked(self): pass


class BusToolbar:
    def __init__(self, settings: Settings, handler: BusToolbarHandler):
        self.settings = settings
        self.handler = handler

    def create_frame(self, master) -> tkinter.Frame:
        frame = tkinter.Frame(master)

        ImageButton(frame, "icons/undo-solid.png",
                    self.handler.on_reset_clicked).pack(side="left", padx=5)

        ImageButton(frame, "icons/undo-solid_step.png",
                    self.handler.on_auto_reset_clicked).pack(side="left", padx=5)

        ImageButton(frame, "icons/file-download-solid_play.png",
                    self.handler.on_auto_assemble).pack(side="left", padx=5)

        ImageButton(frame, "icons/step-forward-solid.png",
                    self.handler.on_step_clicked).pack(side="left", padx=5)

        ImageButton(frame, "icons/play-solid.png", self.handler.on_play_changed,
                    btn_type=ImageButtonType.TOGGLEABLE).pack(side="left", padx=5)

        ImageButton(frame, "icons/database-solid.png",
                    self.handler.on_show_memory_browser_clicked).pack(side="right", padx=5)

        return frame
