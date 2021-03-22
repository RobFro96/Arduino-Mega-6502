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
    
    ldx #0
loop:
    jsr led_btn_update
    inx
    cpx #4
    bne loop
    ldx #0
    jmp loop

led_btn_update:
    lda ORA
    and BTNS,x
    bne ledoff
    lda ORA
    ora LEDS,x
    sta ORA
    rts
ledoff:
    lda #0xFF
    eor LEDS,x
    and ORA
    sta ORA
    rts

BTNS:
    .byte BTN1
    .byte BTN2
    .byte BTN3
    .byte BTN4
LEDS:
    .byte LED1
    .byte LED2
    .byte LED3
    .byte LED4

    .org $FFFC
    .word reset