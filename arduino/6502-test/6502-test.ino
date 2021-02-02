#include <SPI.h>

void setup() {
  SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE3));
  Serial.begin(9600);
  pinMode(10, OUTPUT);
  digitalWrite(10, 1);
}

void loop() {
  digitalWrite(10, 0);
  uint8_t dataH = SPI.transfer(0x00);
  uint8_t dataL = SPI.transfer(0x00);
  digitalWrite(10, 1);
  Serial.print(dataH, HEX);
  Serial.println(dataL, HEX);
}
