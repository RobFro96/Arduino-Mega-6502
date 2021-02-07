    .org $8000
reset:
    lda #$FF
    sta $7F02   ; DDRB = 0xFF

    lda #0
    sta $0000

loop:
    lda $0000
    adc #1

    sta $7F00
    sta $0000

    lda #$FF

    jmp loop

    .org $FFFA
    .word reset
    .word reset
    .word reset