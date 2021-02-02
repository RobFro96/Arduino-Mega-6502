import dataclasses
import logging
import tkinter
import tkinter.ttk

from util.settings import Settings

from memory.memory_toolbar import MemoryToolbar


@dataclasses.dataclass
class DBusFixState:
    is_fixed: bool
    dbus_value: int


class MemoryBrowserHandler:
    def on_key_pressed(self, addr: int, digit: int): pass


class MemoryBrowser:
    def __init__(self, root: tkinter.Tk, settings: Settings, handler: MemoryBrowserHandler,
                 toolbar: MemoryToolbar):
        self.root = root
        self.settings = settings
        self.handler = handler
        self.toolbar = toolbar

        self.last_pc_marker = None

        self.__create_gui()
        self.__config_treeview()
        self.window.geometry(self.settings.get_connect_window_size())
        self.window.minsize(400, 600)

    def __create_gui(self):
        self.window = tkinter.Toplevel(self.root)
        self.window.title(self.settings.get_text("membrow_title"))
        self.window.iconbitmap(self.settings.get_icon_path())
        self.window.protocol('WM_DELETE_WINDOW', self.on_close)
        self.window.withdraw()

        frame = self.toolbar.create_frame(self.window)
        frame.pack(side="top", fill="x", pady=5)

    def __config_treeview(self):
        if self.settings.get_dpi_awareness():
            tkinter.ttk.Style().configure("Treeview", rowheight=25)

        frame2 = tkinter.Frame(self.window)
        frame2.pack(side="top", fill="both", expand=True)
        frame2.grid_propagate(0)
        frame2.grid_rowconfigure(0, weight=1)
        frame2.grid_columnconfigure(0, weight=1)

        self.treeview = tkinter.ttk.Treeview(frame2, columns=("value", "disasm"),
                                             selectmode="browse")
        self.treeview.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = tkinter.ttk.Scrollbar(frame2, command=self.treeview.yview)
        self.scrollbar.grid(row=0, column=1, sticky="nsew")
        self.treeview["yscrollcommand"] = self.scrollbar.set

        self.treeview.heading("#0", text=self.settings.get_text("membrow_tv_address"))
        self.treeview.heading("value", text=self.settings.get_text("membrow_tv_value"))
        self.treeview.heading("disasm", text=self.settings.get_text("membrow_tv_disasm"))
        self.treeview.column("#0", width=50)
        self.treeview.column("value", width=50)

        self.treeview.tag_configure("bold", font=(None, 9, "bold"))
        self.treeview.tag_configure("terminal", font=(
            self.settings.get_terminal_font(), 9, "normal"))
        self.treeview.tag_configure("terminal_italic", font=(
            self.settings.get_terminal_font(), 9, "italic"))
        self.treeview.tag_configure("terminal_bold", font=(
            self.settings.get_terminal_font(), 9, "bold"))

        self.treeview_ram = self.treeview.insert(
            "", "end", text=self.settings.get_text("membrow_tv_ram"), values=("", ""), tag="bold")
        self.treeview_eeprom = self.treeview.insert(
            "", "end", text=self.settings.get_text("membrow_tv_eeprom"), values=("", ""), tag="bold")
        self.treeview_rvector = self.treeview.insert(
            "", "end", text=self.settings.get_text("membrow_tv_rvector"), values=("", ""), tag="bold")

        self.treeview.bind("<KeyPress>", self.on_treeview_keydown)

    def get_treeview(self) -> tkinter.ttk.Treeview:
        return self.treeview

    def get_master_entries(self):
        return [self.treeview_ram, self.treeview_eeprom, self.treeview_rvector]

    def show(self):
        self.window.deiconify()
        self.window.geometry(self.settings.get_connect_window_size() + "+%d+%d" %
                             (self.root.winfo_x() + self.root.winfo_width(), self.root.winfo_y()))

    def on_close(self):
        self.window.withdraw()

    def on_treeview_keydown(self, e):
        item_id = self.treeview.focus()
        try:
            addr = int(self.treeview.item(item_id)["text"], 16)
        except ValueError:
            return

        converter_map = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
                         "9": 9, "a": 10, "A": 10, "b": 11, "B": 11, "c": 12, "C": 12, "d": 13,
                         "D": 13, "e": 14, "E": 14, "f": 15, "F": 15}

        if not e.char in converter_map:
            return

        self.handler.on_key_pressed(addr, converter_map[e.char])

    def set_last_pc_marker(self, last_pc_marker):
        self.last_pc_marker = last_pc_marker

    def goto_last_pc_marker(self):
        if self.last_pc_marker is not None:
            self.treeview.see(self.last_pc_marker)

    def goto_item(self, item):
        self.treeview.see(item)
