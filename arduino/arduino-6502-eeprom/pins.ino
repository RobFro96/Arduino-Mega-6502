// Control Bus PORTK
const uint8_t RDY_BE = (1 << 1);
const uint8_t RESB = (1 << 2);
const uint8_t PHI2 = (1 << 3);
const uint8_t RWB = (1 << 4);
const uint8_t IRQB = (1 << 5);
const uint8_t NMIB = (1 << 6);
const uint8_t SYNC = (1 << 7);

// Auxillary PORTG
const uint8_t HALT_LED = (1 << 0);
const uint8_t HALT_BTN = (1 << 1);
const uint8_t EEPROM_WE = (1 << 2);

// Auxiallary PORTD
const uint8_t EEPROM_OE = (1 << 7);

void pins_init()
{
    pinMode(A8, INPUT);
    pinMode(A9, INPUT);
    pinMode(A10, INPUT);
    pinMode(A11, INPUT);
    pinMode(A12, INPUT);
    pinMode(A13, INPUT);
    pinMode(A14, INPUT);

    // ABus
    DDRC = 0;
    DDRL = 0;

    // DBus
    PORTA = 0;
    DDRA = 0;

    // CBus
    PORTK = PHI2;
    DDRK = PHI2;

    // Aux
    PORTG = EEPROM_WE;
    DDRG = HALT_LED + EEPROM_WE;
    PORTD = 0;
    DDRD = EEPROM_OE;
}

#define p_reset_l() ({ DDRK |= RESB; })
#define p_reset_h() ({ DDRK &= ~RESB; })

#define p_abus_val_l() (PINL)
#define p_abus_val_h() (PINC)
uint16_t p_abus_val()
{
    return (uint16_t)p_abus_val_l() + (((uint16_t)p_abus_val_h()) << 8);
}
#define p_abus_output() ({ DDRL = 0xFF; DDRC=0xFF; })
#define p_abus_input() ({ DDRL = 0x00; DDRC = 0x00; })
void p_abus_set(uint16_t abus)
{
    PORTL = abus;
    PORTC = abus >> 8;
}

#define p_dbus_val() (PINA)
#define p_dbus_output() ({ DDRA = 0xFF; })
#define p_dbus_input() ({ DDRA = 0x00; })
void p_dbus_set(uint8_t dbus)
{
    PORTA = dbus;
}

#define p_cbus_val() (PINK)
uint8_t p_cbus_vectors_set(uint8_t cbus)
{
    const uint8_t allowed_pulldown = IRQB + NMIB + RESB;
    DDRK = (cbus & allowed_pulldown) + (DDRK & ~allowed_pulldown);
}

#define p_phi2_l() ({ PORTK &= ~PHI2; })
#define p_phi2_h() ({ PORTK |= PHI2; })

#define p_rdy_be_l() ({ DDRK |= RDY_BE; })
#define p_rdy_be_h() ({ DDRK &= ~RDY_BE; })

#define p_eeprom_we_l() ({ PORTG &= ~EEPROM_WE; })
#define p_eeprom_we_h() ({ PORTG |= EEPROM_WE; })

#define p_eeprom_oe_l() ({ PORTD &= ~EEPROM_OE; })
#define p_eeprom_oe_h() ({ PORTD |= EEPROM_OE; })
