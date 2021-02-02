import enum
import tkinter

from util.settings import Settings

from memory.memory_map import MemoryMap


class MemoryFillerRegion:
    RAM = "ram"
    EEPROM = "eeprom"


class MemoryFiller:

    def __init__(self, root: tkinter.Tk, settings: Settings, region: MemoryFillerRegion):
        self.root = root
        self.settings = settings
        self.region = region

        self.__create_gui()

    def __create_gui(self):
        t = self.settings.get_translation()
        self.window = tkinter.Toplevel(self.root)

        self.window.title(t["mfill_title_%s" % self.region])
        self.window.iconbitmap(self.settings.get_icon_path())
        self.window.protocol('WM_DELETE_WINDOW', self.on_close)

        tkinter.Label(self.window, text=t["mfill_from"]).grid(row=0, column=0, sticky="W")
        tkinter.Label(self.window, text=t["mfill_to"]).grid(row=1, column=0, sticky="W")
        tkinter.Label(self.window, text=t["mfill_value"]).grid(row=2, column=0, sticky="W")

        self.from_entry_var = tkinter.StringVar()
        self.to_entry_var = tkinter.StringVar()
        self.value_entry_var = tkinter.StringVar(value="0x00")

        if self.region == MemoryFillerRegion.RAM:
            self.from_entry_var.set("0x%04X" % MemoryMap.RAM_START)
            self.to_entry_var.set("0x%04X" % (MemoryMap.RAM_START + MemoryMap.RAM_SIZE - 1))
        else:
            self.from_entry_var.set("0x%04X" % MemoryMap.EEPROM_START)
            self.to_entry_var.set("0x%04X" % (MemoryMap.EEPROM_START + MemoryMap.EEPROM_SIZE - 1))

        tkinter.Entry(self.window, textvariable=self.from_entry_var).grid(
            row=0, column=1, sticky="EW")
        tkinter.Entry(self.window, textvariable=self.to_entry_var).grid(
            row=1, column=1, sticky="EW")
        tkinter.Entry(self.window, textvariable=self.value_entry_var).grid(
            row=2, column=1, sticky="EW")

    def on_close(self):
        self.window.withdraw()
