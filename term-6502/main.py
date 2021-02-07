#!/usr/bin/python
# -*- coding: utf-8 -*-

import msvcrt
import os
import threading
import time

import coloredlogs

from assembly_actions import AssemblyActions
from bus_actions import BusActions
from help_actions import HelpActions
from myprint import myprint, myprint_warning
from py6502.dis6502 import dis6502
from serial_actions import SerialActions
from serial_thread import SerialThread


def kbfunc():
    return ord(msvcrt.getch()) if msvcrt.kbhit() else 0


# enable colored logs
coloredlogs.install()


class Main():
    def __init__(self):
        self.args = HelpActions.get_args()
        self.portname: str = None
        self.serial_thread: SerialThread = None
        self.assembly_file: str = None
        self.binary: list = None
        self.disasm: dis6502 = None
        self.stop_event = threading.Event()
        self.auto_single_step = False
        self.next_single_step_time = 0

    def run(self):
        # Select Portname
        self.portname = SerialActions.port_select(self.args)
        if self.portname is None:
            self.exit()
            return

        # Connect to serial port
        result = SerialActions.connecting(self.portname, self.args)
        if not result.success:
            self.exit_on_error()
            return
        self.serial_thread: SerialThread = result.serial_thread

        # Open Assembly File
        self.select_assembly()
        if self.assembly_file is None:
            self.exit()
            return

        HelpActions.print_help()

        try:
            while not self.stop_event.wait(1e-3) and self.serial_thread.is_connected():
                key = kbfunc()
                if key:
                    # ignore additional key presses
                    while kbfunc():
                        pass
                    self.on_key_pressed(key)

                BusActions.update(self.serial_thread, self.disasm)

                if self.auto_single_step and self.next_single_step_time < time.time():
                    BusActions.send_api_single_step(self.serial_thread)
                    self.next_single_step_time = time.time() + self.args.ass_delay

        except KeyboardInterrupt:
            pass

        if self.serial_thread.is_connected():
            self.exit()
        else:
            self.exit_on_error()

    def exit(self):
        self.stop_event.set()
        if self.serial_thread:
            self.serial_thread.close()

    def exit_on_error(self):
        self.exit()
        myprint("Press any key to exit...\n")
        msvcrt.getch()

    def select_assembly(self, force_dialog=False):
        new_file = AssemblyActions.select(self.args, force_dialog)
        if new_file:
            self.assembly_file = new_file
            myprint("Selected File: %s\n" % self.assembly_file)
            self.read_binary_and_update_disam()

    def is_file_binary(self):
        return os.path.splitext(self.assembly_file)[1] == ".bin"

    def read_binary_and_update_disam(self):
        result = AssemblyActions.read_bin_file(self.assembly_file)
        if result.success:
            self.binary = result.eeprom_content
            memory = [0]*0x8000 + self.binary
            self.disasm = dis6502(memory)
        return result.success

    def assemble(self, no_warning=False):
        if self.is_file_binary():
            if not no_warning:
                myprint_warning("Selected file is a binary.\n")
            return True
        success = AssemblyActions.assemble(self.assembly_file)

        if success:
            self.read_binary_and_update_disam()
        return success

    def program(self):
        self.auto_single_step = False
        AssemblyActions.flash(self.args, self.binary, self.serial_thread)

    def reset(self, force_autoreset=True):
        if not self.args.simplereset or force_autoreset:
            self.auto_single_step = False
            BusActions.send_api_auto_reset(self.serial_thread)
        else:
            BusActions.send_api_reset(self.serial_thread)

    def single_step(self):
        self.auto_single_step = False
        BusActions.send_api_single_step(self.serial_thread)

    def run_program(self):
        self.auto_single_step = False
        BusActions.send_api_run(self.serial_thread)
        myprint("Running program, no bus trace available!\n")

    def assemble_program_reset(self):
        self.auto_single_step = False
        success = self.assemble(no_warning=True)
        if not success:
            return
        self.program()
        self.reset(force_autoreset=True)

    def auto_single_step_toggle(self):
        self.auto_single_step = not self.auto_single_step

    def on_key_pressed(self, key):
        keymap = {
            "h": HelpActions.print_help,
            "q": self.stop_event.set,

            "o": lambda: self.select_assembly(True),
            "a": self.assemble,
            "p": self.program,

            "r": self.reset,
            "u": self.assemble_program_reset,

            "s": self.single_step,
            "t": self.auto_single_step_toggle,
            "x": self.run_program
        }

        if chr(key) in keymap:
            keymap[chr(key)]()


if __name__ == "__main__":
    Main().run()
