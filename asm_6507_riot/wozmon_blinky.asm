RIOT = 0x80

DRA     = RIOT + 0x00
DDRA    = RIOT + 0x01
DRB     = RIOT + 0x02
DDRB    = RIOT + 0x03

READTDI = RIOT + 0x04
WTD1DI  = RIOT + 0x14
WTD8DI  = RIOT + 0x15
WTD64DI = RIOT + 0x16
WTD1KDI = RIOT + 0x17

    .org 0
reset:
    lda #0xFF
    sta DDRB

    ldx #0
loop:
    inx
    stx DRB
    lda #255
    jsr delay
    jmp loop

delay:
    sta WTD1KDI
delay_wait:
    nop ; Sample every 8 cycles instead of every 6
    lda READTDI
    bne delay_wait
    rts