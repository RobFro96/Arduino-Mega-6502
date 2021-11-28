void setup()
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
    PORTK = 0;
    DDRK = 0;
    Serial.begin(115200);
}

void loop()
{
    if (Serial.available())
    {
        Serial.println(Serial.read());
    }
}