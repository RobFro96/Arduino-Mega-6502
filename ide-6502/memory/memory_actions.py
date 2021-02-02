import json
import logging
import threading
import tkinter
import tkinter.filedialog

from device.protocol import ProtocolCommands
from device.serial_thread import SerialThread

from memory.memory_map import MemoryMap


class MemoryActions:
    @classmethod
    def save(cls, memory_map: MemoryMap):
        files = [("JSON", "*.json")]
        filename = tkinter.filedialog.asksaveasfilename(filetypes=files, defaultextension=files)

        try:
            with open(filename, mode="w", encoding="utf8") as fp:
                json.dump(memory_map.memory, fp, separators=(',', ':'))
                return filename
        except (IOError, json.JSONDecodeError):
            logging.exception("Error writing file.")
            return None

    @classmethod
    def open(cls, memory_map: MemoryMap):
        files = [("JSON", "*.json")]
        filename = tkinter.filedialog.askopenfilename(filetypes=files, defaultextension=files)

        logging.debug("reading started")

        try:
            with open(filename, mode="r", encoding="utf8") as fp:
                memory_map.memory = json.load(fp)
        except IOError:
            logging.exception("Error reading file.")
            return None

        logging.debug("reading finished")

        return filename

    @classmethod
    def upload_region(cls, serialThread: SerialThread, memory_map: MemoryMap, start: int, size: int, chunk_size: int = 128):
        serialThread.do(ProtocolCommands.MEM_REQUEST, [start & 0xFF, (start >> 8) & 0xFF, 0], 0)

        for chunk_start in range(start, start + size, chunk_size):
            chunk_stop = min(chunk_start + chunk_size, start + size)
            serialThread.do(ProtocolCommands.MEM_WRITE, memory_map.memory[chunk_start: chunk_stop])

    @classmethod
    def upload(cls, serialThread: SerialThread, memory_map: MemoryMap):
        cls.upload_region(
            serialThread, memory_map, memory_map.RAM_START, memory_map.RAM_SIZE)
        cls.upload_region(
            serialThread, memory_map, memory_map.EEPROM_START, memory_map.EEPROM_SIZE)
        cls.upload_region(
            serialThread, memory_map, memory_map.RESET_VECTOR_START, memory_map.RESET_VECTOR_SIZE)

        memory_map.set_all_normal()

    @classmethod
    def download_region(cls, serialThread: SerialThread, memory_map: MemoryMap, start: int, size: int, chunk_size: int = 128):
        for chunk_start in range(start, start + size, chunk_size):
            chunk_stop = min(chunk_start + chunk_size, start + size)
            chunk_len = chunk_stop - chunk_start
            result = serialThread.do(ProtocolCommands.MEM_REQUEST,
                                     [chunk_start & 0xFF, (chunk_start >> 8) & 0xFF, chunk_len],
                                     chunk_len)

            if result.success:
                memory_map.memory[chunk_start:chunk_len] = result.data

    @classmethod
    def download(cls, serialThread: SerialThread, memory_map: MemoryMap):
        cls.download_region(
            serialThread, memory_map, memory_map.RAM_START, memory_map.RAM_SIZE)
        cls.download_region(
            serialThread, memory_map, memory_map.EEPROM_START, memory_map.EEPROM_SIZE)
        cls.download_region(
            serialThread, memory_map, memory_map.RESET_VECTOR_START, memory_map.RESET_VECTOR_SIZE)

        memory_map.update()
        memory_map.set_all_normal()
