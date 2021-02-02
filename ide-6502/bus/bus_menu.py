import threading
import tkinter
import tkinter.messagebox
import tkinter.simpledialog

from util.convertions import Convertions
from util.settings import Settings

from bus.bus_actions import BusGuiState


class BusMenuHandler:
    def on_open_memory_map(self): pass
    def on_save_memory_map(self): pass
    def on_open_assembly(self): pass
    def on_automatic_assembly_update_changed(self, state: bool): pass
    def on_exit(self): pass
    def on_reset_changed(self, state: bool): pass
    def on_single_step(self): pass
    def on_show_memory_browser(self): pass
    def on_fill_ram(self): pass
    def on_fill_eeprom(self): pass
    def on_upload_memory(self): pass
    def on_download_memory(self): pass


class BusMenu:
    DBUS_FIXED_MENU = 3

    def __init__(self, window: tkinter.Toplevel, settings: Settings, handler: BusMenuHandler):
        self.window = window
        self.settings = settings
        self.handler = handler

        self.fixed_dbus_value = 0xEA

        self.__create()

    def __create(self):
        t = self.settings.get_translation()

        self.menu = tkinter.Menu(self.window)
        self.window.config(menu=self.menu)

        # File Menu
        self.file_menu = tkinter.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label=t["bmenu_file"], menu=self.file_menu, underline=0)

        self.file_menu.add_command(label=t["bmenu_open_mm"],
                                   command=self.handler.on_open_memory_map)
        self.file_menu.add_command(label=t["bmenu_save_mm"],
                                   command=self.handler.on_save_memory_map)
        self.file_menu.add_separator()

        self.file_menu.add_command(label=t["bmenu_open_asm"],
                                   command=self.handler.on_open_assembly)
        self.autoupdate_asm_var = tkinter.BooleanVar(value=True)
        self.file_menu.add_checkbutton(label=t["bmenu_autoupdate_asm"],
                                       variable=self.autoupdate_asm_var,
                                       command=self.__on_autoupdate_asm_changed)

        self.file_menu.add_separator()
        self.file_menu.add_command(label=t["bmenu_exit"], command=self.handler.on_exit)

        # Device Menu
        self.device_menu = tkinter.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label=t["bmenu_device"], menu=self.device_menu, underline=0)

        self.reset_var = tkinter.BooleanVar(value=False)
        self.device_menu.add_checkbutton(label=t["bmenu_reset"], variable=self.reset_var,
                                         command=self.__on_reset_changed)

        self.nmi_var = tkinter.BooleanVar(value=False)
        self.device_menu.add_checkbutton(label=t["bmenu_nmi"], variable=self.nmi_var)

        self.irq_var = tkinter.BooleanVar(value=False)
        self.device_menu.add_checkbutton(label=t["bmenu_irq"], variable=self.irq_var)

        self.fix_dbus_var = tkinter.BooleanVar(value=False)
        self.device_menu.add_checkbutton(variable=self.fix_dbus_var)
        self.__update_fixed_dbus_value(self.fixed_dbus_value)

        self.device_menu.add_command(
            label=t["bmenu_change_dbus_value"], command=self.__on_change_dbus_clicked)

        self.device_menu.add_separator()
        self.device_menu.add_command(label=t["bmenu_single_step"],
                                     command=self.handler.on_single_step)

        # Memory
        self.memory_menu = tkinter.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label=t["bmenu_memory"], menu=self.memory_menu, underline=0)

        self.memory_menu.add_command(
            label=t["bmenu_show_membrow"], command=self.handler.on_show_memory_browser)
        self.memory_menu.add_separator()
        self.memory_menu.add_command(
            label=t["bmenu_fill_ram"], command=self.handler.on_fill_ram)
        self.memory_menu.add_command(
            label=t["bmenu_fill_eeprom"], command=self.handler.on_fill_eeprom)
        self.memory_menu.add_separator()
        self.memory_menu.add_command(
            label=t["bmenu_upload"], command=self.handler.on_upload_memory)
        self.memory_menu.add_command(
            label=t["bmenu_download"], command=self.handler.on_download_memory)

    def __on_autoupdate_asm_changed(self):
        self.handler.on_automatic_assembly_update_changed(self.autoupdate_asm_var.get())

    def __on_reset_changed(self):
        self.handler.on_reset_changed(self.reset_var.get())

    def __update_fixed_dbus_value(self, value: int):
        self.fixed_dbus_value = value
        self.device_menu.entryconfigure(
            self.DBUS_FIXED_MENU, label=self.settings.get_text("bmenu_dbus_fixed") % value)

    def __on_change_dbus_clicked(self):
        t = self.settings.get_translation()
        answer = tkinter.simpledialog.askstring(
            t["change_dbus_value_title"], t["change_dbus_value_text"], parent=self.window,
            initialvalue="0x%02X" % self.fixed_dbus_value)

        number = Convertions.string_to_int_auto_base(answer)

        if number is None or number < 0 or number > 255:
            self.__on_change_dbus_clicked()
        else:
            self.__update_fixed_dbus_value(number)

    def get_bus_gui_state(self):
        return BusGuiState(
            reset=self.reset_var.get(),
            nmi=self.nmi_var.get(),
            irq=self.irq_var.get(),
            is_dbus_fixed=self.fix_dbus_var.get(),
            dbus_value=self.fixed_dbus_value
        )
