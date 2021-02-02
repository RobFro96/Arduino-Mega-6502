import logging
import os
import subprocess
import tkinter
import tkinter.filedialog

from py6502.asm6502 import asm6502
from util.settings import Settings

from memory.memory_map import MemoryMap


class AssemblerActions:
    @classmethod
    def open_asm(cls):
        files = [("Assembly", "*.asm")]
        filename = tkinter.filedialog.askopenfilename(filetypes=files, defaultextension=files)

        return filename

    @classmethod
    def assemble(cls, settings: Settings, filename: str, memory_map: MemoryMap):
        if settings.get_use_vasm:
            return cls.assemble_vasm(filename, memory_map)
        else:
            return cls.assemble_py6502(filename, memory_map)

    @classmethod
    def assemble_py6502(cls, filename: str, memory_map: MemoryMap):
        try:
            with open(filename, mode="r", encoding="utf8") as fp:
                lines = fp.readlines()
        except IOError:
            logging.exception("Error reading file.")
            return False, None

        asm = asm6502()
        result = asm.assemble(lines)

        object_code = [0 if x == -1 else x for x in asm.object_code]
        memory_map.memory[MemoryMap.EEPROM_START: MemoryMap.EEPROM_START + MemoryMap.EEPROM_SIZE] = \
            object_code[MemoryMap.EEPROM_START: MemoryMap.EEPROM_START + MemoryMap.EEPROM_SIZE]
        memory_map.memory[MemoryMap.RESET_VECTOR_START: MemoryMap.RESET_VECTOR_START + MemoryMap.RESET_VECTOR_SIZE] = \
            object_code[MemoryMap.RESET_VECTOR_START: MemoryMap.RESET_VECTOR_START +
                        MemoryMap.RESET_VECTOR_SIZE]

        memory_map.update()
        memory_map.set_all_italic()

        return True, result[0]

    @classmethod
    def assemble_vasm(cls, filename: str, memory_map: MemoryMap):
        vasm_path = os.path.join(os.getcwd(), "vasm", "vasm6502_oldstyle.exe")
        pre, _ = os.path.splitext(filename)
        out_filename = pre + ".bin"

        logging.info([vasm_path, "-Fbin", "-dotdir", filename, "-o", out_filename])
        process = subprocess.Popen([vasm_path, "-Fbin", "-dotdir", filename, "-o", out_filename],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        try:
            with open(out_filename, "rb") as fp:
                eeprom_content = list(bytearray(fp.read()))
        except (OSError, IOError, FileNotFoundError):
            return False, stderr.decode("utf8").split("\n")

        memory_map.memory[MemoryMap.EEPROM_START: MemoryMap.EEPROM_START + MemoryMap.EEPROM_SIZE] = \
            eeprom_content[0: MemoryMap.EEPROM_SIZE]
        memory_map.memory[MemoryMap.RESET_VECTOR_START: MemoryMap.RESET_VECTOR_START +
                          MemoryMap.RESET_VECTOR_SIZE] = \
            eeprom_content[MemoryMap.RESET_VECTOR_START - MemoryMap.EEPROM_START:
                           MemoryMap.RESET_VECTOR_START + MemoryMap.RESET_VECTOR_SIZE - MemoryMap.EEPROM_START]

        memory_map.update()
        memory_map.set_all_italic()

        return True, stderr.decode("utf8").split("\n")
