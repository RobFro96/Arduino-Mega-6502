void setup()
{
    pins_init();
    Serial.begin(115200);

    pinMode(13, 1);
    digitalWrite(13, 0);

    Serial.write(0);
}

void loop()
{
    if (Serial.available())
    {
        protocol_on_rxd();
    }
}
