from myprint import Color, myprint


class HelpActions:
    shortcuts = [
        ("h", "Help"),
        ("q", "Quit"),
        ("", ""),

        ("a", "Assemble"),
        ("f", "Assemble + Flash"),
        ("o", "Open Assemly File"),

        ("r", "Reset 6502"),
        ("s", "Single Step"),
        ("x", "Halt/Run")
    ]

    tabulator = 20
    shortcuts_per_line = 3

    @classmethod
    def print_help(cls):
        myprint(" 6502 - TERMINAL\n", Color.BOLD)
        myprint("=================\n", Color.BOLD)

        for i, shortcut in enumerate(cls.shortcuts):
            if shortcut[0]:
                myprint("[" + shortcut[0] + "] ", Color.BOLD)
            else:
                myprint(" "*4)
            myprint(shortcut[1] + " "*(cls.tabulator - len(shortcut[1])))

            if (i + 1) % cls.shortcuts_per_line == 0:
                myprint("\n")
            else:
                myprint("   ")
        myprint("\n")
