import sys
import serial
import numpy as np
from collections import deque

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout
)

from PyQt5.QtCore import QTimer

import pyqtgraph as pg


PORT = "/dev/cu.usbserial-0001"   # CHANGE THIS
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("ESP32 IMU Dashboard")

mainLayout = QVBoxLayout()

# ------------------
# Roll Pitch Yaw
# ------------------

rollLabel = QLabel("Roll: 0")
pitchLabel = QLabel("Pitch: 0")
yawLabel = QLabel("Yaw: 0")

mainLayout.addWidget(rollLabel)
mainLayout.addWidget(pitchLabel)
mainLayout.addWidget(yawLabel)

# ------------------
# Plots
# ------------------

accelPlot = pg.PlotWidget(title="Accelerometer")
gyroPlot = pg.PlotWidget(title="Gyroscope")

mainLayout.addWidget(accelPlot)
mainLayout.addWidget(gyroPlot)

window.setLayout(mainLayout)

N = 500

axData = deque([0]*N, maxlen=N)
ayData = deque([0]*N, maxlen=N)
azData = deque([0]*N, maxlen=N)

gxData = deque([0]*N, maxlen=N)
gyData = deque([0]*N, maxlen=N)
gzData = deque([0]*N, maxlen=N)

curveAX = accelPlot.plot(name="AX")
curveAY = accelPlot.plot(name="AY")
curveAZ = accelPlot.plot(name="AZ")

curveGX = gyroPlot.plot(name="GX")
curveGY = gyroPlot.plot(name="GY")
curveGZ = gyroPlot.plot(name="GZ")


def update():

    try:

        line = ser.readline().decode().strip()

        if not line:
            return

        vals = list(map(float, line.split(",")))

        if len(vals) != 9:
            return

        ax, ay, az, gx, gy, gz, roll, pitch, yaw = vals

        rollLabel.setText(
            f"Roll: {roll:.2f}°"
        )

        pitchLabel.setText(
            f"Pitch: {pitch:.2f}°"
        )

        yawLabel.setText(
            f"Yaw: {yaw:.2f}°"
        )

        axData.append(ax)
        ayData.append(ay)
        azData.append(az)

        gxData.append(gx)
        gyData.append(gy)
        gzData.append(gz)

        curveAX.setData(list(axData))
        curveAY.setData(list(ayData))
        curveAZ.setData(list(azData))

        curveGX.setData(list(gxData))
        curveGY.setData(list(gyData))
        curveGZ.setData(list(gzData))

    except:
        pass


timer = QTimer()
timer.timeout.connect(update)
timer.start(10)

window.resize(1200, 800)
window.show()

sys.exit(app.exec_())