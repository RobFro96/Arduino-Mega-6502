#define SHIFT_DATA 10
#define SHIFT_CLK 12
#define SHIFT_LATCH 11
#define WRITE_EN 13

const uint8_t EEPROM_DATA[] = {7, 8, 9, 6, 5, 4, 3, 2};

byte data[64];

void setup()
{
  // put your setup code here, to run once:
  pinMode(SHIFT_DATA, OUTPUT);
  pinMode(SHIFT_CLK, OUTPUT);
  pinMode(SHIFT_LATCH, OUTPUT);
  digitalWrite(WRITE_EN, HIGH);
  pinMode(WRITE_EN, OUTPUT);
  Serial.begin(115200);

  for (int i = 0; i < 64; i++)
  {
    data[i] = i;
  }

  for (int address = 0; address < 0x100; address += 64)
  {
    erase_eeprom_page(address);
  }

  write_eeprom_page(0, data);
  print_contents();
}

void loop()
{
  // put your main code here, to run repeatedly:
}

/*
 * Output the address bits and outputEnable signal using shift registers.
 */
void setAddress(int address, bool outputEnable)
{
  shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, (address >> 8) | (outputEnable ? 0x00 : 0x80));
  shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, address);

  digitalWrite(SHIFT_LATCH, LOW);
  digitalWrite(SHIFT_LATCH, HIGH);
  digitalWrite(SHIFT_LATCH, LOW);
}

/*
 * Read a byte from the EEPROM at the specified address.
 */
byte read_eeprom(int address)
{
  for (int pin = 0; pin < 8; pin++)
  {
    pinMode(EEPROM_DATA[pin], INPUT);
  }
  setAddress(address, true);

  byte data = 0;
  for (int pin = 7; pin >= 0; pin--)
  {
    data = (data << 1) + digitalRead(EEPROM_DATA[pin]);
  }
  return data;
}

/*
 * Write a byte to the EEPROM at the specified address.
 */
void write_eeprom(int address, byte data)
{
  setAddress(address, false);
  for (int pin = 0; pin < 8; pin++)
  {
    pinMode(EEPROM_DATA[pin], OUTPUT);
  }

  for (int pin = 0; pin < 8; pin++)
  {
    digitalWrite(EEPROM_DATA[pin], data & 1);
    data = data >> 1;
  }
  digitalWrite(WRITE_EN, LOW);
  delayMicroseconds(1);
  digitalWrite(WRITE_EN, HIGH);
  delay(10);
}

void write_eeprom_page(int address, byte *data)
{
  address = address & 0xFFC0;

  setAddress(address, false);
  for (int pin = 0; pin < 8; pin++)
  {
    pinMode(EEPROM_DATA[pin], OUTPUT);
  }

  for (int i = 0; i < 64; i++)
  {
    setAddress(address + i, false);

    byte data_byte = data[i];
    for (int pin = 0; pin < 8; pin++)
    {
      digitalWrite(EEPROM_DATA[pin], data_byte & 1);
      data_byte = data_byte >> 1;
    }

    digitalWrite(WRITE_EN, LOW);
    delayMicroseconds(1);
    digitalWrite(WRITE_EN, HIGH);
    delayMicroseconds(1);
  }

  delay(10);
}

void erase_eeprom_page(int address)
{
  address = address & 0xFFC0;

  setAddress(address, false);
  for (int pin = 0; pin < 8; pin++)
  {
    pinMode(EEPROM_DATA[pin], OUTPUT);
    digitalWrite(EEPROM_DATA[pin], 1);
  }

  for (int i = 0; i < 64; i++)
  {
    setAddress(address + i, false);
    digitalWrite(WRITE_EN, LOW);
    delayMicroseconds(1);
    digitalWrite(WRITE_EN, HIGH);
    delayMicroseconds(1);
  }

  delay(10);
}

/*
 * Read the contents of the EEPROM and print them to the serial monitor.
 */
void print_contents()
{
  for (int base = 0; base <= 255; base += 16)
  {
    byte data[16];
    for (int offset = 0; offset <= 15; offset += 1)
    {
      data[offset] = read_eeprom(base + offset);
    }

    char buf[80];
    sprintf(buf, "%03x:  %02x %02x %02x %02x %02x %02x %02x %02x   %02x %02x %02x %02x %02x %02x %02x %02x",
            base, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7],
            data[8], data[9], data[10], data[11], data[12], data[13], data[14], data[15]);

    Serial.println(buf);
  }
}
