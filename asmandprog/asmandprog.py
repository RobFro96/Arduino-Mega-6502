import argparse
import os
import sys
import time

import coloredlogs
import serial
import serial.tools.list_ports

RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"


class AsmAndProg:
    @classmethod
    def get_bin_from_asm(cls, assembly_file: str) -> str:
        return os.path.splitext(assembly_file)[0] + ".bin"

    @classmethod
    def get_ports(cls) -> tuple[list[str], list[str]]:
        port_list: list = sorted(serial.tools.list_ports.comports())
        port_names: list[str] = [port[0] for port in port_list]
        port_descrs: list[str] = [port[1] for port in port_list]
        return port_names, port_descrs

    def __init__(self) -> None:
        self.configure_argparser()
        if self.filename.endswith(".asm"):
            print("Assemble %s" % self.filename)
            if not self.assemble():
                sys.exit(1)
            self.filename = self.get_bin_from_asm(self.filename)

        if self.filename.endswith(".bin"):
            print("Program %s" % self.filename)

            if not self.analyze_mem_region():
                sys.exit(2)

            if not self.load_binary():
                sys.exit(3)

            if not self.open_port():
                sys.exit(4)

            if not self.program():
                sys.exit(5)

            if not self.verify():
                sys.exit(6)

            print("Programming finished.")
            sys.exit(1)
        else:
            print(RED + ("Error: Cannot assemble or program %s" % self.filename) + RESET)
            sys.exit(7)

    def configure_argparser(self) -> None:
        parser = argparse.ArgumentParser(
            prog="Assembler and EEPROM programmer",
            description="Assemble 6502 programs and program to DIY Ardunio EEPROM programmer")

        parser.add_argument("filename",
                            help="assembly or binary file to program to EEPROM")
        parser.add_argument("-p", "--port", default="autodetect", required=False,
                            help="serial port to EEPROM programmer, default: autodetect")
        parser.add_argument("-a", "--asm-options", default="-Fbin -dotdir", required=False,
                            help="vasm assembler options")
        parser.add_argument(
            "-m", "--mem-region", default="E000-FFFF", required=False,
            help="memory region of EEPROM to program to, hex values separated by (-), both values included")
        parser.add_argument("-l", "--left-align", action="store_true", required=False,
                            help="left align memory")
        parser.add_argument(
            "-d", "--port-descr", default="USB-SERIAL", required=False,
            help="Port description matching the EEPROM programmer used for port autodetection")
        parser.add_argument("-b", "--baud-rate", default=115200, type=int, required=False,
                            help="EEPROM programmer baud rate")
        parser.add_argument("-f", "--full-flash", action="store_true", required=False,
                            help="fully program the EEPROM and do not skip empty blocks")

        self.args: argparse.Namespace = parser.parse_args()
        self.filename: str = self.args.filename

    def assemble(self) -> bool:
        print("-"*75)
        vasm_path: str = os.path.join(os.path.split(__file__)[0], "vasm", "vasm6502_oldstyle.exe")
        out_filename: str = self.get_bin_from_asm(self.filename)
        command: str = " ".join(
            [vasm_path] + self.args.asm_options.split(" ") + [self.filename, "-o", out_filename]
        )
        print(command)

        code: int = os.system(command)

        if code:
            print(RED, end="")
        print("VASM exited with code %d." % code)
        print(RESET, end="")
        print("-"*75)

        return code == 0

    def analyze_mem_region(self) -> bool:
        splitted: list[str] = self.args.mem_region.split("-")
        if len(splitted) != 2:
            print(RED + "Invalid memory range: no or too many dash (-) symbols." + RESET)
            return False

        try:
            self.mem_start = int(splitted[0], 16)
            self.mem_end = int(splitted[1], 16)
        except:
            print(RED + "Cannot read hex values." + RESET)
            return False

        if self.mem_start & 0x3F != 0 or (self.mem_end + 1) & 0x3F != 0:
            print(RED + "Memory region is not aligned to 64-byte blocks." + RESET)
            return False

        self.mem_size: int = self.mem_end - self.mem_start + 1
        if self.mem_size <= 0:
            print(RED + "Invalid memory region: size or negative size." + RESET)
            return False

        return True

    def load_binary(self) -> bool:
        try:
            with open(self.filename, "rb") as fp:
                self.mem_content = list(bytearray(fp.read()))
                if len(self.mem_content) < self.mem_size:
                    zeros: list = [0] * (self.mem_size - len(self.mem_content))
                    if self.args.left_align:
                        self.mem_content += zeros
                    else:
                        self.mem_content: list = zeros + self.mem_content
                elif len(self.mem_content) > self.mem_size:
                    print(RED + "Binary file is larger than memory range." + RESET)
                    return False

                return True
        except (OSError, IOError, FileNotFoundError):
            print(RED + ("Cannot read binary %s" % self.filename) + RESET)
            return False

    def open_port(self) -> bool:
        self.portname: str = self.args.port
        if self.portname == "autodetect":
            if not self.autodetect_port():
                return False

        print("Connecting to port %s." % self.portname)

        try:
            self.port = serial.Serial(self.portname, self.args.baud_rate, timeout=1)
        except serial.SerialException:
            print(RED + "Cannot connect to serial port." + RESET)
            return False

        time.sleep(2)

        if not self.serial_write("i"):
            return False

        result: str = self.serial_read()
        if not "RobertFromm,EEPROMProgrammer" in result:
            print(RED + "Reading firmware information from EEPROM programmer failed." + RESET)
            return False

        print("Successfully connected to EEPROM programmer")
        return True

    def serial_write(self, command: str) -> bool:
        if not command.endswith("\n"):
            command += "\n"

        try:
            self.port.write(command.encode("ascii"))
        except serial.SerialException:
            print(RED + "Writing to serial port failed." + RESET)
            return False
        return True

    def serial_read(self) -> str:
        try:
            line: bytes = self.port.read_until(b"\n")
            return line.decode("ascii").strip("\n")
        except serial.SerialException:
            print(RED + "Reading to serial port failed." + RESET)
            return ""

    def autodetect_port(self) -> bool:
        for portname, port_descr in zip(*self.get_ports()):
            if self.args.port_descr in port_descr:
                self.portname = portname
                return True
        print(RED + "Cannot autodetect port." + RESET)
        return False

    def program(self) -> bool:
        for i in range(0, self.mem_size, 64):
            segment: list = self.mem_content[i: i+64]
            addr: int = i + self.mem_start
            if not self.args.full_flash and not any(segment):
                continue

            if not self.program_block(addr, segment):
                print(RED + ("Programm block %04X failed." % addr)+RESET)
                return False
        return True

    def program_block(self, addr: int, segment: list[int]) -> bool:
        print("Programming block %04X " % addr, end="")

        command = "w"
        command += "%04x" % addr
        for byte in segment:
            command += "%02x" % byte

        if not self.serial_write(command):
            return False

        result: str = self.serial_read()
        if not command[:5] in result:
            return False

        print("finished.")
        return True

    def verify(self) -> bool:
        success = True

        for i in range(0, self.mem_size, 64):
            segment: list = self.mem_content[i: i+64]
            addr: int = i + self.mem_start
            if not self.args.full_flash and not any(segment):
                continue

            if not self.verify_block(addr, segment):
                success = False

        return success

    def verify_block(self, addr: int, segment: list[int]) -> bool:
        print("Verifiying block %04X " % addr, end="")

        command = "r"
        command += "%04x" % addr

        response: str = command
        for byte in segment:
            response += "%02x" % byte

        if not self.serial_write(command):
            return False

        result: str = self.serial_read()
        if result != response:
            print(RED + "failed." + RESET)
            print("EXPECT: " + repr(response))
            print("GOT:    " + repr(result))
            return False

        print("finished.")
        return True


if __name__ == "__main__":
    coloredlogs.install()
    AsmAndProg()
