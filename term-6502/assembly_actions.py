import os
import tkinter
import tkinter.filedialog

import util


class AssemblyActions:
    @classmethod
    def select(cls, args, force_dialog=False):
        if args.file and os.path.exists(args.file) and not force_dialog:
            return args.file

        if not args.nodpi:
            util.enable_dpi_awareness()
        root = tkinter.Tk()
        root.iconbitmap("icon.ico")
        root.withdraw()

        filename = tkinter.filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Open Assembly File",
            filetypes=(("Assembly", "*.asm"),))

        return filename
