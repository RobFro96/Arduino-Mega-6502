import dataclasses
import threading
import typing

from device.protocol import CbusBits, ProtocolCommands
from device.serial_thread import SerialThread


class BusState:
    def __init__(self, data):
        self.cbus = data[0]
        self.dbus = data[1]
        self.abus = data[2] + (data[3] << 8)

    def get_resb(self) -> bool:
        return bool(self.cbus & CbusBits.RESB)

    def get_rwb(self) -> bool:
        return bool(self.cbus & CbusBits.RWB)

    def get_sync(self) -> bool:
        return bool(self.cbus & CbusBits.SYNC)

    def get_nmib(self) -> bool:
        return bool(self.cbus & CbusBits.NMIB)

    def get_irqb(self) -> bool:
        return bool(self.cbus & CbusBits.IRQB)

    def get_rdy_be(self) -> bool:
        return bool(self.cbus & CbusBits.RDY_BE)

    def __repr__(self):
        return "BusState(cbus=0x%02X, dbus=0x%02X, abus=0x%04X)" % (self.cbus, self.dbus, self.abus)

    def get_signal_list(self) -> typing.List[str]:
        result = []
        if not self.get_resb():
            result.append("RESB")
        if not self.get_nmib():
            result.append("NMIB")
        if not self.get_irqb():
            result.append("IRQB")
        if not self.get_rdy_be():
            result.append("RDY_BE")
        return result


@dataclasses.dataclass
class BusGuiState:
    reset: bool
    nmi: bool
    irq: bool
    is_dbus_fixed: bool
    dbus_value: int


class BusActions:
    @classmethod
    def do_pin_peek(cls, serialThread: SerialThread, callback):
        def thread_function():
            result = serialThread.do(ProtocolCommands.PIN_PEEK, [], 4)

            if not result.success:
                return

            bus_state = BusState(result.data)
            callback(bus_state)

        threading.Thread(target=thread_function).start()

    @classmethod
    def do_single_step(cls, serialThread: SerialThread, callback, gui_state: BusGuiState):
        def thread_function():
            cbus = 0
            if gui_state.reset:
                cbus |= CbusBits.RESB
            if gui_state.nmi:
                cbus |= CbusBits.NMIB
            if gui_state.irq:
                cbus |= CbusBits.IRQB

            fixed_dbus_byte = 1 if gui_state.is_dbus_fixed else 0

            result = serialThread.do(ProtocolCommands.SINGLE_STEP,
                                     [cbus, fixed_dbus_byte, gui_state.dbus_value], 4)

            if not result.success:
                return

            bus_state = BusState(result.data)
            callback(bus_state)

        threading.Thread(target=thread_function).start()
