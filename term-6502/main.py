#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import logging
import msvcrt
import threading

import coloredlogs

from assembly_actions import AssemblyActions
from help_actions import HelpActions
from myprint import Color, myprint
from serial_actions import SerialActions
from serial_thread import SerialThread


def kbfunc():
    return ord(msvcrt.getch()) if msvcrt.kbhit() else 0


# enable colored logs
coloredlogs.install(fmt='%(asctime)s,%(msecs)d %(levelname)-5s '
                    '[%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG)


class Main():
    def __init__(self):
        self.args = self.get_args()
        self.portname: str = None
        self.serial_thread: SerialThread = None
        self.assembly_file: str = None
        self.stop_event = threading.Event()

    def run(self):
        self.portname = SerialActions.port_select(self.args)

        if self.portname is None:
            self.exit()
            return

        result = SerialActions.connecting(self.portname, self.args)

        if not result.success:
            self.exit_on_error()
        self.serial_thread: SerialThread = result.serial_thread

        self.assembly_file = AssemblyActions.select(self.args)
        if not self.assembly_file:
            self.exit()
            return
        myprint("Selected File: %s\n" % self.assembly_file)

        HelpActions.print_help()

        try:
            while not self.stop_event.wait(1e-3):
                key = kbfunc()
                if key:
                    self.on_key_pressed(key)

        except KeyboardInterrupt:
            pass

        self.exit()

    def exit(self):
        self.stop_event.set()
        if self.serial_thread:
            self.serial_thread.close()

    def exit_on_error(self):
        self.exit()
        myprint("Press any key to exit...\n")
        input()

    def get_args(self):
        parser = argparse.ArgumentParser(
            description="TERM-6502\nArduino Mega 6502 Support")
        parser.add_argument("-p", "--port", type=str, action="store", help="serial port of device")
        parser.add_argument("-b", "--baud", type=int, action="store", default=115200,
                            help="baud rate of serial port")
        parser.add_argument("-f", "--file", type=str, action="store", help="assembly file to load")
        parser.add_argument("-d", "--nodpi", action="store_true",
                            help="disable DPI awareness")
        return parser.parse_args()

    def select_assembly(self, force_dialog=False):
        new_file = AssemblyActions.select(self.args, force_dialog)
        if new_file:
            self.assembly_file = new_file
        myprint("Selected File: %s\n" % self.assembly_file)

    def on_key_pressed(self, key):
        if key == ord("h"):
            HelpActions.print_help()
        elif key == ord("q"):
            self.exit()
        elif key == ord("o"):
            self.select_assembly(True)


if __name__ == "__main__":
    Main().run()
