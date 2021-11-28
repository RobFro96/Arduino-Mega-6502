counter = 0x00
update = 0x01

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

LCD_CMD = 0x7F10
LCD_DATA = 0x7F11
LCD_GOTO_LINE1 = 0x80
LCD_GOTO_LINE2 = 0xC0

    .org 0x8000
reset:
    cli
    ldx #$ff
    txs

    lda #0x82
    sta IER

    lda #32
    sta counter
    lda #1
    sta update
    
    lda #0b00111000
    jsr lcd_command
    lda #0b00001110
    jsr lcd_command
    lda #0b00000110
    jsr lcd_command
    lda #0b00000001
    jsr lcd_command
    
loop:
    lda update
    beq loop

    lda #LCD_GOTO_LINE1
    jsr lcd_command
    lda counter
    sta LCD_DATA
    
    lda #0
    sta update
    jmp loop

lcd_command:
    sta LCD_CMD
lcd_wait: 
    lda LCD_CMD
    and #0x80
    bne lcd_wait
    rts

irq:
    pha
    lda IFR
    and #CA1
    beq exit_irq
    inc counter
    inc update
    bit ORA
exit_irq:
    pla
    rti

    .org $FFFA
    .word reset
    .word reset
    .word irq