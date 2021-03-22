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
    lda #0xFF
    sta DDRB
    
loop:
    lda ORA
    sta ORB

    jmp loop

    .org $FFFC
    .word reset