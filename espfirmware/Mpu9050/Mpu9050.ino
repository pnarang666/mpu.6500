#include <Wire.h>
#include <MPU9250_asukiaaa.h>

MPU9250_asukiaaa mySensor;

#define SDA_PIN 21
#define SCL_PIN 22
#define MPU_ADDR 0x68

#define CALIB_SAMPLES 200

float gyroXoffset = 0;
float gyroYoffset = 0;
float gyroZoffset = 0;

void enableMagBypass() {
  // Wake MPU9250
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B); // PWR_MGMT_1
  Wire.write(0x00);
  Wire.endTransmission();
  delay(100);

  // Enable bypass mode for AK8963 magnetometer
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x37); // INT_PIN_CFG
  Wire.write(0x02); // BYPASS_EN
  Wire.endTransmission();
  delay(100);
}

void calibrateGyro() {
  Serial.println("Keep sensor completely still...");
  delay(2000);

  gyroXoffset = 0;
  gyroYoffset = 0;
  gyroZoffset = 0;

  for (int i = 0; i < CALIB_SAMPLES; i++) {
    mySensor.gyroUpdate();

    gyroXoffset += mySensor.gyroX();
    gyroYoffset += mySensor.gyroY();
    gyroZoffset += mySensor.gyroZ();

    delay(10);
  }

  gyroXoffset /= CALIB_SAMPLES;
  gyroYoffset /= CALIB_SAMPLES;
  gyroZoffset /= CALIB_SAMPLES;

  Serial.println("Gyro calibration complete");

  Serial.print("X offset = ");
  Serial.println(gyroXoffset);

  Serial.print("Y offset = ");
  Serial.println(gyroYoffset);

  Serial.print("Z offset = ");
  Serial.println(gyroZoffset);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("MPU9250 + ESP32");

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000);

  enableMagBypass();

  mySensor.setWire(&Wire);

  mySensor.beginAccel();
  mySensor.beginGyro();
  mySensor.beginMag();

  Serial.println("Sensors initialized");

  calibrateGyro();
}

void loop() {

  mySensor.accelUpdate();
  mySensor.gyroUpdate();
  mySensor.magUpdate();

  float ax = mySensor.accelX();
  float ay = mySensor.accelY();
  float az = mySensor.accelZ();

  float gx = mySensor.gyroX() - gyroXoffset;
  float gy = mySensor.gyroY() - gyroYoffset;
  float gz = mySensor.gyroZ() - gyroZoffset;

  float mx = mySensor.magX();
  float my = mySensor.magY();
  float mz = mySensor.magZ();

  Serial.println("--------------------------------");

  Serial.print("Accel X: ");
  Serial.print(ax, 3);
  Serial.print("  Y: ");
  Serial.print(ay, 3);
  Serial.print("  Z: ");
  Serial.println(az, 3);

  Serial.print("Gyro  X: ");
  Serial.print(gx, 3);
  Serial.print("  Y: ");
  Serial.print(gy, 3);
  Serial.print("  Z: ");
  Serial.println(gz, 3);

  Serial.print("Mag   X: ");
  Serial.print(mx, 3);
  Serial.print("  Y: ");
  Serial.print(my, 3);
  Serial.print("  Z: ");
  Serial.println(mz, 3);

  delay(500);
}

