ORB = 0x7F00
ORA = 0x7F01
DDRB = 0x7F02
DDRA = 0x7F03

BTN1 = 0x01
LED1 = 0x02
BTN2 = 0x04
LED2 = 0x08
BTN3 = 0x10
LED3 = 0x20
BTN4 = 0x40
LED4 = 0x80

    .org 0x8000
reset:
    ldx #$ff
    txs

    lda #(LED1 + LED2 + LED3 + LED4)
    sta DDRA
    
loop:
    lda ORA
    and #BTN1
    
    bne ledoff
    
    lda ORA
    ora #LED1
    sta ORA
    jmp loop

ledoff:
    lda ORA
    and #~LED1
    sta ORA

    jmp loop

    .org $FFFC
    .word reset