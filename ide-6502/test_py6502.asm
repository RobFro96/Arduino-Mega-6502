    ORG $8000
reset:
    LDA #%00111000
    STA $7F70
    LDA #%00001110
    STA $7F70
    LDA #%00000110
    STA $7F70
    LDA #%00000001
    STA $7F70

    LDA #$48
    STA $7F71
    LDA #$48
    STA $7F71
    LDA #$48
    STA $7F71
    LDA #$48
    STA $7F71
    

    ORG $FFFA
    DW $FFFF
    DW &reset
    DW &reset