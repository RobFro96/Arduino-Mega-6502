ORB = 0x7F00
ORA = 0x7F01
DDRB = 0x7F02
DDRA = 0x7F03

    .org 0x8000
reset:
    ;cli
    ldx #$ff
    txs
    lda #0xFF
    sta DDRB

    lda #0
loop:
    sta ORB
    jmp loop

nmi:
    inc a
    rti

irq:
    dec a
    rti

    .org $FFFA
    .word nmi
    .word reset
    .word irq