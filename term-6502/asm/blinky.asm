    .org $8000
reset:
    lda #$FF
    sta $7F02   ; DDRB = 0xFF

loop:
    lda #$55
    sta $7F00   ; ORB = 0x55

    lda #$AA
    sta $7F00   ; ORB = 0xAA

    jmp loop

    .org $FFFA
    .word reset
    .word reset
    .word reset