rom = [0xEA] * 0x2000

with open("010_nop_gen.bin", "wb") as outfile:
    outfile.write(bytearray(rom))
