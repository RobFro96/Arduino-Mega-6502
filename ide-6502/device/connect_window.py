import tkinter
import tkinter.ttk

import serial.tools.list_ports
from util.scroll_text import ScrollText
from util.settings import Settings

from device.connect_thread import ConnectThread, ConnectThreadHandler
from device.serial_thread import SerialThread


class ConnectWindowHandler:
    def on_close(self): pass
    def on_connected(self, serial_thread: SerialThread, firmware_version: int): pass


class ConnectWindow(ConnectThreadHandler):
    def __init__(self, root: tkinter.Tk, settings: Settings, handler: ConnectWindowHandler):
        self.root = root
        self.settings = settings
        self.handler = handler

        self.window: tkinter.Toplevel
        self.connect_thread: ConnectThread

        self.__create_gui()
        self.update_com_list()

    def __create_gui(self):
        self.window = tkinter.Toplevel(self.root)
        self.window.title(self.settings.get_text("conwin_title"))
        self.window.iconbitmap(self.settings.get_icon_path())
        self.window.protocol('WM_DELETE_WINDOW', self.handler.on_close)
        self.window.after(1, self.window.focus_force)

        tkinter.Label(self.window, text=self.settings.get_text("conwin_select_com"),
                      font=(None, 9, "bold")).pack(side="top", pady=5)

        frame1 = tkinter.Frame(self.window)
        frame1.pack(side="top", fill="x", pady=5)

        self.com_combobox = tkinter.ttk.Combobox(frame1)
        self.com_combobox.pack(side="left", fill="x", expand=True, padx=5)

        self.refresh_btn = tkinter.Button(frame1, text=self.settings.get_text("conwin_refresh"),
                                          command=self.update_com_list)
        self.refresh_btn.pack(side="left", padx=5)

        self.connect_btn = tkinter.Button(frame1, text=self.settings.get_text("conwin_connect"),
                                          command=self.on_connect)
        self.connect_btn.pack(side="left", padx=5)

        self.scroll_text = ScrollText(self.window, (self.settings.get_terminal_font(), 9, "normal"))
        self.scroll_text.pack(side="top", fill="both", expand=True)
        self.scroll_text.tag_config("com_list_update", foreground="gray")
        self.scroll_text.tag_config("error", foreground="red")

        self.window.geometry(self.settings.get_connect_window_size())
        self.window.minsize(640, 480)

    def update_com_list(self):
        ports = sorted(serial.tools.list_ports.comports())

        port_descr = [port[1] for port in ports]
        self.port_names = [port[0] for port in ports]

        self.com_combobox["values"] = port_descr
        if len(port_descr) > 0:
            self.com_combobox.current(0)

        self.scroll_text.add_content(self.settings.get_text(
            "conwin_info_refreshed") % len(ports) + "\n", "com_list_update")

    def on_connect(self):
        port_id = self.com_combobox.current()

        if port_id < 0 or port_id >= len(self.port_names):
            return

        port = self.port_names[port_id]
        self.connect_to(port)

    def connect_to(self, port: str):
        self.connect_thread = ConnectThread(port, self.settings, self)
        self.connect_thread.start()

    def on_connection(self, success: bool, port: str):
        if success:
            self.scroll_text.add_content(self.settings.get_text(
                "conwin_info_connection") % port + "\n")
        else:
            self.scroll_text.add_content(self.settings.get_text(
                "conwin_error_connection") % port + "\n", "error")

    def on_response(self, success: bool, port: str):
        if success:
            self.scroll_text.add_content(self.settings.get_text(
                "conwin_info_response") % port + "\n")
        else:
            self.scroll_text.add_content(self.settings.get_text(
                "conwin_error_response") % port + "\n", "error")

    def on_whoiam_version(self, success: bool, port: str, firmware_version: int):
        if success:
            self.scroll_text.add_content(self.settings.get_text(
                "conwin_info_whoiam") % firmware_version + "\n")
            self.window.withdraw()
            self.handler.on_connected(
                self.connect_thread.get_serial_thread(), firmware_version)
        else:
            self.scroll_text.add_content(self.settings.get_text(
                "conwin_error_whoiam") + "\n", "error")
