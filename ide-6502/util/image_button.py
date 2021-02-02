import enum
import tkinter


class ImageButtonType(enum.Enum):
    NORMAL = 1
    TOGGLEABLE = 2


class ImageButton:
    def __init__(self, master, image_file, command, text="", btn_type=ImageButtonType.NORMAL):
        self.image = tkinter.PhotoImage(file=image_file)
        self.btn_type = btn_type
        self.command = command
        self.button = tkinter.Button(master, text=text, image=self.image,
                                     compound="left", relief="flat")

        # storing image in button is stopping the carbage collector
        self.button.image = self.image

        if self.btn_type == ImageButtonType.NORMAL:
            self.button.config(command=command)
        else:
            self.button.bind("<Button-1>", self.__on_clicked)

        self.is_active = True

    def pack(self, *args, **kwargs):
        self.button.pack(*args, **kwargs)

    def grid(self, *args, **kwargs):
        self.button.grid(*args, **kwargs)

    def __on_clicked(self, _):
        self.set_active(not self.is_active)
        self.command(self.is_active)

    def set_active(self, value: bool):
        self.is_active = value
        self.button.config(state="normal" if value else "disabled")

    def get_active(self) -> bool:
        return self.is_active
