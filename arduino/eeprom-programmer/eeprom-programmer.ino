#define SHIFT_DATA 10
#define SHIFT_CLK 12
#define SHIFT_LATCH 11
#define WRITE_EN 13

const uint8_t EEPROM_DATA[] = {7, 8, 9, 6, 5, 4, 3, 2};

const String HEX_DIGITS = "0123456789abcdef";

String msg = "";

void setup() {
    pinMode(SHIFT_DATA, OUTPUT);
    pinMode(SHIFT_CLK, OUTPUT);
    pinMode(SHIFT_LATCH, OUTPUT);
    digitalWrite(WRITE_EN, HIGH);
    pinMode(WRITE_EN, OUTPUT);

    Serial.begin(115200);
}

void loop() {
    if (Serial.available()) {
        char c = Serial.read();
        if (c != '\n') {
            msg = msg + c;
        } else {
            if (msg.length() > 2 * 66 + 1) {
                msg = msg.substring(0, 2 * 66 + 1);
            }
            byte data[66];
            for (int i = 0; i < 66; i++) {
                data[i] = 0xFF;
            }
            ascii_to_hex(msg.substring(1), data);
            int address = ((int)data[0] << 8) + data[1];
            address = address & 0x7FFF;

            if (msg.startsWith("r")) {
                // reading EEPROM
                read_eeprom_page(address, data + 2);
                Serial.print("r");
                print_data(data, 66);
                Serial.print("\n");

            } else if (msg.startsWith("w")) {
                // write EEPROM
                write_eeprom_page(address, data + 2);
                Serial.print("w");
                print_data(data, 2);
                Serial.print("\n");
            } else if (msg.startsWith("i")) {
                Serial.print("iRobertFromm,EEPROMProgrammer,1,2023-12\n");
            }
            msg = "";
        }
    }
}

int ascii_to_hex(String str, byte *data) {
    if (str.length() % 2 == 1) {
        str = str + '0';
    }
    str.toLowerCase();

    int length = str.length() / 2;
    for (int i = 0; i < length; i++) {
        int first_digit = HEX_DIGITS.indexOf(str[2 * i]);
        int second_digit = HEX_DIGITS.indexOf(str[2 * i + 1]);

        data[i] = 16 * first_digit + second_digit;
    }

    return length;
}

int print_data(byte *data, int length) {
    for (int i = 0; i < length; i++) {
        Serial.print(HEX_DIGITS[(data[i] >> 4) & 0xF]);
        Serial.print(HEX_DIGITS[data[i] & 0xF]);
    }
}

void set_address(int address, bool outputEnable) {
    shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST,
             (address >> 8) | (outputEnable ? 0x00 : 0x80));
    shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, address);

    digitalWrite(SHIFT_LATCH, LOW);
    digitalWrite(SHIFT_LATCH, HIGH);
    digitalWrite(SHIFT_LATCH, LOW);
}

void read_eeprom_page(int address, byte *data) {
    address = address & 0xFFC0;

    for (int pin = 0; pin < 8; pin++) {
        pinMode(EEPROM_DATA[pin], INPUT);
    }

    for (int i = 0; i < 64; i++) {
        set_address(address + i, true);

        byte data_byte = 0;
        for (int pin = 7; pin >= 0; pin--) {
            data_byte = (data_byte << 1) + digitalRead(EEPROM_DATA[pin]);
        }

        data[i] = data_byte;
    }
}

void write_eeprom_page(int address, const byte *data) {
    address = address & 0xFFC0;

    set_address(address, false);
    for (int pin = 0; pin < 8; pin++) {
        pinMode(EEPROM_DATA[pin], OUTPUT);
    }

    for (int i = 0; i < 64; i++) {
        set_address(address + i, false);

        byte data_byte = data[i];
        for (int pin = 0; pin < 8; pin++) {
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