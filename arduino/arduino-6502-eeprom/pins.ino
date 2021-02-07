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
    PORTG |= EEPROM_WE;
    DDRG |= HALT_LED + EEPROM_WE;
    PORTD = 0;
    DDRD = EEPROM_OE;
}
