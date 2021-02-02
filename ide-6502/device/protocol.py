import enum


class Protocol:
    START_BYTE = 0xFF
    WHOIAM_BYTE = 0x2F


class ProtocolMsg(enum.IntEnum):
    START_BYTE = 0
    COMMAND = 1
    PAYLOAD_LEN = 2
    DATA = 3


class ProtocolCommands(enum.IntEnum):
    WHOIAM_VERSION = 1
    PIN_PEEK = 2
    SINGLE_STEP = 3
    MEM_REQUEST = 4
    MEM_WRITE = 5


class CbusBits(enum.IntEnum):
    RDY_BE = (1 << 1)
    RESB = (1 << 2)
    PHI2 = (1 << 3)
    RWB = (1 << 4)
    IRQB = (1 << 5)
    NMIB = (1 << 6)
    SYNC = (1 << 7)
