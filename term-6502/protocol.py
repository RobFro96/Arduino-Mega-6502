import enum


class Protocol:
    START_BYTE = 0xFF
    WHOIAM_BYTE = 0xF2


class ProtocolMsg(enum.IntEnum):
    START_BYTE = 0
    COMMAND = 1
    PAYLOAD_LEN = 2
    DATA = 3


class ProtocolCommands(enum.IntEnum):
    WHOIAM_VERSION = 1
    MEM_REQUEST = 2
    MEM_WRITE = 3
    MEM_PAGE_WRITE = 4


class CbusBits(enum.IntEnum):
    RDY_BE = (1 << 1)
    RESB = (1 << 2)
    PHI2 = (1 << 3)
    RWB = (1 << 4)
    IRQB = (1 << 5)
    NMIB = (1 << 6)
    SYNC = (1 << 7)
