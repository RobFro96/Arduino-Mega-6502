"""Arduino-Mega-6502: Programmer and Debugger for 6502 Ben Eater inspired 8-bit Computer
by Robert Fromm, February 2021

Opens serial port selection window, connects to serial port
"""

import dataclasses
import tkinter

import serial
import serial.tools.list_ports

from myprint import myprint, myprint_error
from protocol import Protocol, ProtocolCommands
from serial_thread import SerialThread


@dataclasses.dataclass
class ConnectingResult:
    """Result of SerialActions.connect() function
    """
    success: bool
    serial_thread: SerialThread = None


def enable_dpi_awareness():
    """Enable tkinter DPI Awarness for better GUI scaling on windows
    """
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)


class SerialSelectWindow:
    """Window created with Tkinter to select serial port.
    """
    @dataclasses.dataclass
    class Result:
        """Result after closing the window
        """
        submitted: bool
        portname: str = None

    def __init__(self, args):
        """Constructor.

        Args:
            args: CLI arguments
        """
        self.args = args
        self.result = self.Result(False)
        self.__create_window()
        self.refresh_ports()

    def refresh_ports(self):
        """Refreshs the ports list and updates the GUI
        """
        self.port_names, self.port_descrs = SerialActions.get_ports()
        self.list_box.delete(0, "end")
        for port_descr in self.port_descrs:
            self.list_box.insert("end", port_descr)

    def __create_window(self):
        """Create the Window
        """
        # DPI awareness
        if not self.args.nodpi:
            enable_dpi_awareness()

        # Windows Title and Icon
        self.window = tkinter.Tk()
        self.window.title("Serial Port")
        self.window.iconbitmap("icon.ico")

        # Label and Listbox
        tkinter.Label(self.window, text="Select Serial Port",
                      anchor="w").pack(side="top", fill="x", pady=5)
        self.list_box = tkinter.Listbox(self.window, height=1, selectmode="single")
        self.list_box.pack(side="top", fill="both", expand=True, pady=5)

        # Buttons at the bottom
        control_frame = tkinter.Frame()
        control_frame.pack(side="bottom", fill="both", pady=5)

        tkinter.Button(control_frame, text="OK", command=self.__on_submit).pack(side="left", padx=5)
        tkinter.Button(control_frame, text="Refresh",
                       command=self.refresh_ports).pack(side="left", padx=5)
        tkinter.Button(control_frame, text="Cancel",
                       command=self.__on_cancel).pack(side="left", padx=5)

        self.list_box.bind('<Double-Button>', self.__on_submit)

        # Window size
        if self.args.nodpi:
            self.window.minsize(300, 200)
        else:
            self.window.minsize(450, 300)
        self.window.geometry("+300+300")

    def open(self):
        """Opens window and returns result if closed or serial port selected.

        Returns:
            Result: result
        """
        tkinter.mainloop()
        return self.result

    def __on_submit(self, *_):
        """On submitted pressed or double click on serial port
        """
        if len(self.list_box.curselection()) > 0:
            portname = self.port_names[self.list_box.curselection()[0]]
            self.result = self.Result(True, portname)
            self.window.destroy()
        else:
            self.refresh_ports()

    def __on_cancel(self):
        """On cancel button pressed
        """
        self.result = self.Result(False)
        self.window.destroy()


class SerialActions:
    """Opens serial port selection window, connects to serial port
    """
    @classmethod
    def get_ports(cls):
        """Get the serial ports connected to the PC

        Returns:
            list, list: list of names and descriptions
        """
        port_list = sorted(serial.tools.list_ports.comports())
        port_names = [port[0] for port in port_list]
        port_descrs = [port[1] for port in port_list]
        return port_names, port_descrs

    @classmethod
    def port_select(cls, args):
        """Opens the select port window or uses the port specified in the CLI arguments

        Args:
            args : CLI arguments

        Returns:
            str: portname or None
        """
        port_names, _ = cls.get_ports()

        if args.port in port_names:
            return args.port

        result = SerialSelectWindow(args).open()

        if result.submitted:
            return result.portname
        return None

    @classmethod
    def connecting(cls, portname: str, args):
        """Connects to the given portname, resets the Arduino, checks WhoIAm register

        Args:
            portname (str): portname
            args: CLI arguments

        Returns:
            ConnectingResult: result
        """
        myprint("Connecting to %s." % portname)

        # Opens serial thread
        try:
            serial_thread = SerialThread(portname, args)
            serial_thread.open()
        except serial.SerialException:
            myprint_error("\nCannot connect to serial port %s.\n" % portname)
            serial_thread.close()
            return ConnectingResult(False)

        myprint(".")

        # resets device
        if not serial_thread.wait_on_ready(5):
            myprint_error("\nDevice on serial port %s is not responding.\n" % portname)
            serial_thread.close()
            return ConnectingResult(False)

        myprint(".")

        # checks WhoIAm value
        result = serial_thread.do(ProtocolCommands.WHOIAM_VERSION, [], 2)
        if not result.success:
            myprint_error("\nDevice on serial port %s is not responding to message.\n" % portname)
            serial_thread.close()
            return ConnectingResult(False)

        if result.data[0] != Protocol.WHOIAM_BYTE:
            myprint_error("\nDevice sent wront WHOIAM byte: 0x%02X \n" % result.data[0])
            serial_thread.close()
            return ConnectingResult(False)

        myprint(". Firmware Version: %d\n" % result.data[1])
        return ConnectingResult(True, serial_thread)
