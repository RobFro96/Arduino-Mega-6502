"""Arduino-Mega-6502: Programmer and Debugger for 6502 Ben Eater inspired 8-bit Computer
by Robert Fromm, February 2021

Constants of communication protocol with Arduino.
"""


import enum


class Protocol:
    """Byte values of protocol
    """
    START_BYTE = 0xFF
    WHOIAM_BYTE = 0xF2


class ProtocolMsg(enum.IntEnum):
    """Stucture of a message
    """
    START_BYTE = 0
    COMMAND = 1
    PAYLOAD_LEN = 2
    DATA = 3


class ProtocolCommands(enum.IntEnum):
    """Command codes
    """
    WHOIAM_VERSION = 1
    MEM_REQUEST = 2
    MEM_WRITE = 3
    MEM_PAGE_WRITE = 4
    BUS_ACTION = 5
    API_ACTIONS = 6


class CbusBits(enum.IntEnum):
    """Definition of bits of the control bus value of BUS_ACTION message
    """
    RDY_BE = (1 << 1)
    RESB = (1 << 2)
    PHI2 = (1 << 3)
    RWB = (1 << 4)
    IRQB = (1 << 5)
    NMIB = (1 << 6)
    SYNC = (1 << 7)


class ApiActions(enum.IntEnum):
    """Definition of bits of the API_ACTIONS message
    """
    SINGLE_STEP = (1 << 0)
    RUN = (1 << 1)
    RESET = (1 << 2)
    NMI = (1 << 3)
    IRQ = (1 << 4)
    AUTO_RESET = (1 << 5)
