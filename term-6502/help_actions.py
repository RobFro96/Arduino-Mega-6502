import argparse

from myprint import Color, myprint


class HelpActions:
    shortcuts = [
        ("h", "Help"),
        ("q", "Quit"),
        ("", ""),

        ("o", "Open .asm or .bin"),
        ("a", "Assemble"),
        ("p", "Program"),

        ("r", "Reset 6502"),
        ("u", "Assemble+Program+Reset"),
        ("", ""),

        ("s", "Single Step"),
        ("t", "Auto single step"),
        ("x", "Run")
    ]

    tabulator = 20
    shortcuts_per_line = 3

    @classmethod
    def get_args(cls):
        parser = argparse.ArgumentParser(
            description="TERM-6502\nArduino Mega 6502 Support")
        parser.add_argument("-p", "--port", type=str, action="store", help="serial port of device")
        parser.add_argument("-b", "--baud", type=int, action="store", default=115200,
                            help="baud rate of serial port")
        parser.add_argument("-f", "--file", type=str, action="store", help="assembly file to load")
        parser.add_argument("-d", "--nodpi", action="store_true",
                            help="disable DPI awareness")
        parser.add_argument("-F", "--fullflash", action="store_true",
                            help="program always the complete EEPROM")
        parser.add_argument("-r", "--simplereset", action="store_true",
                            help="just set the reset line on reset.")
        parser.add_argument("-a", "--ass_delay", type=float, action="store", default=0,
                            help="Auto single step delay in seconds")
        return parser.parse_args()

    @classmethod
    def print_help(cls):
        myprint(" 6502 - TERMINAL\n")
        myprint("=================\n")

        for i, shortcut in enumerate(cls.shortcuts):
            if shortcut[0]:
                myprint("[" + shortcut[0] + "] ", Color.BLUE)
            else:
                myprint(" "*4)
            myprint(shortcut[1] + " "*(cls.tabulator - len(shortcut[1])))

            if (i + 1) % cls.shortcuts_per_line == 0:
                myprint("\n")
            else:
                myprint("   ")
        myprint("\n")
