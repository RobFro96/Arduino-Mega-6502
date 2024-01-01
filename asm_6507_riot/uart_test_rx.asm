RAM = 0x00

uart_buf = RAM

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

;    ldx #0xff
;startup_delay:
;    dex
;    bne startup_delay

    lda #0x01
    sta DDRB

    lda #0x02
    sta DDRA
    sta DRA

    lda #0x3A
    sta uart_buf
    jsr serial_tx

loop:
    lda DRA
    and #0x01
    bne loop
    jsr serial_rx
    lda uart_buf
    pha
    jsr serial_tx
    pla
    and #0x01
    sta DRB
    jmp loop


serial_tx:
    lda #$fd ; Inverse bit 1
    and DRA
    sta DRA ; Start bit
    lda #8 ; 2c ; 9600 = 8, 4800 = 21
    jsr delay_short ; 20 + (8-1)*8 = 76c ; Start bit total 104 cycles - 104 cycles measured
    nop ; 2c
    nop ; 2c
    ldx #8 ; 2c
serial_tx_loop:
    lsr uart_buf ; 5c
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
    
;Returns byte in A - assumes 9600 baud = ~104us/bit, 1 cycle = 1us (1 MHz)
;We should call this ASAP when RX pin goes low - let's assume it just happened (13 cycles ago)
serial_rx:
    ;Minimum 13 cycles before we get here
    lda #15 ; 1.5 period-ish ; 2 cycles - 15 for 9600 baud, 34 for 4800
    jsr delay_short ; 140c
    ldx #8 ; 2 cycles
    ;149 cycles to get here
serial_rx_loop: ;103 cycles
    lda DRA ; Read RX bit 0 ; 3 cycles
    lsr ; Shift received bit into carry - in many cases might be safe to just lsr DRA ; 2 cyclesabaa
    ror uart_buf ; Rotate into MSB 5 cycles
    lda #9 ; 2 cycles ;9 for 9600 baud, 22 for 4800 baud (add 104us == 104 / 8 = 13)
    jsr delay_short ; Delay until middle of next bit - overhead; 84 cycles
    nop ; 2c
    dex ; 2c
    bne serial_rx_loop ; 3 cycles
    ;Should already be in the middle of the stop bit
    ; We can ignore the actual stop bit and use the time for other things
    ; Received byte in inb
    rts

message:
    .text "Hello World!!!"
    .byte 10
    .byte 0

    .org 0xFFFA
    .word reset
    .word reset
    .word reset