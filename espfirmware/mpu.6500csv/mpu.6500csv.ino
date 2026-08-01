#include <Wire.h>
#include <MPU9250_asukiaaa.h>

MPU9250_asukiaaa imu;

float gxOff = 0;
float gyOff = 0;
float gzOff = 0;

float yaw = 0.0;

unsigned long lastMicros;

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

  Wire.begin(21,22);

  imu.setWire(&Wire);

  imu.beginAccel();
  imu.beginGyro();

  calibrateGyro();

  lastMicros = micros();

  Serial.println("ax,ay,az,gx,gy,gz,roll,pitch,yaw");
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

  unsigned long now = micros();

  float dt = (now - lastMicros) / 1000000.0f;

  lastMicros = now;

  float roll =
      atan2(ay, az) * 180.0 / PI;

  float pitch =
      atan2(
        -ax,
        sqrt(ay * ay + az * az)
      ) * 180.0 / PI;

  yaw += gz * dt;

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

  Serial.print(gz,3);
  Serial.print(",");

  Serial.print(roll,2);
  Serial.print(",");

  Serial.print(pitch,2);
  Serial.print(",");

  Serial.println(yaw,2);

  delay(10);
}