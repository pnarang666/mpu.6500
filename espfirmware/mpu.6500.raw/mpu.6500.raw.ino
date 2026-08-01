#include <Wire.h>
#include <MPU9250_asukiaaa.h>

MPU9250_asukiaaa imu;

float gxOff=0;
float gyOff=0;
float gzOff=0;

void calibrateGyro() {

  const int N=500;

  for(int i=0;i<N;i++) {

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

  Wire.begin(21,22);

  imu.setWire(&Wire);

  imu.beginAccel();
  imu.beginGyro();

  delay(1000);

  calibrateGyro();

  Serial.println(
    "timestamp,ax,ay,az,gx,gy,gz"
  );
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

  Serial.print(micros());

  Serial.print(",");
  Serial.print(ax,4);

  Serial.print(",");
  Serial.print(ay,4);

  Serial.print(",");
  Serial.print(az,4);

  Serial.print(",");
  Serial.print(gx,3);

  Serial.print(",");
  Serial.print(gy,3);

  Serial.print(",");
  Serial.println(gz,3);

  delay(10);
}