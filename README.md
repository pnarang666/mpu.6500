# MPU / IMU Dashboard Toolkit

Small collection of ESP32 + MPU-series IMU firmware sketches and Python desktop dashboards for streaming, visualizing, logging, and inspecting accelerometer/gyroscope motion data in real time.

## What This Repository Contains

- `espfirmware/`
  Arduino/ESP32 sketches for different MPU sensor output modes.
- `imu_dashboard.py`
  Basic PyQtGraph live dashboard for accelerometer, gyroscope, and roll/pitch/yaw values.
- `imu_workstation.py`
  Desktop logger and real-time plotting tool for raw IMU streams.
- `imu_3d_dashboard.py`, `imu3d.py`
  Early 3D visualization experiments.
- `imu_dashboard_v2.py`
  Iterated dashboard variant.
- `imu_dashboard_pro/`
  Most complete workstation build, with serial auto-detection, complementary filtering, calibration, logging, and 3D OpenGL orientation display.
- `imu_log.csv`
  Example captured sensor log.

## Recommended Entry Point

If you want the most feature-complete desktop app, start with:

```bash
cd imu_dashboard_pro
python3 main.py
```

This version includes:

- serial connection management
- live accelerometer and gyroscope plots
- roll / pitch / yaw estimation
- gyro calibration
- yaw reset
- IMU logging
- OpenGL-based 3D orientation viewer
- basic RMS noise and sample-rate diagnostics

## Data Flow

Typical workflow:

1. Flash one of the ESP32 firmware sketches from `espfirmware/`.
2. Connect the board over USB serial.
3. Stream IMU values at `115200` baud.
4. Read the stream in one of the Python dashboards.
5. Visualize motion, inspect orientation, and optionally log CSV data.

## Firmware

The firmware folder contains multiple experiments and sensor targets, including:

- `mpu.6500csv/`
  Streams:
  `ax, ay, az, gx, gy, gz, roll, pitch, yaw`
- `mpu.6500basic/`
  Simpler MPU-6500 sketch variant.
- `mpu.6500.raw/`
  Raw MPU-6500 stream variant.
- `mpu.6050raw/`
  Raw MPU-6050 sketch.
- `Mpu9050/`
  MPU-9050 test sketches.

Example from `mpu.6500csv/mpu.6500csv.ino`:

- initializes I2C on pins `21,22`
- starts serial at `115200`
- calibrates gyro bias at startup
- computes roll and pitch from accelerometer
- integrates yaw from gyro Z
- prints CSV rows continuously

## Python Apps

### `imu_dashboard.py`

Basic live dashboard:

- fixed serial port path
- PyQt5 + PyQtGraph UI
- live accel and gyro plots
- roll/pitch/yaw display from streamed values

Useful for quick bring-up when the firmware already emits orientation.

### `imu_workstation.py`

Raw IMU logger and plotter:

- auto-finds `/dev/cu.usbserial*`
- logs `t, ax, ay, az, gx, gy, gz` to `imu_log.csv`
- computes roll and pitch locally from accelerometer
- useful for inspecting unfiltered raw data

### `imu_dashboard_pro/`

Most advanced version:

- auto-detects ESP32 serial ports on macOS
- expects data in the form:
  `timestamp_us,ax,ay,az,gx,gy,gz`
- uses a complementary filter for roll/pitch/yaw
- supports gyro bias calibration
- tracks sample rate and noise metrics
- includes logging and 3D OpenGL attitude rendering

## Requirements

For the pro dashboard, install:

```bash
pip install -r imu_dashboard_pro/requirements.txt
```

Current dependencies:

- `pyserial`
- `pyqt5`
- `pyqtgraph`
- `pyopengl`
- `numpy`

Depending on your platform, you may also need:

- system OpenGL support
- Qt platform plugins
- Arduino libraries such as `MPU9250_asukiaaa`

## Running

### Pro dashboard

```bash
cd imu_dashboard_pro
python3 main.py
```

### Basic dashboard

```bash
python3 imu_dashboard.py
```

### Raw workstation logger

```bash
python3 imu_workstation.py
```

## Serial Notes

- Default baud rate is `115200`.
- Some scripts assume macOS device names like `/dev/cu.usbserial-0001`.
- If your board appears under a different path, update the port logic or constants in the relevant script.

## Current State

This repository is best understood as a practical IMU experimentation workspace rather than a polished library. It contains several parallel dashboard prototypes and firmware variants, with `imu_dashboard_pro/` as the clearest “main” implementation.

## Possible Cleanup Direction

If you continue developing this project, a sensible next step would be:

- choose one canonical firmware format
- choose one canonical desktop app
- document supported sensor boards explicitly
- add a wiring diagram and calibration procedure
- separate archived experiments from the recommended path
