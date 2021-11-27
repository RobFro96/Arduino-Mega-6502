DDRB = 0x7F02
ORB = 0x7F00

    .org 0x8000
reset:
    lda #0xFF
    sta DDRB   ; DDRB = 0xFF

loop:
    lda #0xA5
    sta ORB   ; ORB = 0xA5

    lda #0x5A
    sta ORB   ; ORB = 0x5A

    jmp loop

    .org 0xFFFC
    .word reset