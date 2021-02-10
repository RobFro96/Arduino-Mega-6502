"""Arduino-Mega-6502: Programmer and Debugger for 6502 Ben Eater inspired 8-bit Computer
by Robert Fromm, February 2021

Runs the Assembler, reades the binary file, programs the EEPROM
"""

import dataclasses
import os
import tkinter
import tkinter.filedialog

from myprint import myprint, myprint_error
from protocol import ProtocolCommands
from serial_actions import enable_dpi_awareness
from serial_thread import SerialThread


@dataclasses.dataclass
class ReadBinFileResult:
    """Result of AssemblyActions.read_bin_file()
    """
    success: bool
    eeprom_content: list = None


class AssemblyActions:
    """Runs the Assembler, reades the binary file, programs the EEPROM
    """
    @classmethod
    def select(cls, args, force_dialog=False):
        """Opens the open file dialog the select the assembly or binary file.
        If force_dialog is not set the file defines by the args is used, if exists.

        Args:
            args: CLI arguments
            force_dialog (bool, optional): Defaults to False.

        Returns:
            str: filename
        """
        if args.file and os.path.exists(args.file) and not force_dialog:
            return args.file

        if not args.nodpi:
            enable_dpi_awareness()
        root = tkinter.Tk()
        root.iconbitmap("icon.ico")
        root.withdraw()

        filename = tkinter.filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Open Assembly File",
            filetypes=[("Assembly or Binary", ".asm .bin")])

        return filename

    @classmethod
    def get_bin_from_asm(cls, assembly_file: str) -> str:
        """Get the corresponding binary file to the Assembly file by replacing the file extention

        Args:
            assembly_file (str): filename of assembly file

        Returns:
            str: filename of binary file
        """
        return os.path.splitext(assembly_file)[0] + ".bin"

    @classmethod
    def assemble(cls, assembly_file: str):
        """Runs the assembler. The return code of the assembler defines the success.

        Args:
            assembly_file (str): assembly filename

        Returns:
            bool: if return code is 0.
        """
        myprint("-"*75 + "\n")
        myprint("Running VASM on file %s.\n" % assembly_file)
        vasm_path = os.path.join(os.getcwd(), "vasm", "vasm6502_oldstyle.exe")
        out_filename = cls.get_bin_from_asm(assembly_file)

        code = os.system(" ".join(
            [vasm_path, "-Fbin", "-dotdir", assembly_file, "-o", out_filename]
        ))

        if code:
            myprint_error("VASM exited with code %d.\n" % code)
        else:
            myprint("VASM exited with code %d.\n" % code)
        myprint("-"*75 + "\n")

        return code == 0

    @classmethod
    def read_bin_file(cls, assembly_file: str):
        """Reads the binary file and returns the content.
        As the return value the dataclass ReadBinFileResult is used

        Args:
            assembly_file (str): name of assembly file

        Returns:
            ReadBinFileResult: result
        """
        bin_file = cls.get_bin_from_asm(assembly_file)
        try:
            with open(bin_file, "rb") as fp:
                eeprom_content = list(bytearray(fp.read()))
                return ReadBinFileResult(True, eeprom_content)
        except (OSError, IOError, FileNotFoundError):
            return ReadBinFileResult(False)

    @classmethod
    def flash(cls, args, eeprom_content, serial_thread: SerialThread):
        """Programs the EEPROM.
        Page writes are used to speed up the process.
        Empty memory pages are skipped if fullflash in not set in CLI arguments.

        Args:
            args: CLI arguments
            eeprom_content (list): EEPROM content as list
            serial_thread (SerialThread)
        """
        myprint("Writing to EEPROM: ")

        for addr in range(0, 0x8000, 64):
            segment = eeprom_content[addr:addr+64]
            if not args.fullflash and not any(segment):
                continue
            serial_thread.do(ProtocolCommands.MEM_PAGE_WRITE,
                             [addr & 0xFF, (addr >> 8) & 0xFF] + segment)
            myprint(".")
        myprint("\nWriting finished.\n")
