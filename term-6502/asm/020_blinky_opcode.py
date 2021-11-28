rom = [0] * 0x2000

# lda #$FF
rom[0] = 0xA9
rom[1] = 0xFF

# sta $8002
rom[2] = 0x8D
rom[3] = 0x02
rom[4] = 0x80

# lda #$A5
rom[5] = 0xA9
rom[6] = 0xA5

# sta $8000
rom[7] = 0x8D
rom[8] = 0x00
rom[9] = 0x80

# lda #$5A
rom[10] = 0xA9
rom[11] = 0x5A

# sta $8000
rom[12] = 0x8D
rom[13] = 0x00
rom[14] = 0x80

# jmp $E005
rom[15] = 0x4C
rom[16] = 0x05
rom[17] = 0xE0

# reset vector = $E000
rom[0x1FFC] = 0x00
rom[0x1FFD] = 0xE0

with open("020_blinky_opcode.bin", "wb") as outfile:
    outfile.write(bytearray(rom))
