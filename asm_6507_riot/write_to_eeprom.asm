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

EEPROM_START_ADDR = 0
    ;.word 0xF080
EEPROM_PAGE_DATA = 2
    ;.byte 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31
    
    .org 0x30
    ldy #0
eeprom_write_loop:
    lda EEPROM_PAGE_DATA,y
    sta (EEPROM_START_ADDR),y
    iny
    cpy #32
    bne eeprom_write_loop
    
    ; delay 10 ms
    lda #160
    sta WTD64DI
delay_wait:
    lda READTDI
    bne delay_wait
        
    ; return to WozMon
    jmp 0xFE00
    