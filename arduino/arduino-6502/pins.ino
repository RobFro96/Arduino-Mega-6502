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
}

void pins_reset_6502()
{
    PORTK &= RESB;
    DDRK |= RESB;
}

uint16_t pins_get_abus()
{
    return (uint16_t)PINL + (((uint16_t)PINC) << 8);
}

uint8_t pins_get_abus_low_byte()
{
    return PINL;
}

uint8_t pins_get_abus_high_byte()
{
    return PINC;
}

uint8_t pins_get_dbus()
{
    return PINA;
}

uint8_t pins_get_cbus()
{
    return PINK;
}

uint8_t pins_pulldown_cbus(uint8_t cbus)
{
    const uint8_t allowed_pulldown = IRQB + NMIB + RDY_BE + RESB;
    DDRK = (cbus & allowed_pulldown) + (DDRK & ~allowed_pulldown);
}

uint8_t pins_phi2_l()
{
    PORTK &= ~PHI2;
}

uint8_t pins_phi2_h()
{
    PORTK |= PHI2;
}

void pins_write_dbus(uint8_t dbus)
{
    DDRA = 0xFF;
    PORTA = dbus;
}

void pins_clear_dbus()
{
    DDRA = 0x00;
}