import sys
import time
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, QSplitter)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QFont, QColor

import pyqtgraph as pg

# Local imports
from serial_reader import SerialReader
from imu_filter import IMUFilter
from opengl_view import IMUOpenGLView
from logger import IMULogger

class IMUWorkstation(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Titan IMU Analysis Workstation")
        self.resize(1400, 900)
        
        # Initialize components
        self.reader = SerialReader()
        self.filter = IMUFilter(alpha=0.98)
        self.logger = IMULogger()
        
        self.calibrate_mode = False
        self.calibration_samples = []
        
        self.init_ui()
        self.setup_timer()
        
        # Dark theme stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f111a;
            }
            QFrame {
                background-color: #1a1c2c;
                border-radius: 8px;
                border: 1px solid #2a2d3e;
            }
            QLabel {
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
            }
            QPushButton {
                background-color: #2a2d3e;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3f445e;
            }
            QPushButton#action-btn {
                background-color: #3d5afe;
            }
            QPushButton#action-btn:hover {
                background-color: #536dfe;
            }
            QPushButton#danger-btn {
                background-color: #ff5252;
            }
            QPushButton#danger-btn:hover {
                background-color: #ff867f;
            }
        """)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- Top Header: Status and RPY ---
        header_layout = QHBoxLayout()
        
        self.status_label = QLabel("DISCONNECTED")
        self.status_label.setStyleSheet("color: #ff5252; font-weight: bold; font-size: 14px;")
        
        rpy_widget = QFrame()
        rpy_layout = QHBoxLayout(rpy_widget)
        self.roll_val = QLabel("ROLL: 0.00°")
        self.pitch_val = QLabel("PITCH: 0.00°")
        self.yaw_val = QLabel("YAW: 0.00°")
        for lbl in [self.roll_val, self.pitch_val, self.yaw_val]:
            lbl.setFont(QFont("Monospace", 18, QFont.Bold))
        rpy_layout.addWidget(self.roll_val)
        rpy_layout.addWidget(self.pitch_val)
        rpy_layout.addWidget(self.yaw_val)
        
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()
        header_layout.addWidget(rpy_widget)
        main_layout.addLayout(header_layout)

        # --- Center: Viewer and Side Panel ---
        center_splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel: OpenGL View
        self.gl_viewer = IMUOpenGLView()
        center_splitter.addWidget(self.gl_viewer)
        
        # Right Panel: Controls and Metrics
        side_panel = QFrame()
        side_layout = QVBoxLayout(side_panel)
        
        # Metrics Group
        metrics_label = QLabel("SYSTEM METRICS")
        metrics_label.setStyleSheet("font-weight: bold; color: #3d5afe;")
        side_layout.addWidget(metrics_label)
        
        self.hz_label = QLabel("Sample Rate: 0 Hz")
        self.acc_mag_label = QLabel("Accel Mag: 0.00 g")
        self.gyro_mag_label = QLabel("Gyro Mag: 0.00°/s")
        self.acc_noise_label = QLabel("Acc RMS: -")
        self.gyro_noise_label = QLabel("Gyro RMS: -")
        
        for lbl in [self.hz_label, self.acc_mag_label, self.gyro_mag_label, self.acc_noise_label, self.gyro_noise_label]:
            side_layout.addWidget(lbl)
            
        side_layout.addSpacing(20)
        
        # Calibration Group
        calib_label = QLabel("CALIBRATION")
        calib_label.setStyleSheet("font-weight: bold; color: #3d5afe;")
        side_layout.addWidget(calib_label)
        
        self.calib_btn = QPushButton("Calibrate Gyro")
        self.calib_btn.setObjectName("action-btn")
        self.calib_btn.clicked.connect(self.start_calibration)
        side_layout.addWidget(self.calib_btn)
        
        self.reset_yaw_btn = QPushButton("Reset Yaw (Z)")
        self.reset_yaw_btn.clicked.connect(self.filter.reset_yaw)
        side_layout.addWidget(self.reset_yaw_btn)
        
        side_layout.addSpacing(20)
        
        # Logging Group
        log_label = QLabel("RECORDING")
        log_label.setStyleSheet("font-weight: bold; color: #3d5afe;")
        side_layout.addWidget(log_label)
        
        self.log_btn = QPushButton("Start Logging")
        self.log_btn.clicked.connect(self.toggle_logging)
        side_layout.addWidget(self.log_btn)
        
        self.conn_btn = QPushButton("Connect Serial")
        self.conn_btn.clicked.connect(self.toggle_connection)
        side_layout.addWidget(self.conn_btn)
        
        side_layout.addStretch()
        center_splitter.addWidget(side_panel)
        center_splitter.setSizes([1000, 300])
        main_layout.addWidget(center_splitter, 3)

        # --- Bottom: Plots ---
        plot_splitter = QSplitter(Qt.Horizontal)
        
        # Accel Plots
        self.acc_plot = pg.PlotWidget(title="Accelerometer (g)")
        self.acc_plot.addLegend()
        self.acc_plot.setBackground('#1a1c2c')
        self.acc_curves = [
            self.acc_plot.plot(pen='r', name="ax"),
            self.acc_plot.plot(pen='g', name="ay"),
            self.acc_plot.plot(pen='b', name="az")
        ]
        plot_splitter.addWidget(self.acc_plot)
        
        # Gyro Plots
        self.gyro_plot = pg.PlotWidget(title="Gyroscope (°/s)")
        self.gyro_plot.addLegend()
        self.gyro_plot.setBackground('#1a1c2c')
        self.gyro_curves = [
            self.gyro_plot.plot(pen='r', name="gx"),
            self.gyro_plot.plot(pen='g', name="gy"),
            self.gyro_plot.plot(pen='b', name="gz")
        ]
        plot_splitter.addWidget(self.gyro_plot)
        
        main_layout.addWidget(plot_splitter, 2)
        
        # Data storage for plots
        self.plot_limit = 500
        self.acc_data = [np.zeros(self.plot_limit) for _ in range(3)]
        self.gyro_data = [np.zeros(self.plot_limit) for _ in range(3)]

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(50) # 20 Hz UI update

    def toggle_connection(self):
        if not self.reader.connected:
            success, port = self.reader.connect()
            if success:
                self.status_label.setText(f"CONNECTED: {port}")
                self.status_label.setStyleSheet("color: #4caf50; font-weight: bold; font-size: 14px;")
                self.conn_btn.setText("Disconnect")
                self.reader.data_callback = self.handle_data
            else:
                self.status_label.setText(f"FAILED: {port}")
        else:
            self.reader.disconnect()
            self.status_label.setText("DISCONNECTED")
            self.status_label.setStyleSheet("color: #ff5252; font-weight: bold; font-size: 14px;")
            self.conn_btn.setText("Connect Serial")

    def handle_data(self, data):
        # data: [ts_us, ax, ay, az, gx, gy, gz]
        ts, ax, ay, az, gx, gy, gz = data
        
        if self.calibrate_mode:
            self.calibration_samples.append([gx, gy, gz])
            if len(self.calibration_samples) >= 500:
                self.filter.calibrate_gyro(self.calibration_samples)
                self.calibrate_mode = False
                self.calib_btn.setText("Calibrate Gyro")
                self.calib_btn.setEnabled(True)
        
        # Update filter
        roll, pitch, yaw = self.filter.update(ts, ax, ay, az, gx, gy, gz)
        
        # Push to plot buffers
        for i, val in enumerate([ax, ay, az]):
            self.acc_data[i] = np.roll(self.acc_data[i], -1)
            self.acc_data[i][-1] = val
            
        for i, val in enumerate([gx, gy, gz]):
            self.gyro_data[i] = np.roll(self.gyro_data[i], -1)
            self.gyro_data[i][-1] = val

        # Logging
        if self.logger.logging:
            self.logger.log([ts, ax, ay, az, gx, gy, gz, roll, pitch, yaw])

    def start_calibration(self):
        self.calibrate_mode = True
        self.calibration_samples = []
        self.calib_btn.setText("Calibrating...")
        self.calib_btn.setEnabled(False)

    def toggle_logging(self):
        if not self.logger.logging:
            success, name = self.logger.start()
            if success:
                self.log_btn.setText("Stop Logging")
                self.log_btn.setObjectName("danger-btn")
                self.setStyleSheet(self.styleSheet()) # Force refresh
        else:
            self.logger.stop()
            self.log_btn.setText("Start Logging")
            self.log_btn.setObjectName("")
            self.setStyleSheet(self.styleSheet())

    def update_ui(self):
        # Update Labels
        self.roll_val.setText(f"ROLL: {self.filter.roll:6.2f}°")
        self.pitch_val.setText(f"PITCH: {self.filter.pitch:6.2f}°")
        self.yaw_val.setText(f"YAW: {self.filter.yaw:6.2f}°")
        
        # Update OpenGL
        self.gl_viewer.set_orientation(self.filter.get_quaternion())
        
        # Update Plots
        for i in range(3):
            self.acc_curves[i].setData(self.acc_data[i])
            self.gyro_curves[i].setData(self.gyro_data[i])
            
        # Update Stats
        stats = self.filter.get_stats()
        if stats:
            self.hz_label.setText(f"Sample Rate: {stats['sample_rate']:6.1f} Hz")
            
            # Magnitudes (current)
            ax, ay, az = self.acc_data[0][-1], self.acc_data[1][-1], self.acc_data[2][-1]
            gx, gy, gz = self.gyro_data[0][-1], self.gyro_data[1][-1], self.gyro_data[2][-1]
            
            acc_mag = np.sqrt(ax**2 + ay**2 + az**2)
            gyro_mag = np.sqrt(gx**2 + gy**2 + gz**2)
            
            self.acc_mag_label.setText(f"Accel Mag: {acc_mag:6.3f} g")
            self.gyro_mag_label.setText(f"Gyro Mag: {gyro_mag:6.1f}°/s")
            
            # Noise (RMS) - mean of x,y,z RMS for display
            acc_rms = np.mean(stats['accel_rms'])
            gyro_rms = np.mean(stats['gyro_rms'])
            self.acc_noise_label.setText(f"Acc RMS: {acc_rms:6.4f} g")
            self.gyro_noise_label.setText(f"Gyro RMS: {gyro_rms:6.4f}°/s")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IMUWorkstation()
    window.show()
    sys.exit(app.exec_())