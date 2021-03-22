ORB = 0x7F00
ORA = 0x7F01
DDRB = 0x7F02
DDRA = 0x7F03
PCR = 0x7F0C
IFR = 0x7F0D
IER = 0x7F0E

CA1 = 0x02
CA2 = 0x01
CB1 = 0x10
CB2 = 0x08

    .org 0x8000
reset:
    cli
    ldx #$ff
    txs
    
    lda #0xFF
    sta DDRB

    lda #0
    sta PCR
    sta IFR

    lda #0x82
    sta IER

    lda #0
    sta ORB
loop:
    jmp loop

irq:
    lda IFR
    and #CA1
    beq exit_irq
    inc ORB
    bit ORA
exit_irq:
    rti

    .org $FFFA
    .word reset
    .word reset
    .word irq