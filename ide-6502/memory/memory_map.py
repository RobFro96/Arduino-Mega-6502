import tkinter
import tkinter.ttk

from py6502.dis6502 import dis6502


class MemoryRegion:
    def __init__(self, start: int, size: int):
        self.start = start
        self.size = size
        self.entries = []

    def is_in_region(self, addr: int) -> bool:
        return addr >= self.start and addr < self.start + self.size

    def range(self):
        return range(self.start, self.start + self.size)

    def get_end(self) -> int:
        return self.start + self.size

    def index(self, addr: int) -> int:
        return addr - self.start

    def get_entry(self, addr: int):
        return self.entries[self.index(addr)]

    def create_entries(self, treeview: tkinter.ttk.Treeview, master_entry):
        self.entries = []
        for addr in self.range():
            entry = treeview.insert(master_entry, "end", text="%04X" % addr,
                                    value=("", ""), tag="terminal")
            self.entries.append(entry)

    def update_memory(self, treeview: tkinter.ttk.Treeview, memory):
        for addr in self.range():
            treeview.item(self.get_entry(addr),
                          values=("%02X" % memory[addr & 0xFFFF], ""))

    def update_memory_and_disassembly(self, treeview: tkinter.ttk.Treeview, memory):
        disasm = dis6502(memory)
        addr = self.start
        while addr < self.get_end():
            line_disasm = disasm.disassemble_line(addr)
            text = line_disasm.opcode + " " + line_disasm.operand

            treeview.item(self.get_entry(addr),
                          values=("%02X" % memory[addr & 0xFFFF], text))

            addr += 1
            for _ in range(line_disasm.length - 1):
                treeview.item(self.get_entry(addr),
                              values=("%02X" % memory[addr & 0xFFFF], ""))
                addr += 1


class MemoryMap:
    RAM_START = 0x0000
    RAM_SIZE = 0x0800
    EEPROM_START = 0x8000
    EEPROM_SIZE = 0x1000
    RESET_VECTOR_START = 0xFFFA
    RESET_VECTOR_SIZE = 0x0006
    MEMORY_SIZE = 0x10000

    def __init__(self, treeview: tkinter.ttk.Treeview):
        self.treeview = treeview
        self.ram = MemoryRegion(self.RAM_START, self.RAM_SIZE)
        self.eeprom = MemoryRegion(self.EEPROM_START, self.EEPROM_SIZE)
        self.reset_vector = MemoryRegion(self.RESET_VECTOR_START, self.RESET_VECTOR_SIZE)
        self.memory = [0] * self.MEMORY_SIZE

        self.memory[0xfffb] = 0x80
        self.memory[0xfffd] = 0x80
        self.memory[0xffff] = 0x80

        self.last_pc_marker = None

    def get_value_string(self, addr: int):
        return "%02X" % self.memory[addr & 0xFFFF],

    def create_entries(self, ram_entry, eeprom_entry, reset_vector_entry):
        self.ram.create_entries(self.treeview, ram_entry)
        self.eeprom.create_entries(self.treeview, eeprom_entry)
        self.reset_vector.create_entries(self.treeview, reset_vector_entry)

    def get_entry(self, addr: int):
        if self.ram.is_in_region(addr):
            return self.ram.get_entry(addr)
        if self.eeprom.is_in_region(addr):
            return self.eeprom.get_entry(addr)
        if self.reset_vector.is_in_region(addr):
            return self.reset_vector.get_entry(addr)
        return None

    def update(self, update_ram=True, update_eeprom=True, update_rvector=True):
        if update_ram:
            self.ram.update_memory(self.treeview, self.memory)
        if update_eeprom:
            self.eeprom.update_memory_and_disassembly(self.treeview, self.memory)
        if update_rvector:
            self.reset_vector.update_memory(self.treeview, self.memory)

    def change_memory_address_by_keypress(self, addr: int, digit: int):
        val = self.memory[addr]
        self.memory[addr] = ((val << 4) & 0xF0) + digit

        self.update(self.ram.is_in_region(addr),
                    self.eeprom.is_in_region(addr),
                    self.reset_vector.is_in_region(addr))

        self.treeview.item(self.get_entry(addr), tags=("terminal_italic",))

    def set_pc_marker(self, addr: int):
        if self.last_pc_marker is not None:
            self.treeview.item(self.last_pc_marker, tags=("terminal",))
            self.last_pc_marker = None

        entry = self.get_entry(addr)
        if entry is None:
            return

        self.treeview.item(entry, tags=("terminal_bold",))
        self.last_pc_marker = entry

        return entry

    def set_all_tags(self, tags):
        for mem_region in [self.ram, self.eeprom, self.reset_vector]:
            for addr in mem_region.range():
                self.treeview.item(self.get_entry(addr), tags=tags)

    def set_all_italic(self):
        self.set_all_tags(("terminal_italic",))

    def set_all_normal(self):
        self.set_all_tags(("terminal",))
