#include <Wire.h>
#include <MPU9250_asukiaaa.h>

MPU9250_asukiaaa imu;

float gxOff = 0;
float gyOff = 0;
float gzOff = 0;

void calibrateGyro() {
  const int N = 500;

  for (int i = 0; i < N; i++) {
    imu.gyroUpdate();

    gxOff += imu.gyroX();
    gyOff += imu.gyroY();
    gzOff += imu.gyroZ();

    delay(5);
  }

  gxOff /= N;
  gyOff /= N;
  gzOff /= N;
}

void setup() {
  Serial.begin(115200);

  Wire.begin(21, 22);

  imu.setWire(&Wire);

  imu.beginAccel();
  imu.beginGyro();

  Serial.println("Calibrating...");
  calibrateGyro();
  Serial.println("Done");
}

void loop() {

  imu.accelUpdate();
  imu.gyroUpdate();

  float ax = imu.accelX();
  float ay = imu.accelY();
  float az = imu.accelZ();

  float gx = imu.gyroX() - gxOff;
  float gy = imu.gyroY() - gyOff;
  float gz = imu.gyroZ() - gzOff;

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

  delay(100);
}