"""Arduino-Mega-6502: Programmer and Debugger for 6502 Ben Eater inspired 8-bit Computer
by Robert Fromm, February 2021

Color definitions and function used for printing messages.
"""

import sys


class Color:
    """Color Codes
    """
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    GRAY = "\033[37m"
    DARK = "\033[90m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    LIGHT_YELLOW = "\033[38;5;229m"
    ORANGE = "\033[38;5;202m"


def myprint(text, color=None):
    """Function to print a text in the given color.
    After this function stdout is flushed to ensure that the text appears on screen.

    Args:
        text (str): text to print
        color (str, optional): color to used. Defaults to None.
    """
    if color:
        print(color, end="")
    print(text, end="")
    if color:
        print(Color.RESET, end="")
    sys.stdout.flush()


def myprint_error(text):
    """Prints an error message in red

    Args:
        text (str): text to print
    """
    myprint(text, Color.RED)


def myprint_warning(text):
    """Prints an warning message in yellow

    Args:
        text (str): text to print
    """
    myprint(text, Color.YELLOW)
