"""Arduino-Mega-6502: Programmer and Debugger for 6502 Ben Eater inspired 8-bit Computer
by Robert Fromm, February 2021

Memory Regions and colorization
"""

import dataclasses

from myprint import Color


class MemoryRegions:
    """Memory Regions and colorization
    """
    @dataclasses.dataclass
    class Region:
        """Dataclass of region containing name, start address, end address (inclusive) and display
        color.
        """
        name: str
        start: int
        end: int
        color: str = ""

        def is_in_region(self, addr: int):
            """Returns True, if given address is in this region.

            Args:
                addr (int): Address to check

            Returns:
                [type]: True, if in region
            """
            return self.start <= addr <= self.end

    # Define all regions
    ZEROPAGE = Region("ZEROPAGE", 0x0000, 0x00FF, Color.LIGHT_YELLOW)
    STACK = Region("STACK", 0x0100, 0x01FF, Color.ORANGE)
    RAM = Region("RAM", 0x0200, 0x3FFF, Color.YELLOW)
    PIA = Region("PIA", 0x7F00, 0x7F0F, Color.BLUE)
    LCD = Region("LCD", 0x7F10, 0x7F1F, Color.GREEN)
    EEPROM = Region("EEPROM", 0x8000, 0xFFFF, "")

    # Add regions to list
    REGIONS = [ZEROPAGE, STACK, RAM, PIA, LCD, EEPROM]

    @classmethod
    def get_region(cls, addr: int):
        """Returns the matching region of the given address.
        Returns None of no region matches.

        Args:
            addr (int): Address to check

        Returns:
            Region: Matching region
        """
        for region in cls.REGIONS:
            if region.is_in_region(addr):
                return region
        return None

    @classmethod
    def get_color(cls, addr: int):
        """Returns region color by address.

        Args:
            addr (int): Address to check

        Returns:
            str: Matching color code or empty string
        """
        region = cls.get_region(addr)
        if region is None:
            return ""
        return region.color
