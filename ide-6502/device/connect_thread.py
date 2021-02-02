import logging
import threading

import serial
from util.settings import Settings

from device.protocol import Protocol, ProtocolCommands
from device.serial_thread import SerialThread


class ConnectThreadHandler:
    def on_connection(self, success: bool, port: str): pass
    def on_response(self, success: bool, port: str): pass
    def on_whoiam_version(self, success: bool, port: str, firmware_version: int): pass


class ConnectThread(threading.Thread):
    def __init__(self, port: str, settings: Settings, handler: ConnectThreadHandler):
        threading.Thread.__init__(self)
        self.port = port
        self.settings = settings
        self.handler = handler

        self.serial_thread: SerialThread

    def run(self):
        try:
            self.serial_thread = SerialThread(self.settings, self.port)
            self.serial_thread.open()
        except serial.SerialException:
            logging.exception("Error connecting to %s.", self.port)
            self.handler.on_connection(False, self.port)
            self.serial_thread.close()
            return
        self.handler.on_connection(True, self.port)

        if not self.serial_thread.wait_on_ready(5):
            logging.exception("No response after reset from %s", self.port)
            self.handler.on_response(False, self.port)
            self.serial_thread.close()
            return
        self.handler.on_response(True, self.port)

        result = self.serial_thread.do(ProtocolCommands.WHOIAM_VERSION, [], 2)
        if not result.success:
            self.serial_thread.close()

        if result.data[0] != Protocol.WHOIAM_BYTE:
            result.success = False
            self.serial_thread.close()

        self.handler.on_whoiam_version(result.success, self.port, result.data[1])

    def get_serial_thread(self) -> SerialThread:
        return self.serial_thread
