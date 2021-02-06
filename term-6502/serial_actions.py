import dataclasses
import tkinter

import serial
import serial.tools.list_ports

import util
from myprint import Color, myprint, myprint_error
from protocol import Protocol, ProtocolCommands
from serial_thread import SerialThread


@dataclasses.dataclass
class ConnectingResult:
    success: bool
    serial_thread: SerialThread = None


class SerialSelectWindow:
    @dataclasses.dataclass
    class Result:
        submitted: bool
        portname: str = None

    def __init__(self, args):
        self.args = args
        self.result = self.Result(False)
        self.__create_window()
        self.refresh_ports()

    def refresh_ports(self):
        self.port_names, self.port_descrs = SerialActions.get_ports()
        self.list_box.delete(0, "end")
        for port_descr in self.port_descrs:
            self.list_box.insert("end", port_descr)

    def __create_window(self):
        if not self.args.nodpi:
            util.enable_dpi_awareness()

        self.window = tkinter.Tk()
        self.window.title("Serial Port")
        self.window.iconbitmap("icon.ico")

        tkinter.Label(self.window, text="Select Serial Port",
                      anchor="w").pack(side="top", fill="x", pady=5)
        self.list_box = tkinter.Listbox(self.window, height=1, selectmode="single")
        self.list_box.pack(side="top", fill="both", expand=True, pady=5)

        control_frame = tkinter.Frame()
        control_frame.pack(side="bottom", fill="both", pady=5)

        tkinter.Button(control_frame, text="OK", command=self.__on_submit).pack(side="left", padx=5)
        tkinter.Button(control_frame, text="Refresh",
                       command=self.refresh_ports).pack(side="left", padx=5)
        tkinter.Button(control_frame, text="Cancel",
                       command=self.__on_cancel).pack(side="left", padx=5)

        self.list_box.bind('<Double-Button>', self.__on_submit)

        if self.args.nodpi:
            self.window.minsize(300, 200)
        else:
            self.window.minsize(450, 300)
        self.window.geometry("+300+300")

    def open(self):
        tkinter.mainloop()
        return self.result

    def __on_submit(self, *_):
        if len(self.list_box.curselection()) > 0:
            portname = self.port_names[self.list_box.curselection()[0]]
            self.result = self.Result(True, portname)
            self.window.destroy()
        else:
            self.refresh_ports()

    def __on_cancel(self):
        self.result = self.Result(False)
        self.window.destroy()


class SerialActions:
    @classmethod
    def get_ports(cls):
        port_list = sorted(serial.tools.list_ports.comports())
        port_names = [port[0] for port in port_list]
        port_descrs = [port[1] for port in port_list]
        return port_names, port_descrs

    @classmethod
    def port_select(cls, args):
        port_names, _ = cls.get_ports()

        if args.port in port_names:
            return args.port

        result = SerialSelectWindow(args).open()

        if result.submitted:
            return result.portname
        return None

    @classmethod
    def connecting(cls, portname: str, args):
        myprint("Connecting to ")
        myprint(portname, Color.BOLD)
        myprint(".")

        try:
            serial_thread = SerialThread(portname, args)
            serial_thread.open()
        except serial.SerialException:
            myprint_error("\nCannot connect to serial port %s.\n" % portname)
            serial_thread.close()
            return ConnectingResult(False)

        myprint(".")

        if not serial_thread.wait_on_ready(5):
            myprint_error("\nDevice on serial port %s is not responding.\n" % portname)
            serial_thread.close()
            return ConnectingResult(False)

        myprint(".")

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
