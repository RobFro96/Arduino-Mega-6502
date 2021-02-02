import dataclasses
import logging
import queue
import threading
import time
import typing

import serial
from util.settings import Settings

from device.protocol import Protocol, ProtocolCommands, ProtocolMsg


@dataclasses.dataclass
class SerialThreadResponse:
    success: bool
    data: typing.List[int] = None


class SerialThread(threading.Thread):
    def __init__(self, settings: Settings, port: str):
        threading.Thread.__init__(self)
        self.port = port
        self.settings = settings
        self.connection: serial.Serial

        self.stop_event = threading.Event()
        self.ready_event = threading.Event()

        self.read_queues = {}
        for cmd in ProtocolCommands:
            self.read_queues[cmd] = queue.Queue()

    def open(self):
        self.connection = serial.Serial(self.port, self.settings.get_baud_rate(), timeout=1)
        self.start()

    def close(self):
        self.stop_event.set()

    def wait_on_ready(self, timeout=None):
        return self.ready_event.wait(timeout)

    def run(self):
        self.connection.setDTR(True)
        time.sleep(1e-3)
        self.connection.setDTR(False)
        self.connection.read(1)
        self.ready_event.set()

        msg = []
        payload_len = 0

        while not self.stop_event.wait(1e-3):
            n = max(0, min(self.connection.inWaiting(), 1024))  # Anzahl der zu lesenden Bytes
            buffer = self.connection.read(n)  # Auslesen der Bytes

            for char in buffer:
                # Algorithmus zur Detektion einer Nachricht
                if (char == Protocol.START_BYTE and len(msg) == 0) or len(msg) > 0:
                    msg.append(char)
                if len(msg) == ProtocolMsg.PAYLOAD_LEN + 1:
                    payload_len = char
                if len(msg) == payload_len + ProtocolMsg.DATA:
                    self.__read_message(msg)
                    msg = []
                    payload_len = 0

        logging.info("SerialThread closed.")
        if self.connection and self.connection.is_open:
            self.connection.close()

    def __read_message(self, msg):
        if len(msg) < 3:
            logging.warning("Too short message: %r", msg)
            return

        command = msg[ProtocolMsg.COMMAND]

        if not command in self.read_queues:
            logging.warning("Unknown command in message: %r", msg)
            return

        self.read_queues[command].put(msg)

    def do(self, command: ProtocolCommands, data: typing.List, expected_len: int = -1) -> SerialThreadResponse:
        if not command in self.read_queues:
            raise Exception("Unknown command: %x" % command)

        msg = [Protocol.START_BYTE, command, len(data)]
        msg.extend(data)

        self.connection.write(bytearray(msg))

        try:
            ack = self.read_queues[command].get(timeout=1)
            data = ack[ProtocolMsg.DATA:]
            if len(data) != expected_len and expected_len != -1:
                logging.error("No response or wrong length from command %d.", command)
                return SerialThreadResponse(False)
            return SerialThreadResponse(True, data)
        except queue.Empty:
            return SerialThreadResponse(False)
