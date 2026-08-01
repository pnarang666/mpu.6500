import sys
import csv
import glob
import serial
import numpy as np

from collections import deque

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
)

from PyQt5.QtCore import QTimer

import pyqtgraph as pg


ports = glob.glob("/dev/cu.usbserial*")

if len(ports)==0:
    raise RuntimeError("ESP32 not found")

PORT = ports[0]

ser = serial.Serial(PORT,115200,timeout=1)

logfile = open("imu_log.csv","w",newline="")
writer = csv.writer(logfile)

writer.writerow([
    "t","ax","ay","az","gx","gy","gz"
])

app = QApplication(sys.argv)

window = QWidget()

layout = QVBoxLayout()

statusLabel = QLabel("Waiting...")

layout.addWidget(statusLabel)

accelPlot = pg.PlotWidget(title="Accelerometer")
gyroPlot  = pg.PlotWidget(title="Gyroscope")

layout.addWidget(accelPlot)
layout.addWidget(gyroPlot)

window.setLayout(layout)

N = 500

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


def update():

    try:

        line = ser.readline().decode().strip()

        if "timestamp" in line:
            return

        vals = line.split(",")

        if len(vals)!=7:
            return

        t,ax,ay,az,gx,gy,gz = map(float,vals)

        writer.writerow(vals)

        roll = np.degrees(
            np.arctan2(
                ay,
                az
            )
        )

        pitch = np.degrees(
            np.arctan2(
                -ax,
                np.sqrt(
                    ay*ay +
                    az*az
                )
            )
        )

        statusLabel.setText(
            f"Roll={roll:.1f}°   "
            f"Pitch={pitch:.1f}°"
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
timer.start(5)

window.resize(1200,800)
window.show()

sys.exit(app.exec_())