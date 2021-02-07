import dataclasses

from myprint import Color


class MemoryRegions:
    @dataclasses.dataclass
    class Region:
        name: str
        start: int
        end: int
        color: str = ""

        def is_in_region(self, addr: int):
            return self.start <= addr <= self.end

    ZEROPAGE = Region("ZEROPAGE", 0x0000, 0x00FF, Color.LIGHT_YELLOW)
    STACK = Region("STACK", 0x0100, 0x01FF, Color.ORANGE)
    RAM = Region("RAM", 0x0200, 0x3FFF, Color.YELLOW)
    PIA = Region("PIA", 0x7F00, 0x7F0F, Color.BLUE)
    LCD = Region("LCD", 0x7F10, 0x7F1F, Color.GREEN)
    EEPROM = Region("EEPROM", 0x8000, 0xFFFF, "")

    REGIONS = [ZEROPAGE, STACK, RAM, PIA, LCD, EEPROM]

    @classmethod
    def get_region(cls, addr: int):
        for region in cls.REGIONS:
            if region.is_in_region(addr):
                return region
        return None

    @classmethod
    def get_color(cls, addr: int):
        region = cls.get_region(addr)
        if region is None:
            return ""
        return region.color
