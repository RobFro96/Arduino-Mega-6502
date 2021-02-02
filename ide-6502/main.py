#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Arduino-6502: Hybrid Simulator and Debugger for 6502 CPUs
by Robert Fromm, November 2020

Main program. Main class to expand EventHandlers and connect GUI and functionality.
"""

import logging
import threading
import tkinter

import coloredlogs

from bus.bus_actions import BusActions, BusState
from bus.bus_menu import BusMenu, BusMenuHandler
from bus.bus_toolbar import BusToolbar, BusToolbarHandler
from bus.bus_tracer import BusTracer, BusTracerHandler
from device.connect_window import ConnectWindow, ConnectWindowHandler
from device.serial_thread import SerialThread
from memory.assembler_actions import AssemblerActions
from memory.memory_actions import MemoryActions
from memory.memory_browser import MemoryBrowser, MemoryBrowserHandler
from memory.memory_filler import MemoryFiller, MemoryFillerRegion
from memory.memory_map import MemoryMap
from memory.memory_toolbar import MemoryToolbar, MemoryToolbarHandler
from util.convertions import Convertions
from util.settings import Settings

# enable colored logs
coloredlogs.install(fmt='%(asctime)s,%(msecs)d %(levelname)-5s '
                    '[%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG)

SETTINGS_FILE = "settings.json"


class Main:
    def __init__(self):
        """Constructor. Initializing and starting GUI
        """
        # Load settings
        self.settings = Settings.from_file(SETTINGS_FILE)
        if self.settings is None:
            return

        # Initialize TKinter
        if self.settings.get_dpi_awareness():
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        self.root = tkinter.Tk()
        self.root.iconbitmap(self.settings.get_icon_path())
        self.root.withdraw()

        self.connect_window = ConnectWindow(
            self.root, self.settings, self.MyConnectWindowHandler(self))

        autoconnect_port = self.settings.get_autoconnect_port()
        if autoconnect_port:
            self.connect_window.connect_to(autoconnect_port)

        self.serial_thread: SerialThread
        self.bus_toolbar: BusToolbar
        self.bus_tracer: BusTracer
        self.bus_menu: BusMenu
        self.memory_map: MemoryMap
        self.memory_toolbar: MemoryToolbar
        self.memory_browser: MemoryBrowser
        self.assembly_filename: str = None
        self.run_event = threading.Event()

        logging.info("Started.")
        self.root.mainloop()

    def on_connected(self, serial_thread: SerialThread, firmware_version: int):
        self.serial_thread = serial_thread

        self.bus_toolbar = BusToolbar(self.settings, self.MyBusToolbarHandler(self))
        self.bus_tracer = BusTracer(self.root, self.settings,
                                    self.MyBusTracerHandler(self), self.bus_toolbar)
        self.bus_tracer.add_firmware_message(firmware_version)
        self.bus_menu = BusMenu(self.bus_tracer.window, self.settings, self.MyBusMenuHandler(self))

        self.memory_toolbar = MemoryToolbar(self.settings, self.MyMemoryToolbarHandler(self))
        self.memory_browser = MemoryBrowser(self.root, self.settings,
                                            self.MyMemoryBrowserHandler(self), self.memory_toolbar)
        self.memory_map = MemoryMap(self.memory_browser.get_treeview())
        self.memory_map.create_entries(*self.memory_browser.get_master_entries())
        self.memory_map.update()

        BusActions.do_pin_peek(self.serial_thread, self.bus_update)
        self.root.deiconify()

    def quit(self):
        self.serial_thread.close()
        self.root.quit()

    def single_step(self, force_reset=False, callback=None):
        gui_state = self.bus_menu.get_bus_gui_state()

        if force_reset:
            gui_state.reset = True

        def callback_with_update(bus_state: BusState):
            self.bus_update(bus_state)
            if callback is not None:
                callback()

        BusActions.do_single_step(self.serial_thread,
                                  lambda state: self.root.after(1, callback_with_update, state),
                                  gui_state)

    def bus_update(self, bus_state: BusState):
        self.bus_tracer.add_bus_state_line(bus_state)

        if bus_state.get_sync():
            entry = self.memory_map.set_pc_marker(bus_state.abus)
            self.memory_browser.set_last_pc_marker(entry)

        if not bus_state.get_rwb() and self.memory_map.ram.is_in_region(bus_state.abus):
            # write to RAM
            self.memory_map.memory[bus_state.abus] = bus_state.dbus
            self.memory_map.update(True, False, False)

    def auto_reset(self):
        def step(n=0):
            if n < 9:
                self.single_step(False, lambda: step(n+1))

        self.single_step(True, step)

    def goto_in_memory_browser(self, search_str: str):
        addr = Convertions.string_to_int_auto_base(search_str)
        if addr is not None:
            item = self.memory_map.get_entry(addr)
            if item is not None:
                self.memory_browser.goto_item(item)

    def save_memory(self):
        t = self.settings.get_translation()
        result = MemoryActions.save(self.memory_map)
        if result is not None:
            self.bus_tracer.add_line("btracer_save_mem", result)
        else:
            tkinter.messagebox.showerror(t["save_mem_failed_title"], t["save_mem_failed"])

    def open_memory(self):
        t = self.settings.get_translation()
        self.root.update()
        result = MemoryActions.open(self.memory_map)
        if result is not None:
            self.bus_tracer.add_line("btracer_load_mem", result)

            def update():
                self.memory_map.update()
                self.memory_map.set_all_italic()
            self.root.after(100, update)
        else:
            tkinter.messagebox.showerror(t["load_mem_failed_title"], t["load_mem_failed"])

    def upload_memory(self):
        MemoryActions.upload(self.serial_thread, self.memory_map)
        self.bus_tracer.add_line("btracer_upload_mem")

    def download_memory(self):
        MemoryActions.download(self.serial_thread, self.memory_map)
        self.bus_tracer.add_line("btracer_download_mem")

    def open_assembly(self, ask_filename=True):
        if ask_filename:
            self.assembly_filename = AssemblerActions.open_asm()

        success, result = AssemblerActions.assemble(
            self.settings, self.assembly_filename, self.memory_map)

        self.bus_tracer.add_assembly_lines(success, self.assembly_filename, result)

    def auto_assemble(self):
        self.open_assembly(self.assembly_filename is None)
        self.upload_memory()
        self.auto_reset()

    def play_or_stop(self, play):
        if play:
            self.run_event.clear()

            def step():
                if not self.run_event.is_set():
                    self.single_step(False, step)
            step()
        else:
            self.run_event.set()

    class MyHandler:
        def __init__(self, main: "Main"):
            self.main = main

    class MyConnectWindowHandler(MyHandler, ConnectWindowHandler):
        def on_close(self):
            self.main.root.quit()

        def on_connected(self, serial_thread: SerialThread, firmware_version: int):
            self.main.on_connected(serial_thread, firmware_version)

    class MyBusTracerHandler(MyHandler, BusTracerHandler):
        def on_closed(self):
            self.main.quit()

    class MyBusToolbarHandler(MyHandler, BusToolbarHandler):
        def on_reset_clicked(self):
            self.main.single_step(True)

        def on_auto_reset_clicked(self):
            self.main.auto_reset()

        def on_auto_assemble(self):
            self.main.auto_assemble()

        def on_step_clicked(self):
            self.main.single_step()

        def on_play_changed(self, is_active: bool):
            self.main.play_or_stop(not is_active)

        def on_show_memory_browser_clicked(self):
            self.main.memory_browser.show()

    class MyMemoryBrowserHandler(MyHandler, MemoryBrowserHandler):
        def on_key_pressed(self, addr: int, digit: int):
            self.main.memory_map.change_memory_address_by_keypress(addr, digit)

    class MyBusMenuHandler(MyHandler, BusMenuHandler):
        def on_open_memory_map(self):
            self.main.open_memory()

        def on_save_memory_map(self):
            self.main.save_memory()

        def on_open_assembly(self):
            self.main.open_assembly()

        def on_automatic_assembly_update_changed(self, state: bool): pass

        def on_exit(self):
            self.main.quit()

        def on_reset_changed(self, state: bool):
            pass

        def on_single_step(self):
            self.main.single_step()

        def on_show_memory_browser(self):
            self.main.memory_browser.show()

        def on_fill_ram(self):
            MemoryFiller(self.main.root, self.main.settings, MemoryFillerRegion.RAM)

        def on_fill_eeprom(self):
            pass

        def on_upload_memory(self):
            self.main.upload_memory()

        def on_download_memory(self):
            self.main.download_memory()

    class MyMemoryToolbarHandler(MyHandler, MemoryToolbarHandler):
        def on_save_clicked(self):
            self.main.save_memory()

        def on_open_clicked(self):
            self.main.open_memory()

        def on_upload_clicked(self):
            self.main.upload_memory()

        def on_download_clicked(self):
            self.main.download_memory()

        def on_goto_pc_clicked(self):
            self.main.memory_browser.goto_last_pc_marker()

        def on_goto_clicked(self, search_str: str):
            self.main.goto_in_memory_browser(search_str)


if __name__ == "__main__":
    Main()
