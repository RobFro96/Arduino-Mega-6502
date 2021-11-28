LCD_CMD = 0x9000
LCD_DATA = 0x9001

    .org 0xE000
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