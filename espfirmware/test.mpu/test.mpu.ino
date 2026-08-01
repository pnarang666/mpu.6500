#include <Wire.h>

void setup() {
  Serial.begin(115200);

  Wire.begin(21,22);

  Wire.beginTransmission(0x68);
  Wire.write(0x75); // WHO_AM_I
  Wire.endTransmission(false);

  Wire.requestFrom(0x68,1);

  if(Wire.available()) {
    uint8_t id = Wire.read();

    Serial.print("WHO_AM_I = 0x");
    Serial.println(id,HEX);
  }
}

void loop(){}
