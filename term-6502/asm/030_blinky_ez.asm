    .org 0x8000
    lda #0xFF
    sta 0x7F02   ; DDRB = 0xFF

    lda #0xA5
    sta 0x7F00   ; ORB = 0xA5

    lda #0x5A
    sta 0x7F00   ; ORB = 0x5A

    jmp 0x8005

    .org $FFFC
    .word 0x8000