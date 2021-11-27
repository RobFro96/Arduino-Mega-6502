ORB = 0x7F00
ORA = 0x7F01
DDRB = 0x7F02
DDRA = 0x7F03

LED1 = 0x02
LED2 = 0x08
LED3 = 0x20
LED4 = 0x80

    .org 0x8000
reset:
    ldx #$ff
    txs

    lda #(LED1 + LED2 + LED3 + LED4)
    sta DDRA

loop:
    lda ORA
    ora #LED1
    sta ORA ; LED1 on

    jsr delay

    lda ORA
    eor #LED2
    sta ORA ; LED2 toogle
    
    jsr delay

    lda ORA
    and #~LED1 ; LED1 off
    sta ORA

    jsr delay

    lda ORA
    eor #LED2
    sta ORA ; LED2 toogle

    jsr delay

    jmp loop

delay:
;    nop
    ldy #0xFF
delay1:
    ldy #39
delay2:
    dey
    bne delay2
    dex
    bne delay1
    rts

    .org $FFFC
    .word reset