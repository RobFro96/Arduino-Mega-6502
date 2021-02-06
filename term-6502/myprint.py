class Color:
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


def myprint(text, color=None):
    if color:
        print(color, end="")
    print(text, end="")
    if color:
        print(Color.RESET, end="")


def myprint_error(text):
    myprint(text, Color.RED)


def myprint_warning(text):
    myprint(text, Color.YELLOW)
