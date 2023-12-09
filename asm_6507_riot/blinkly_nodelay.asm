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
    lda #0xFF
    sta DDRB   ; DDRB = 0xFF

loop:
    lda #0xA5
    sta DRB

    lda #0x5A
    sta DRB

    jmp loop

    .org 0xFFFA
    .word reset
    .word reset
    .word reset