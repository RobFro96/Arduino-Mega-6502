"""Arduino-Mega-6502: Programmer and Debugger for 6502 Ben Eater inspired 8-bit Computer
by Robert Fromm, February 2021

Opens a thread for serial communication with the Arduino, using the specified protocol.
"""

import dataclasses
import queue
import threading
import typing

import serial

from myprint import myprint_error
from protocol import Protocol, ProtocolCommands, ProtocolMsg


@dataclasses.dataclass
class SerialThreadResponse:
    """Response of SerialThread.do() method
    """
    success: bool
    data: typing.List[int] = None


class SerialThread(threading.Thread):
    """Opens a thread for serial communication with the Arduino, using the specified protocol.
    """

    def __init__(self, port: str, args):
        """Constructor.
        Initializing the thread.

        Args:
            port (str): portname
            args: CLI arguments (baud rate)
        """
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
        """Open the serial port and starts the thread.
        May throw serial.SerialException.
        """
        self.connection = serial.Serial(self.port, self.args.baud, timeout=1)
        self.start()

    def close(self):
        """Closes the thread by setting the stop event.
        """
        self.stop_event.set()

    def wait_on_ready(self, timeout=None):
        """Wait until the Arduiono is ready.
        (Arduinos sends one byte after reset)

        Args:
            timeout (int, optional): timeout in seconds. Defaults to None.

        Returns:
            bool: True if Arduino is ready
        """
        return self.ready_event.wait(timeout)

    def is_connected(self):
        """Returns true if serial thread is running.
        Serial threads stopps if Arduino is disconnected.

        Returns:
            bool: True if running
        """
        return not self.stop_event.is_set()

    def run(self):
        """Thread run method.
        """
        self.ready_event.set()

        msg = []
        payload_len = 0

        try:
            while not self.stop_event.wait(1e-3):
                n = max(0, min(self.connection.inWaiting(), 1024))  # Number of bytes to read
                buffer = self.connection.read(n)  # Read bytes

                for char in buffer:
                    # Analyze charwise
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

        # Close
        if self.connection and self.connection.is_open:
            self.connection.close()

    def __read_message(self, msg):
        """Executed if one message was read completly.
        Puts message into corresponding queue. Each command code has its own queue.

        Args:
            msg (list): complete message (start, command, length, data)
        """
        if len(msg) < 3:
            return

        command = msg[ProtocolMsg.COMMAND]

        if not command in self.read_queues:
            return

        self.read_queues[command].put(msg)

    def do(self, command: ProtocolCommands, data: typing.List, expected_len: int = -1) \
            -> SerialThreadResponse:
        """Performs a serial interaction.
        Containing of a complete message to the Arduino and waiting for a response with the same
        command code.

        Args:
            command (ProtocolCommands): Command Code
            data (typing.List): Data to be sent
            expected_len (int, optional): Checking the length of the received message. Defaults to -1.

        Raises:
            Exception: Unknown Command

        Returns:
            SerialThreadResponse: response
        """
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
