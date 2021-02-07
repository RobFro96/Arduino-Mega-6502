rom = [0xEA] * 0x8000

with open("all_EA.bin", "wb") as outfile:
    outfile.write(bytearray(rom))
