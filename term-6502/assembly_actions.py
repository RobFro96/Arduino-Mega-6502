import dataclasses
import os
import tkinter
import tkinter.filedialog

import coloredlogs

import util
from myprint import myprint, myprint_error
from protocol import ProtocolCommands
from serial_thread import SerialThread


@dataclasses.dataclass
class ReadBinFileResult:
    success: bool
    eeprom_content: list = None


class AssemblyActions:
    @classmethod
    def select(cls, args, force_dialog=False):
        if args.file and os.path.exists(args.file) and not force_dialog:
            return args.file

        if not args.nodpi:
            util.enable_dpi_awareness()
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
        return os.path.splitext(assembly_file)[0] + ".bin"

    @classmethod
    def assemble(cls, assembly_file: str):
        myprint("-"*75 + "\n")
        myprint("Running VASM on file %s.\n" % assembly_file)
        vasm_path = os.path.join(os.getcwd(), "vasm", "vasm6502_oldstyle.exe")
        out_filename = cls.get_bin_from_asm(assembly_file)

        # process = subprocess.Popen(
        # [vasm_path, "-Fbin", "-dotdir", assembly_file, "-o", out_filename]
        #    ["ls"])
        # process.communicate()

        code = os.system(" ".join(
            [vasm_path, "-Fbin", "-dotdir", assembly_file, "-o", out_filename]
        ))

        coloredlogs.install()

        if code:
            myprint_error("VASM exited with code %d.\n" % code)
        else:
            myprint("VASM exited with code %d.\n" % code)
        myprint("-"*75 + "\n")

        return code == 0

    @classmethod
    def read_bin_file(cls, assembly_file: str):
        bin_file = cls.get_bin_from_asm(assembly_file)
        try:
            with open(bin_file, "rb") as fp:
                eeprom_content = list(bytearray(fp.read()))
                return ReadBinFileResult(True, eeprom_content)
        except (OSError, IOError, FileNotFoundError):
            return ReadBinFileResult(False)

    @classmethod
    def flash(cls, args, eeprom_content, serial_thread: SerialThread):
        myprint("Writing to EEPROM: ")

        for addr in range(0, 0x8000, 64):
            segment = eeprom_content[addr:addr+64]
            if not args.fullflash and not any(segment):
                continue
            serial_thread.do(ProtocolCommands.MEM_PAGE_WRITE,
                             [addr & 0xFF, (addr >> 8) & 0xFF] + segment)
            myprint(".")
        myprint("\nWriting finished.\n")
