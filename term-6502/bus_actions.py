import queue

from memory_regions import MemoryRegions
from myprint import Color, myprint
from protocol import ApiActions, CbusBits, ProtocolCommands, ProtocolMsg
from py6502.dis6502 import dis6502
from serial_thread import SerialThread


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

    def get_signal_list(self):
        result = []
        if not self.get_resb():
            result.append("RESB")
        if not self.get_nmib():
            result.append("NMIB")
        if not self.get_irqb():
            result.append("IRQB")
        return result


class BusActions:
    @classmethod
    def update(cls, serial_thread: SerialThread, binary):
        bus_action_queue: queue.Queue = serial_thread.read_queues[ProtocolCommands.BUS_ACTION]
        while not bus_action_queue.empty():
            data = bus_action_queue.get()[ProtocolMsg.DATA:]
            bus_state = BusState(data)

            values = dict(
                abus=bus_state.abus,
                dbus=bus_state.dbus,
                rw="R" if bus_state.get_rwb() else "w",
                signal_list=" ".join(bus_state.get_signal_list()),
                disasm=cls.get_disassembly(binary, bus_state.abus) if bus_state.get_sync() else ""
            )
            # bold = Color.BOLD if bus_state.get_sync() else ""
            region_color = MemoryRegions.get_color(bus_state.abus)

            myprint("> AB = 0x%(abus)04X  %(rw)s  DB = 0x%(dbus)02X    " % values, region_color)
            myprint("%(signal_list)-5s " % values, Color.GRAY)
            myprint("%(disasm)s\n" % values)

    @classmethod
    def get_disassembly(cls, disasm: dis6502, addr: int):
        if disasm is None:
            return ""
        result = disasm.disassemble_line(addr)
        return result.opcode + " " + result.operand

    @classmethod
    def send_api_action(cls, serial_thread: SerialThread, action):
        serial_thread.do(ProtocolCommands.API_ACTIONS, [action])

    @classmethod
    def send_api_reset(cls, serial_thread: SerialThread):
        cls.send_api_action(serial_thread, ApiActions.RESET)

    @classmethod
    def send_api_auto_reset(cls, serial_thread: SerialThread):
        cls.send_api_action(serial_thread, ApiActions.AUTO_RESET)

    @classmethod
    def send_api_single_step(cls, serial_thread: SerialThread):
        cls.send_api_action(serial_thread, ApiActions.SINGLE_STEP)

    @classmethod
    def send_api_run(cls, serial_thread: SerialThread):
        cls.send_api_action(serial_thread, ApiActions.RUN)
