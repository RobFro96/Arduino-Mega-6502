ORB = 0x7F00
ORA = 0x7F01
DDRB = 0x7F02
DDRA = 0x7F03
PCR = 0x7F0C
IFR = 0x7F0D
IER = 0x7F0E

LCD_CMD = 0x7F10
LCD_DATA = 0x7F11

    .org 0x8000
reset:
    cli
    ldx #$ff
    txs
    
    lda #0b00111000
    sta LCD_CMD
    lda #0b00001110
    sta LCD_CMD
    lda #0b00000110
    sta LCD_CMD
    lda #0b00000001
    sta LCD_CMD

    ldx #0
print_loop:
    lda message,x
    beq loop
    sta LCD_DATA
    inx
    jmp print_loop
    
loop:
    jmp loop

message:
    .asciiz "Hello World!"

    .org $FFFA
    .word reset
    .word reset
    .word 0