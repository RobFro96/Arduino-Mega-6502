    .org $8000
reset:
    lda #$2F

    ; Zero page
    sta $0000

    ; Stack
    sta $0100

    ; RAM
    sta $1000

    ; LCD
    sta $7F10

    ; PIA
    sta $7F00

loop:
    jmp loop

    .org $FFFA
    .word reset
    .word reset
    .word reset