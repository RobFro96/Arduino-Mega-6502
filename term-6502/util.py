def enable_dpi_awareness():
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
