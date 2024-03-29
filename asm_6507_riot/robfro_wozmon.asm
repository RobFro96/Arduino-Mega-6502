EEPROM_PROG_LOC = 0x40
WOZMON_RAM = 0x50
UART_BUF = WOZMON_RAM
UART_CONF = WOZMON_RAM + 1	; BIT0=0: upper case only, BIT1=0: wozmon echo activated, BIT2=1: only output with ECHO_FORCE
XAML = WOZMON_RAM + 2        ; Last "opened" location Low
XAMH = WOZMON_RAM + 3        ; Last "opened" location High
STL = WOZMON_RAM + 4         ; Store address Low
STH = WOZMON_RAM + 5         ; Store address High
HEXL = WOZMON_RAM + 6        ; Hex value parsing Low
HEXH = WOZMON_RAM + 7        ; Hex value parsing High
YSAV = WOZMON_RAM + 8        ; Used to see if hex value is given
MODE = WOZMON_RAM + 9        ; $00=XAM, $7F=STOR, $AE=BLOCK XAM
INBUF = WOZMON_RAM + 10       ; Input buffer

RIOT = 0x80
DRA = RIOT + 0x00
DDRA = RIOT + 0x01
DRB = RIOT + 0x02
DDRB = RIOT + 0x03
READTDI = RIOT + 0x04
WTD1DI = RIOT + 0x14
WTD8DI = RIOT + 0x15
WTD64DI = RIOT + 0x16
WTD1KDI = RIOT + 0x17
	
	.org 0xF000
USER_SPACE:
	lda #0x80
	sta DDRB
	ldx #0
.print_loop:
    lda .user_message,x
    beq .loop
    jsr ECHO
    inx
	jmp .print_loop

.loop:
	lda #0x80
	eor DRB
	sta DRB
	lda #255
	sta WTD1KDI
	jsr DELAY_WAIT
	jmp .loop

.user_message:
	.asciiz "\rUSER SPACE\r"

	.org 0xFE00
RESET:
	; 6502 reset defaults
	cld
	cli
	ldx #0x7F
	txs

	; initialize RIOT DRA for UART
	lda #0x02
	sta DDRA
	sta DRA

	; is boot button pressed?
	lda #4
	bit DRA
	beq .launch_wozmon ; PA2 = L -> WOZMON
	jmp USER_SPACE   ; else PA2 = H -> USER_SPACE
	
.launch_wozmon:
	; initialize UART_CONF
	lda #0
	sta UART_CONF

	; autohold boot button
	lda #0x6
	sta DDRA

	; copy eeprom prog to RAM
	ldy #0
.restore_eeprom_prog_loop:
	lda EEPROM_PROG, y
	sta EEPROM_PROG_LOC, y
	iny
	cpy #11
	bne .restore_eeprom_prog_loop
	
	; WOZMON
	LDA #$1B                     ; Begin with escape.
.nocr:
	CMP #$08                     ; Backspace key?
	BEQ .backspace               ; Yes.
	CMP #$1B                     ; ESC?
	BEQ .escape                  ; Yes.
	INY                          ; Advance text index.
	BPL .nextchar                ; Auto ESC if line longer than 127.
	
.escape:
	LDA #'#'                     ; "#".
	JSR ECHO                     ; Output it.
	
.getline:
	LDA #$0D                     ; Send CR
	JSR ECHO_FORCE
	
	LDY #$01                     ; Initialize text index.
.backspace:
	DEY                          ; Back up text index.
	BMI .getline                 ; Beyond start of line, reinitialize.
	
.nextchar:
	JSR GETCHAR
	STA INBUF, Y                 ; Add to text buffer.

	lda #2
	bit UART_CONF				; echo charachter actived in UART_CONF?
	bne .no_echo				; BIT1 = 1: no echo
	lda INBUF, Y
	JSR ECHO                     ; Display character.

.no_echo:
	LDA INBUF, Y
	CMP #$0D                     ; CR?
	BNE .nocr                   ; No.
	
	LDY #$FF                     ; Reset text index.
	LDA #$00                     ; For XAM mode.
	TAX                          ; X=0.
.setblock:
	ASL
.setstor:
	ASL                          ; Leaves $7B if setting STOR mode.
	STA MODE                     ; $00 = XAM, $74 = STOR, $B8 = BLOK XAM.
.blskip:
	INY                          ; Advance text index.
.nextitem:
	LDA INBUF, Y                 ; Get character.
	CMP #$0D                     ; CR?
	BEQ .getline                 ; Yes, done this line.
	CMP #$2E                     ; "."?
	BCC .blskip                   ; Skip delimiter.
	BEQ .setblock                 ; Set BLOCK XAM mode.
	CMP #$3A                     ; ":"?
	BEQ .setstor                  ; Yes, set STOR mode.
	CMP #$52                     ; "R"?
	BEQ .run                      ; Yes, run user prog
	STX HEXL                     ; $00 - > L.
	STX HEXH                     ; and H.
	STY YSAV                     ; Save Y for comparison
	
.nexthex:
	LDA INBUF, Y                 ; Get character for hex test.
	EOR #$30                     ; Map digits to $0 - 9.
	CMP #$0A                     ; Digit?
	BCC .dig                      ; Yes.
	ADC #$88                     ; Map letter "A" - "F" to $FA - FF.
	CMP #$FA                     ; Hex letter?
	BCC .hothex                   ; No, character not hex.
.dig:
	ASL
	ASL                          ; Hex digit to MSD of A.
	ASL
	ASL
	
	LDX #$04                     ; Shift count.
.hexshift:
	ASL                          ; Hex digit left, MSB to carry.
	ROL HEXL                     ; Rotate into LSD.
	ROL HEXH                     ; Rotate into MSD's.
	DEX                          ; Done 4 shifts?
	BNE .hexshift                 ; No, loop.
	INY                          ; Advance text index.
	BNE .nexthex                  ; Always taken. Check next character for hex.
	
.hothex:
	CPY YSAV                     ; Check if L, H empty (no hex digits).
	BEQ .escape                  ; Yes, generate ESC sequence.
	
	BIT MODE                     ; Test MODE byte.
	BVC .notstor                  ; B6=0 is STOR, 1 is XAM and BLOCK XAM.

	lda #0x10	; is memory in EEPROM?
	bit STH
	bne .write_eeprom		
	LDA HEXL                     ; no: store in RAM, LSD's of hex data.
	STA (STL, X)                 ; Store current 'store index'.
	jmp .afterwrite
.write_eeprom:					; yes: store in EEPROM
	lda HEXL					
	jsr EEPROM_PROG_LOC			; call EEPROM store program located in RAM
.afterwrite:
	INC STL                      ; Increment store index.
	BNE .nextitem                 ; Get next item (no carry).
	INC STH                      ; Add carry to 'store index' high order.
.tonextitem:
	JMP .nextitem                 ; Get next command item.
	
.run:
	JMP (XAML)                   ; Run at current XAM index.
	
.notstor:
	BMI .xamnext                  ; B7 = 0 for XAM, 1 for BLOCK XAM.
	
	LDX #$02                     ; Byte count.
.setaddr:
	LDA HEXL - 1, X              ; Copy hex data to
	STA STL - 1, X               ; 'store index'.
	STA XAML - 1, X              ; And to 'XAM index'.
	DEX                          ; Next of 2 bytes.
	BNE .setaddr                   ; Loop unless X = 0.
	
.nextprint:
	BNE .printdata                   ; NE means no address to print.
	LDA #$0D                     ; CR.
	JSR ECHO                     ; Output it.
	LDA XAMH                     ; 'Examine index' high - order byte.
	JSR PRBYTE                   ; Output it in hex format.
	LDA XAML                     ; Low - order 'examine index' byte.
	JSR PRBYTE                   ; Output it in hex format.
	LDA #$3A                     ; ":".
	JSR ECHO                     ; Output it.
	
.printdata:
	LDA #$20                     ; Blank.
	JSR ECHO                     ; Output it.
	LDA (XAML, X)                ; Get data byte at 'examine index'.
	JSR PRBYTE                   ; Output it in hex format.
.xamnext:
	STX MODE                     ; 0 - > MODE (XAM mode).
	LDA XAML
	CMP HEXL                     ; Compare 'examine index' to hex data.
	LDA XAMH
	SBC HEXH
	BCS .tonextitem               ; Not less, so no more data to output.
	
	INC XAML
	BNE .mod8check                  ; Increment 'examine index'.
	INC XAMH
	
.mod8check:
	LDA XAML                     ; Check low - order 'examine index' byte
	AND #$07                     ; For MOD 8 = 0
	JMP .nextprint                  ; Always taken.
	
PRBYTE:
	PHA                          ; Save A for LSD.
	LSR
	LSR
	LSR                          ; MSD to LSD position.
	LSR
	JSR PRHEX                    ; Output hex digit.
	PLA                          ; Restore A.
	
PRHEX:
	AND #$0F                     ; Mask LSD for hex print.
	ORA #$30                     ; Add "0".
	CMP #$3A                     ; Digit?
	BCC ECHO                     ; Yes, output it.
	ADC #$06                     ; Add offset for letter.
	
ECHO:
	sta UART_BUF
	lda #4
	bit UART_CONF  ; BIT2 = 1: only force echo
	beq .echo_force_prepare
	lda UART_BUF
	rts
.echo_force_prepare
	lda UART_BUF
ECHO_FORCE:
	sta UART_BUF
	pha
	txa
	pha
	lda #$fd                     ; Inverse bit 1
	and DRA
	sta DRA                      ; Start bit
	lda #8                       ; 2c ; 9600 = 8, 4800 = 21
	jsr DELAY_DIV8              ; 20 + (8 - 1) * 8 = 76c ; Start bit total 104 cycles - 104 cycles measured
	nop                          ; 2c
	nop                          ; 2c
	ldx #8                       ; 2c
.echo_loop:
	lsr UART_BUF                 ; 5c
	lda DRA                      ; 3c
	bcc .transmit_zero                      ; 2 / 3c
	ora #2                       ; TX bit is bit 1 ; 2c
	bcs .set_bit                   ; BRA 3c
.transmit_zero:
	nop                          ; 2c
	and #$fd                     ; 2c
.set_bit:
	sta DRA                      ; 3c
	; Delay one period - overhead ; 101c total ; 103c measured
	lda #8                       ; 2c ; 9600 8, 4800 21
	jsr DELAY_DIV8              ; 20 + (8 - 1) * 8 = 76c
	dex                          ; 2c
	bne .echo_loop           ; 3c
	nop                          ; 2c ; Last bit 98us counted, 100us measured
	nop                          ; 2c
	nop                          ; 2c
	nop                          ; 2c
	lda DRA                      ;3c
	ora #2                       ; 2c
	sta DRA                      ; Stop bit 3c
	lda #8                       ; 2c ; 9600 8, 4800 21
	jsr DELAY_DIV8
	pla
	tax
	pla
	rts
	
DELAY_DIV8:
	sta WTD8DI                   ; Divide by 8 = A contains ticks to delay / 8
DELAY_WAIT:
	nop                          ; Sample every 8 cycles instead of every 6
	lda READTDI
	bne DELAY_WAIT
	rts
	
GETCHAR:
	LDA DRA                      ; Check status.
	AND #1                       ; Key ready?
	BNE GETCHAR                  ; Loop until ready.
SERIAL_RX:
	lda #15                      ; 1.5 period - ish ; 2 cycles - 15 for 9600 baud, 34 for 4800
	jsr DELAY_DIV8              ; 140c
	ldx #8                       ; 2 cycles
.serial_rx_loop:              ;103 cycles
	lda DRA                      ; Read RX bit 0 ; 3 cycles
	lsr                          ; Shift received bit into carry - in many cases might be safe to just lsr DRA ; 2 cycles
	ror UART_BUF                 ; Rotate into MSB 5 cycles
	lda #9                       ; 2 cycles ;9 for 9600 baud, 22 for 4800 baud (add 104us == 104 / 8 = 13)
	jsr DELAY_DIV8              ; Delay until middle of next bit - overhead; 84 cycles
	nop                          ; 2c
	dex                          ; 2c
	bne .serial_rx_loop          ; 3 cycles
	
	; ensure upper case case
	lda #1
	bit UART_CONF				; upper case force activate?
	beq .check_uppercase				; BIT1 = 0: make upper case
	lda UART_BUF
	rts
	
.check_uppercase:	
	lda UART_BUF
	cmp #0x60
	bcs .make_upper_case
	rts
.make_upper_case:
	and #0xDF
	rts

EEPROM_PROG:
	sta (STL, X)
	lda #160
	sta WTD64DI
.eeprom_prog_wait:
	lda READTDI
	bne .eeprom_prog_wait
	rts
	
	.org 0xFFFA
	.word RESET
	.word RESET
	.word RESET
