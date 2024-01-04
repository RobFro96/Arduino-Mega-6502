EEPROM_PROG_LOC = 0x40
WOZMON_RAM = 0x50
UART_BUF = WOZMON_RAM
XAML = WOZMON_RAM + 1        ; Last "opened" location Low
XAMH = WOZMON_RAM + 2        ; Last "opened" location High
STL = WOZMON_RAM + 3         ; Store address Low
STH = WOZMON_RAM + 4         ; Store address High
L = WOZMON_RAM + 5           ; Hex value parsing Low
H = WOZMON_RAM + 6           ; Hex value parsing High
YSAV = WOZMON_RAM + 7        ; Used to see if hex value is given
MODE = WOZMON_RAM + 8        ; $00=XAM, $7F=STOR, $AE=BLOCK XAM

IN = WOZMON_RAM + 9          ; Input buffer

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

	.org 0xFE00
reset:
	; 6502 reset defaults
	cld
	cli
	ldx #0x7F
	txs
	
	; copy eeprom prog to RAM
	ldy #0
restore_eeprom_prog_loop:
	lda eeprom_prog, y
	sta EEPROM_PROG_LOC, y
	iny
	cpy #11
	bne restore_eeprom_prog_loop
	
	; initialize RIOT DRA for UART
	lda #0x02
	sta DDRA
	sta DRA
	
	; WOZMON
	LDA #$1B                     ; Begin with escape.
NOTCR:
	CMP #$08                     ; Backspace key?
	BEQ BACKSPACE                ; Yes.
	CMP #$1B                     ; ESC?
	BEQ ESCAPE                   ; Yes.
	INY                          ; Advance text index.
	BPL NEXTCHAR                 ; Auto ESC if line longer than 127.
	
ESCAPE:
	LDA #'#'                     ; "#".
	JSR ECHO                     ; Output it.
	
GETLINE:
	LDA #$0D                     ; Send CR
	JSR ECHO
	
	LDY #$01                     ; Initialize text index.
BACKSPACE:
	DEY                          ; Back up text index.
	BMI GETLINE                  ; Beyond start of line, reinitialize.
	
NEXTCHAR:
	JSR GETCHAR
	STA IN, Y                    ; Add to text buffer.
	JSR ECHO                     ; Display character.
	CMP #$0D                     ; CR?
	BNE NOTCR                    ; No.
	
	LDY #$FF                     ; Reset text index.
	LDA #$00                     ; For XAM mode.
	TAX                          ; X=0.
SETBLOCK:
	ASL
SETSTOR:
	ASL                          ; Leaves $7B if setting STOR mode.
	STA MODE                     ; $00 = XAM, $74 = STOR, $B8 = BLOK XAM.
BLSKIP:
	INY                          ; Advance text index.
NEXTITEM:
	LDA IN, Y                    ; Get character.
	CMP #$0D                     ; CR?
	BEQ GETLINE                  ; Yes, done this line.
	CMP #$2E                     ; "."?
	BCC BLSKIP                   ; Skip delimiter.
	BEQ SETBLOCK                 ; Set BLOCK XAM mode.
	CMP #$3A                     ; ":"?
	BEQ SETSTOR                  ; Yes, set STOR mode.
	CMP #$52                     ; "R"?
	BEQ RUN                      ; Yes, run user prog
	STX L                        ; $00 - > L.
	STX H                        ; and H.
	STY YSAV                     ; Save Y for comparison
	
NEXTHEX:
	LDA IN, Y                    ; Get character for hex test.
	EOR #$30                     ; Map digits to $0 - 9.
	CMP #$0A                     ; Digit?
	BCC DIG                      ; Yes.
	ADC #$88                     ; Map letter "A" - "F" to $FA - FF.
	CMP #$FA                     ; Hex letter?
	BCC NOTHEX                   ; No, character not hex.
DIG:
	ASL
	ASL                          ; Hex digit to MSD of A.
	ASL
	ASL
	
	LDX #$04                     ; Shift count.
HEXSHIFT:
	ASL                          ; Hex digit left, MSB to carry.
	ROL L                        ; Rotate into LSD.
	ROL H                        ; Rotate into MSD's.
	DEX                          ; Done 4 shifts?
	BNE HEXSHIFT                 ; No, loop.
	INY                          ; Advance text index.
	BNE NEXTHEX                  ; Always taken. Check next character for hex.
	
NOTHEX:
	CPY YSAV                     ; Check if L, H empty (no hex digits).
	BEQ ESCAPE                   ; Yes, generate ESC sequence.
	
	BIT MODE                     ; Test MODE byte.
	BVC NOTSTOR                  ; B6=0 is STOR, 1 is XAM and BLOCK XAM.
	
	lda #0x10
	bit STH
	bne write_eeprom
	LDA L                        ; LSD's of hex data.
	STA (STL, X)                 ; Store current 'store index'.
	jmp continue_write
write_eeprom:
	lda L
	jsr EEPROM_PROG_LOC
	
continue_write:
	INC STL                      ; Increment store index.
	BNE NEXTITEM                 ; Get next item (no carry).
	INC STH                      ; Add carry to 'store index' high order.
TONEXTITEM:
	JMP NEXTITEM                 ; Get next command item.
	
RUN:
	JMP (XAML)                   ; Run at current XAM index.
	
NOTSTOR:
	BMI XAMNEXT                  ; B7 = 0 for XAM, 1 for BLOCK XAM.
	
	LDX #$02                     ; Byte count.
SETADR:
	LDA L - 1, X                 ; Copy hex data to
	STA STL - 1, X               ; 'store index'.
	STA XAML - 1, X              ; And to 'XAM index'.
	DEX                          ; Next of 2 bytes.
	BNE SETADR                   ; Loop unless X = 0.
	
NXTPRNT:
	BNE PRDATA                   ; NE means no address to print.
	LDA #$0D                     ; CR.
	JSR ECHO                     ; Output it.
	LDA XAMH                     ; 'Examine index' high - order byte.
	JSR PRBYTE                   ; Output it in hex format.
	LDA XAML                     ; Low - order 'examine index' byte.
	JSR PRBYTE                   ; Output it in hex format.
	LDA #$3A                     ; ":".
	JSR ECHO                     ; Output it.
	
PRDATA:
	LDA #$20                     ; Blank.
	JSR ECHO                     ; Output it.
	LDA (XAML, X)                ; Get data byte at 'examine index'.
	JSR PRBYTE                   ; Output it in hex format.
XAMNEXT:
	STX MODE                     ; 0 - > MODE (XAM mode).
	LDA XAML
	CMP L                        ; Compare 'examine index' to hex data.
	LDA XAMH
	SBC H
	BCS TONEXTITEM               ; Not less, so no more data to output.
	
	INC XAML
	BNE MOD8CHK                  ; Increment 'examine index'.
	INC XAMH
	
MOD8CHK:
	LDA XAML                     ; Check low - order 'examine index' byte
	AND #$07                     ; For MOD 8 = 0
	BPL NXTPRNT                  ; Always taken.
	
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
	pha
	sta UART_BUF
	txa
	pha
	lda #$fd                     ; Inverse bit 1
	and DRA
	sta DRA                      ; Start bit
	lda #8                       ; 2c ; 9600 = 8, 4800 = 21
	jsr delay_short              ; 20 + (8 - 1) * 8 = 76c ; Start bit total 104 cycles - 104 cycles measured
	nop                          ; 2c
	nop                          ; 2c
	ldx #8                       ; 2c
serial_tx_loop:
	lsr UART_BUF                 ; 5c
	lda DRA                      ; 3c
	bcc tx0                      ; 2 / 3c
	ora #2                       ; TX bit is bit 1 ; 2c
	bcs bitset                   ; BRA 3c
tx0:
	nop                          ; 2c
	and #$fd                     ; 2c
bitset:
	sta DRA                      ; 3c
	; Delay one period - overhead ; 101c total ; 103c measured
	lda #8                       ; 2c ; 9600 8, 4800 21
	jsr delay_short              ; 20 + (8 - 1) * 8 = 76c
	dex                          ; 2c
	bne serial_tx_loop           ; 3c
	nop                          ; 2c ; Last bit 98us counted, 100us measured
	nop                          ; 2c
	nop                          ; 2c
	nop                          ; 2c
	lda DRA                      ;3c
	ora #2                       ; 2c
	sta DRA                      ; Stop bit 3c
	lda #8                       ; 2c ; 9600 8, 4800 21
	jsr delay_short
	pla
	tax
	pla
	rts
	
delay_short:
	sta WTD8DI                   ; Divide by 8 = A contains ticks to delay / 8
shortwait:
	nop                          ; Sample every 8 cycles instead of every 6
	lda READTDI
	bne shortwait
	rts
	
GETCHAR:
	LDA DRA                      ; Check status.
	AND #1                       ; Key ready?
	BNE GETCHAR                  ; Loop until ready.
SERIAL_RX:
	lda #15                      ; 1.5 period - ish ; 2 cycles - 15 for 9600 baud, 34 for 4800
	jsr delay_short              ; 140c
	ldx #8                       ; 2 cycles
.serial_rx_loop:              ;103 cycles
	lda DRA                      ; Read RX bit 0 ; 3 cycles
	lsr                          ; Shift received bit into carry - in many cases might be safe to just lsr DRA ; 2 cycles
	ror UART_BUF                 ; Rotate into MSB 5 cycles
	lda #9                       ; 2 cycles ;9 for 9600 baud, 22 for 4800 baud (add 104us == 104 / 8 = 13)
	jsr delay_short              ; Delay until middle of next bit - overhead; 84 cycles
	nop                          ; 2c
	dex                          ; 2c
	bne .serial_rx_loop          ; 3 cycles
	
	; ensure upper case case
	lda UART_BUF
	cmp #0x60
	bcs make_upper_case
	rts
make_upper_case:
	and #0xDF
	rts
eeprom_prog:
	sta (STL, X)
	lda #160
	sta WTD64DI
eeprom_prog_wait:
	lda READTDI
	bne eeprom_prog_wait
	rts
	
	.org 0xFFFA
	.word reset
	.word reset
	.word reset
