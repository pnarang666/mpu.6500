import sys
import csv
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
import pyqtgraph.opengl as gl

# -----------------------------
# CONFIG
# -----------------------------

PORT = "/dev/cu.usbserial-0001"   # CHANGE THIS
BAUD = 115200

# -----------------------------
# SERIAL
# -----------------------------

ser = serial.Serial(PORT, BAUD, timeout=1)

# -----------------------------
# CSV LOGGING
# -----------------------------

logfile = open("imu_log.csv", "w", newline="")
csvwriter = csv.writer(logfile)

csvwriter.writerow([
    "ax","ay","az",
    "gx","gy","gz",
    "roll","pitch","yaw"
])

# -----------------------------
# APP
# -----------------------------

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("ESP32 MPU6500 Dashboard")

layout = QVBoxLayout()

# -----------------------------
# ANGLE LABELS
# -----------------------------

rollLabel = QLabel("Roll : 0°")
pitchLabel = QLabel("Pitch: 0°")
yawLabel = QLabel("Yaw  : 0°")

layout.addWidget(rollLabel)
layout.addWidget(pitchLabel)
layout.addWidget(yawLabel)

# -----------------------------
# 3D VIEW
# -----------------------------

view = gl.GLViewWidget()
view.setCameraPosition(distance=10)

grid = gl.GLGridItem()
grid.scale(1,1,1)
view.addItem(grid)

cube_vertices = np.array([
    [-1,-0.5,-0.1],
    [ 1,-0.5,-0.1],
    [ 1, 0.5,-0.1],
    [-1, 0.5,-0.1],

    [-1,-0.5, 0.1],
    [ 1,-0.5, 0.1],
    [ 1, 0.5, 0.1],
    [-1, 0.5, 0.1]
])

faces = np.array([
    [0,1,2],
    [0,2,3],

    [4,5,6],
    [4,6,7],

    [0,1,5],
    [0,5,4],

    [2,3,7],
    [2,7,6],

    [1,2,6],
    [1,6,5],

    [0,3,7],
    [0,7,4]
])

mesh = gl.GLMeshItem(
    vertexes=cube_vertices,
    faces=faces,
    smooth=False,
    drawEdges=True
)

view.addItem(mesh)

layout.addWidget(view)

# -----------------------------
# PLOTS
# -----------------------------

accelPlot = pg.PlotWidget(title="Accelerometer")
gyroPlot = pg.PlotWidget(title="Gyroscope")

layout.addWidget(accelPlot)
layout.addWidget(gyroPlot)

window.setLayout(layout)

N = 300

axData = deque([0]*N,maxlen=N)
ayData = deque([0]*N,maxlen=N)
azData = deque([0]*N,maxlen=N)

gxData = deque([0]*N,maxlen=N)
gyData = deque([0]*N,maxlen=N)
gzData = deque([0]*N,maxlen=N)

curveAX = accelPlot.plot()
curveAY = accelPlot.plot()
curveAZ = accelPlot.plot()

curveGX = gyroPlot.plot()
curveGY = gyroPlot.plot()
curveGZ = gyroPlot.plot()

# -----------------------------
# ROTATION
# -----------------------------

prev_roll = 0
prev_pitch = 0
prev_yaw = 0

def update():

    global prev_roll
    global prev_pitch
    global prev_yaw

    try:

        line = ser.readline().decode().strip()

        vals = list(map(float, line.split(",")))

        if len(vals) != 9:
            return

        ax,ay,az,gx,gy,gz,roll,pitch,yaw = vals

        csvwriter.writerow(vals)
        logfile.flush()

        rollLabel.setText(
            f"Roll : {roll:.2f}°"
        )

        pitchLabel.setText(
            f"Pitch: {pitch:.2f}°"
        )

        yawLabel.setText(
            f"Yaw  : {yaw:.2f}°"
        )

        axData.append(ax)
        ayData.append(ay)
        azData.append(az)

        gxData.append(gx)
        gyData.append(gy)
        gzData.append(gz)

        curveAX.setData(axData)
        curveAY.setData(ayData)
        curveAZ.setData(azData)

        curveGX.setData(gxData)
        curveGY.setData(gyData)
        curveGZ.setData(gzData)

        mesh.resetTransform()

        mesh.rotate(yaw,   0,0,1)
        mesh.rotate(pitch, 0,1,0)
        mesh.rotate(roll,  1,0,0)

        prev_roll = roll
        prev_pitch = pitch
        prev_yaw = yaw

    except Exception:
        pass

timer = QTimer()
timer.timeout.connect(update)
timer.start(10)

window.resize(1400,1000)
window.show()

sys.exit(app.exec_())