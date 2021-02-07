import dataclasses
import queue
import threading
import time
import typing

import serial

from myprint import myprint_error
from protocol import Protocol, ProtocolCommands, ProtocolMsg


@dataclasses.dataclass
class SerialThreadResponse:
    success: bool
    data: typing.List[int] = None


class SerialThread(threading.Thread):
    def __init__(self, port: str, args):
        threading.Thread.__init__(self)
        self.port = port
        self.args = args
        self.connection: serial.Serial

        self.stop_event = threading.Event()
        self.ready_event = threading.Event()

        self.read_queues = {}
        for cmd in ProtocolCommands:
            self.read_queues[cmd] = queue.Queue()

    def open(self):
        self.connection = serial.Serial(self.port, self.args.baud, timeout=1)
        self.start()

    def close(self):
        self.stop_event.set()

    def wait_on_ready(self, timeout=None):
        return self.ready_event.wait(timeout)

    def is_connected(self):
        return not self.stop_event.is_set()

    def run(self):
        self.connection.setDTR(True)
        time.sleep(1e-3)
        self.connection.setDTR(False)
        self.connection.read(1)
        self.ready_event.set()

        msg = []
        payload_len = 0

        try:
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
        except serial.SerialException:
            myprint_error("Serial port %s disconnected.\n" % self.port)
            self.stop_event.set()

        if self.connection and self.connection.is_open:
            self.connection.close()

    def __read_message(self, msg):
        if len(msg) < 3:
            return

        command = msg[ProtocolMsg.COMMAND]

        if not command in self.read_queues:
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
                return SerialThreadResponse(False)
            return SerialThreadResponse(True, data)
        except queue.Empty:
            return SerialThreadResponse(False)
