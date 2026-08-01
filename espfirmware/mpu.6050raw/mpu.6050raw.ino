#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

Adafruit_MPU6050 mpu;

float gxBias = 0;
float gyBias = 0;
float gzBias = 0;

void calibrateGyro() {
  sensors_event_t a, g, temp;

  Serial.println("CALIBRATING");

  for (int i = 0; i < 500; i++) {
    mpu.getEvent(&a, &g, &temp);

    gxBias += g.gyro.x;
    gyBias += g.gyro.y;
    gzBias += g.gyro.z;

    delay(5);
  }

  gxBias /= 500.0;
  gyBias /= 500.0;
  gzBias /= 500.0;

  Serial.println("READY");
}

void setup() {
  Serial.begin(115200);

  Wire.begin(21, 22);

  if (!mpu.begin()) {
    Serial.println("MPU6050 NOT FOUND");
    while (1);
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  delay(1000);

  calibrateGyro();
}

void loop() {

  sensors_event_t a, g, temp;

  mpu.getEvent(&a, &g, &temp);

  uint32_t ts = micros();

  // m/s² → g
  float ax = a.acceleration.x / 9.80665f;
  float ay = a.acceleration.y / 9.80665f;
  float az = a.acceleration.z / 9.80665f;

  // rad/s → deg/s
  float gx = (g.gyro.x - gxBias) * 180.0f / PI;
  float gy = (g.gyro.y - gyBias) * 180.0f / PI;
  float gz = (g.gyro.z - gzBias) * 180.0f / PI;

  Serial.print(ts);
  Serial.print(",");

  Serial.print(ax, 4);
  Serial.print(",");

  Serial.print(ay, 4);
  Serial.print(",");

  Serial.print(az, 4);
  Serial.print(",");

  Serial.print(gx, 3);
  Serial.print(",");

  Serial.print(gy, 3);
  Serial.print(",");

  Serial.println(gz, 3);

  delay(5);   // ~200 Hz
}