    .org $8000
reset:
    ; LCD initialization
    lda #%00111000
    sta $7F10
    lda #%00001110
    sta $7F10
    lda #%00000110
    sta $7F10
    lda #%00000001
    sta $7F10

    ; Print Hello
    ldx #0
print_loop:
    lda message, x
    beq loop
    sta $7F11
    inx
    jmp print_loop

loop:
    jmp loop

message: .asciiz "Hello World!"

    .org $FFFA
    .word reset
    .word reset
    .word reset