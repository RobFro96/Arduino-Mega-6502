    .org $8000
reset:
    ; LCD initialization
    lda #%00111000
    sta $7F70
    lda #%00001110
    sta $7F70
    lda #%00000110
    sta $7F70
    lda #%00000001
    sta $7F70

    ; Print Hello
    lda #"H"
    sta $7F71
    lda #"e"
    sta $7F71
    lda #"l"
    sta $7F71
    lda #"l"
    sta $7F71
    lda #"o"
    sta $7F71
    

    .org $FFFA
    .word reset
    .word reset
    .word reset