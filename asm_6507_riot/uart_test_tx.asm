RAM = 0x00

inb     = RAM
outb    = RAM + 1

RIOT = 0x80

DRA     = RIOT + 0x00 ;DRA ('A' side data register)
DDRA    = RIOT + 0x01 ;DDRA ('A' side data direction register)
DRB     = RIOT + 0x02 ;DRB ('B' side data register)
DDRB    = RIOT + 0x03 ;('B' side data direction register)
READTDI = RIOT + 0x04 ;Read timer (disable interrupt)

WEDGC   = RIOT + 0x04 ;Write edge-detect control (negative edge-detect,disable interrupt)
RRIFR   = RIOT + 0x05 ;Read interrupt flag register (bit 7 = timer, bit 6 PA7 edge-detect) Clear PA7 flag
A7PEDI  = RIOT + 0x05 ;Write edge-detect control (positive edge-detect,disable interrupt)
A7NEEI  = RIOT + 0x06 ;Write edge-detect control (negative edge-detect, enable interrupt)
A7PEEI  = RIOT + 0x07 ;Write edge-detect control (positive edge-detect enable interrupt)

READTEI = RIOT + 0x0C ;Read timer (enable interrupt)
WTD1DI  = RIOT + 0x14 ; Write timer (divide by 1, disable interrupt)
WTD8DI  = RIOT + 0x15 ;Write timer (divide by 8, disable interrupt)
WTD64DI = RIOT + 0x16 ;Write timer (divide by 64, disable interrupt)
WTD1KDI = RIOT + 0x17 ;Write timer (divide by 1024, disable interrupt)

WTD1EI  = RIOT + 0x1C ;Write timer (divide by 1, enable interrupt)
WTD8EI  = RIOT + 0x1D ;Write timer (divide by 8, enable interrupt)
WTD64EI = RIOT + 0x1E ;Write timer (divide by 64, enable interrupt)
WTD1KEI = RIOT + 0x1F ;Write timer (divide by 1024, enable interrupt)

    .org 0xFF00
reset:
    lda #0x02
    sta DDRA

    ldy #0
print_loop:
    lda message,y
    beq loop
    jsr serial_tx
    iny
    jmp print_loop
    
loop:
    jmp loop


serial_tx:
    sta outb
    lda #$fd ; Inverse bit 1
    and DRA
    sta DRA ; Start bit
    lda #8 ; 2c ; 9600 = 8, 4800 = 21
    jsr delay_short ; 20 + (8-1)*8 = 76c ; Start bit total 104 cycles - 104 cycles measured
    nop ; 2c
    nop ; 2c
    ldx #8 ; 2c
serial_tx_loop:
    lsr outb ; 5c
    lda DRA ; 3c
    bcc tx0 ; 2/3c
    ora #2 ; TX bit is bit 1 ; 2c
    bcs bitset ; BRA 3c
tx0:
    nop ; 2c
    and #$fd ; 2c
bitset:
    sta DRA ; 3c
    ; Delay one period - overhead ; 101c total ; 103c measured
    lda #8 ; 2c ; 9600 8, 4800 21
    jsr delay_short ; 20 + (8-1)*8 = 76c
    dex ; 2c
    bne serial_tx_loop ; 3c
    nop ; 2c ; Last bit 98us counted, 100us measured
    nop ; 2c
    nop ; 2c
    nop ; 2c
    lda DRA ;3c
    ora #2 ; 2c
    sta DRA ; Stop bit 3c
    lda #8 ; 2c ; 9600 8, 4800 21
    jsr delay_short
    rts

delay_short:
    sta WTD8DI ; Divide by 8 = A contains ticks to delay/8
shortwait:
    nop ; Sample every 8 cycles instead of every 6
    lda READTDI
    bne shortwait
    rts

message:
    .text "Hello World!!!"
    .byte 10
    .byte 0

    .org 0xFFFA
    .word reset
    .word reset
    .word reset