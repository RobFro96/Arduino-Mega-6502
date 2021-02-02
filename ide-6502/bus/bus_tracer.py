
import enum
import tkinter

from util.scroll_text import ScrollText
from util.settings import Settings

from bus.bus_actions import BusState
from bus.bus_toolbar import BusToolbar


class BusTracerHandler:
    def on_closed(self): pass


class BusTracerLineType(enum.Enum):
    BUS = 1
    INFO = 2


class BusTracer:
    def __init__(self, root: tkinter.Tk, settings: Settings, handler: BusTracerHandler,
                 toolbar: BusToolbar):
        self.root = root
        self.settings = settings
        self.handler = handler
        self.toolbar = toolbar

        self.last_line_type = None

        self.__create_gui()

    def __create_gui(self):
        self.window = self.root
        self.window.title(self.settings.get_text("btracer_title"))
        self.window.iconbitmap(self.settings.get_icon_path())
        self.window.protocol('WM_DELETE_WINDOW', self.handler.on_closed)
        self.window.after(1, self.window.focus_force)

        frame = self.toolbar.create_frame(self.window)
        frame.pack(side="top", fill="x", pady=5)

        self.scroll_text = ScrollText(self.window, (self.settings.get_terminal_font(), 9, "normal"))
        self.scroll_text.pack(side="top", fill="both", expand=True)

        self.scroll_text.tag_config("bold", font=(self.settings.get_terminal_font(), 9, "bold"))
        self.scroll_text.tag_config("gray", foreground="gray")

        self.window.geometry(self.settings.get_bus_tracer_window_size())
        self.window.minsize(800, 600)

    def add_firmware_message(self, version: int):
        self.scroll_text.add_content(
            self.settings.get_text("btracer_firmware_version") % version + "\n")
        self.add_seperator(BusTracerLineType.INFO)

    def add_bus_state_line(self, state: BusState):
        tag = "bold" if state.get_sync() else ""
        rwb = "R" if state.get_rwb() else "w"
        signals = ", ".join(state.get_signal_list())

        self.add_seperator(BusTracerLineType.BUS)
        self.scroll_text.add_content(
            self.settings.get_text("btracer_bus_state") % (
                state.abus,
                rwb,
                state.dbus
            ), tag)
        self.scroll_text.add_content(signals + "\n", "gray")

    def add_assembly_lines(self, success, filename: str, result):
        self.add_seperator(BusTracerLineType.INFO)

        if success:
            self.scroll_text.add_content(self.settings.get_text("asm_load_text") % filename + "\n")
        else:
            self.scroll_text.add_content(self.settings.get_text(
                "asm_load_failed") % filename + "\n")

        for line in result:
            self.scroll_text.add_content(line + "\n", "gray")

    def add_seperator(self, my_type: BusTracerLineType):
        if self.last_line_type is None:
            self.last_line_type = my_type

        if self.last_line_type != my_type:
            self.scroll_text.add_content("\n")
            self.last_line_type = my_type

    def add_line(self, translation_key: str, format_keys=None):
        format_keys = format_keys or []

        self.add_seperator(BusTracerLineType.INFO)
        self.scroll_text.add_content(self.settings.get_text(
            translation_key) % format_keys + "\n")
