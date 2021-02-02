    .org $8000
reset:
    lda #$2F

    ; RAM
    sta $0000

    ; LCD
    sta $7F10

    ; PIA
    sta $7F00

    .org $FFFA
    .word reset
    .word reset
    .word reset