import numpy as np
import time

class IMUFilter:
    def __init__(self, alpha=0.98):
        self.alpha = alpha
        
        # State: Roll, Pitch, Yaw (Degrees)
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        
        # Gyro offsets (deg/s)
        self.gyro_bias = np.array([0.0, 0.0, 0.0])
        
        # Buffer for noise calculation
        self.accel_buffer = []
        self.gyro_buffer = []
        self.buffer_size = 500
        
        # For sample rate calculation
        self.last_ts = None
        self.dt = 0.01 # Default dt
        
    def reset_yaw(self):
        self.yaw = 0.0

    def calibrate_gyro(self, samples):
        """Expects a list of [gx, gy, gz] samples"""
        if not samples:
            return
        data = np.array(samples)
        self.gyro_bias = np.mean(data, axis=0)
        return self.gyro_bias

    def update(self, ts_us, ax, ay, az, gx, gy, gz):
        # Calculate dt
        if self.last_ts is not None:
            self.dt = (ts_us - self.last_ts) / 1000000.0
            if self.dt <= 0 or self.dt > 0.1: # Catch anomalies
                self.dt = 0.01
        self.last_ts = ts_us

        # Apply calibration
        gx -= self.gyro_bias[0]
        gy -= self.gyro_bias[1]
        gz -= self.gyro_bias[2]

        # Accelerometer Roll/Pitch
        # atan2(ay, az) gives roll
        # atan2(-ax, sqrt(ay^2 + az^2)) gives pitch
        accel_roll = np.degrees(np.arctan2(ay, az))
        accel_pitch = np.degrees(np.arctan2(-ax, np.sqrt(ay*ay + az*az)))

        # Complementary Filter
        # Roll: gx is rate around X
        # Pitch: gy is rate around Y
        # Yaw: gz is rate around Z (Yaw is gyro only)
        
        self.roll = self.alpha * (self.roll + gx * self.dt) + (1.0 - self.alpha) * accel_roll
        self.pitch = self.alpha * (self.pitch + gy * self.dt) + (1.0 - self.alpha) * accel_pitch
        self.yaw += gz * self.dt

        # Keep values in range
        if self.yaw > 180: self.yaw -= 360
        if self.yaw < -180: self.yaw += 360

        # Update buffers
        self.accel_buffer.append([ax, ay, az])
        self.gyro_buffer.append([gx, gy, gz])
        if len(self.accel_buffer) > self.buffer_size:
            self.accel_buffer.pop(0)
            self.gyro_buffer.pop(0)

        return self.roll, self.pitch, self.yaw

    def get_stats(self):
        if not self.accel_buffer:
            return None
        
        accel_data = np.array(self.accel_buffer)
        gyro_data = np.array(self.gyro_buffer)
        
        return {
            "accel_rms": np.sqrt(np.mean(np.square(accel_data - np.mean(accel_data, axis=0)), axis=0)),
            "gyro_rms": np.sqrt(np.mean(np.square(gyro_data - np.mean(gyro_data, axis=0)), axis=0)),
            "sample_rate": 1.0 / self.dt if self.dt > 0 else 0
        }

    def get_quaternion(self):
        """Convert current RPY to quaternion (ZYX convention)"""
        r = np.radians(self.roll)
        p = np.radians(self.pitch)
        y = np.radians(self.yaw)
        
        cy = np.cos(y * 0.5)
        sy = np.sin(y * 0.5)
        cp = np.cos(p * 0.5)
        sp = np.sin(p * 0.5)
        cr = np.cos(r * 0.5)
        sr = np.sin(r * 0.5)

        qw = cr * cp * cy + sr * sp * sy
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy
        
        return [qw, qx, qy, qz]