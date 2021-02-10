#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Arduino-Mega-6502: Programmer and Debugger for 6502 Ben Eater inspired 8-bit Computer
by Robert Fromm, February 2021

Main program.
"""


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
    """Keypress detection. Works only on windows
    source: https://stackoverflow.com/questions/292095/polling-the-keyboard-detect-a-keypress-in-python

    Returns:
        int: key code or 0 if no key was pressed
    """
    return ord(msvcrt.getch()) if msvcrt.kbhit() else 0


# enable colored logs to ensure the colors are rendered correctly on consoles
# (e.g. Git Bash, Windows CMD)
coloredlogs.install()


class Main():
    """Main Function
    """

    def __init__(self):
        """Constructor.
        Defines the properties.
        """
        self.args = HelpActions.get_args()  # CLI arguments
        self.portname: str = None   # Name of serial port connected to
        self.serial_thread: SerialThread = None  # SerialThread of serial port
        self.assembly_file: str = None  # Assembly or binary file name
        self.binary: list = None  # Binary content (0x8000 to 0xFFFF) of current file
        self.disasm: dis6502 = None  # Py6502 Dissambler object for Opcode line interpretation
        self.stop_event = threading.Event()  # Stop event
        self.auto_single_step = False  # True, if autostepping is active
        self.next_single_step_time = 0  # Next timestamp (time.time()) an auto-step has to be made

    def run(self):
        """Starts the Program.
        """
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

        # Print Help
        HelpActions.print_help()

        # Main Loop
        try:
            while not self.stop_event.wait(1e-3) and self.serial_thread.is_connected():
                key = kbfunc()
                if key:
                    # ignore additional key presses
                    while kbfunc():
                        pass
                    self.on_key_pressed(key)

                BusActions.update(self.serial_thread, self.disasm)

                # Auto stepping
                if self.auto_single_step and self.next_single_step_time < time.time():
                    BusActions.send_api_single_step(self.serial_thread)
                    self.next_single_step_time = time.time() + self.args.ass_delay

        except KeyboardInterrupt:
            pass

        # Exiting
        if self.serial_thread.is_connected():
            self.exit()
        else:
            self.exit_on_error()

    def exit(self):
        """Stopps the program
        """
        self.stop_event.set()
        if self.serial_thread:
            self.serial_thread.close()

    def exit_on_error(self):
        """Steps the program (calls self.exit()).
        Additionaly prints "Press any key to exit..." and waits on keypress.
        Ensures the error message can be read before the console closes.
        """
        self.exit()
        myprint("Press any key to exit...\n")
        msvcrt.getch()

    def select_assembly(self, force_dialog=False):
        """Opens the file open dialog to select the assembly or binary file.
        If force_dialog is not set the file defines by the args is used, if exists.

        Args:
            force_dialog (bool, optional): Defaults to False.
        """
        new_file = AssemblyActions.select(self.args, force_dialog)
        if new_file:
            self.assembly_file = new_file
            myprint("Selected File: %s\n" % self.assembly_file)
            self.read_binary_and_update_disam()

    def is_file_binary(self):
        """Checks if file is a binary or an assembly file by the file extention.

        Returns:
            bool: True of binary file
        """
        return os.path.splitext(self.assembly_file)[1] == ".bin"

    def read_binary_and_update_disam(self):
        """Reads the corresponding binary file and updates the Disassmbler object

        Returns:
            bool: True if reading was successfull
        """
        result = AssemblyActions.read_bin_file(self.assembly_file)
        if result.success:
            self.binary = result.eeprom_content

            # EEPROM is second half of memory, starting at 0x8000.
            memory = [0]*0x8000 + self.binary
            self.disasm = dis6502(memory)
        return result.success

    def assemble(self, no_warning=False):
        """Runs the assembler on the selected file.

        Args:
            no_warning (bool, optional): Disable the warning of selected file is a binary.
                Defaults to False.

        Returns:
            bool: True, if assembly was successfull
        """
        if self.is_file_binary():
            if not no_warning:
                myprint_warning("Selected file is a binary.\n")
            return True
        success = AssemblyActions.assemble(self.assembly_file)

        if success:
            self.read_binary_and_update_disam()
        return success

    def program(self):
        """Programs the EEPROM
        """
        self.auto_single_step = False
        AssemblyActions.flash(self.args, self.binary, self.serial_thread)

    def reset(self, force_autoreset=False):
        """Resets the 6502 processor.
        Either a simple reset (setting the pin) or a full reset (stepping until first opcode fetch)
        is performed.
        Depending on force_autoreset and the args setting

        Args:
            force_autoreset (bool, optional): Defaults to True.
        """
        if not self.args.simplereset or force_autoreset:
            self.auto_single_step = False
            BusActions.send_api_auto_reset(self.serial_thread)
        else:
            BusActions.send_api_reset(self.serial_thread)

    def single_step(self):
        """Single steps the 6502 processor.
        Request is send.
        Arduino automatically answers with bus update.
        """
        self.auto_single_step = False
        BusActions.send_api_single_step(self.serial_thread)

    def run_program(self):
        """Let the 6502 run freely.
        """
        self.auto_single_step = False
        BusActions.send_api_run(self.serial_thread)
        myprint("Running program, no bus trace available!\n")

    def assemble_program_reset(self):
        """Automatically assembles, programs and resets 6502
        """
        self.auto_single_step = False
        success = self.assemble(no_warning=True)
        if not success:
            return
        self.program()
        self.reset(force_autoreset=True)

    def auto_single_step_toggle(self):
        """Toggles autostepping
        """
        self.auto_single_step = not self.auto_single_step

    def on_key_pressed(self, key):
        """On key pressed.
        Using a keymap to execute the methodes above

        Args:
            key (int): Keycode
        """
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
