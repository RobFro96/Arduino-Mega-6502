const uint8_t RDY_BE = (1 << 1);
const uint8_t RESB = (1 << 2);
const uint8_t PHI2 = (1 << 3);
const uint8_t RWB = (1 << 4);
const uint8_t IRQB = (1 << 5);
const uint8_t NMIB = (1 << 6);
const uint8_t SYNC = (1 << 7);

void setup()
{
    pins_init();
    Serial.begin(115200);
    memory_init();

    pinMode(13, 1);
    digitalWrite(13, 0);

    pins_reset_6502();

    Serial.write(0);
}

void loop()
{
    if (Serial.available())
    {
        protocol_on_rxd();
    }
}
