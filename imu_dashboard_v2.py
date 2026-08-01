import sys
import csv
import serial
import numpy as np

from collections import deque

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout
)

from PyQt5.QtCore import QTimer

import pyqtgraph as pg


PORT = "/dev/cu.usbserial-0001"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)

logfile = open("imu_log.csv", "w", newline="")

writer = csv.writer(logfile)

writer.writerow([
    "ax","ay","az",
    "gx","gy","gz",
    "roll","pitch","yaw"
])

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("MPU6500 Dashboard")

layout = QVBoxLayout()

orientationLabel = QLabel(
    "Roll: 0   Pitch: 0   Yaw: 0"
)

layout.addWidget(orientationLabel)

cubePlot = pg.PlotWidget()
cubePlot.setAspectLocked(True)
cubePlot.showGrid(x=True, y=True)

layout.addWidget(cubePlot)

accelPlot = pg.PlotWidget(title="Accelerometer")

layout.addWidget(accelPlot)

gyroPlot = pg.PlotWidget(title="Gyroscope")

layout.addWidget(gyroPlot)

window.setLayout(layout)

N = 250

axHist = deque([0]*N,maxlen=N)
ayHist = deque([0]*N,maxlen=N)
azHist = deque([0]*N,maxlen=N)

gxHist = deque([0]*N,maxlen=N)
gyHist = deque([0]*N,maxlen=N)
gzHist = deque([0]*N,maxlen=N)

curveAX = accelPlot.plot()
curveAY = accelPlot.plot()
curveAZ = accelPlot.plot()

curveGX = gyroPlot.plot()
curveGY = gyroPlot.plot()
curveGZ = gyroPlot.plot()

cubeCurve = cubePlot.plot([],[])

cube = np.array([
    [-1,-0.5],
    [ 1,-0.5],
    [ 1, 0.5],
    [-1, 0.5],
    [-1,-0.5]
])

def update():

    try:

        line = ser.readline().decode().strip()

        vals = list(map(float,line.split(",")))

        if len(vals) != 9:
            return

        ax,ay,az,gx,gy,gz,roll,pitch,yaw = vals

        writer.writerow(vals)

        orientationLabel.setText(
            f"Roll: {roll:.1f}°    "
            f"Pitch: {pitch:.1f}°    "
            f"Yaw: {yaw:.1f}°"
        )

        theta = np.radians(roll)

        R = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta),  np.cos(theta)]
        ])

        rotated = cube @ R.T

        cubeCurve.setData(
            rotated[:,0],
            rotated[:,1]
        )

        axHist.append(ax)
        ayHist.append(ay)
        azHist.append(az)

        gxHist.append(gx)
        gyHist.append(gy)
        gzHist.append(gz)

        curveAX.setData(axHist)
        curveAY.setData(ayHist)
        curveAZ.setData(azHist)

        curveGX.setData(gxHist)
        curveGY.setData(gyHist)
        curveGZ.setData(gzHist)

    except:
        pass

timer = QTimer()

timer.timeout.connect(update)

timer.start(10)

window.resize(1200,900)

window.show()

sys.exit(app.exec_())