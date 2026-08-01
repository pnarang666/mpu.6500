from vpython import *
import serial
import math

PORT = "/dev/cu.usbserial-0001"
BAUD = 115200

ser = serial.Serial(PORT, BAUD)

scene.width = 1200
scene.height = 800
scene.title = "ESP32 MPU6500"

sensor = box(
    length=4,
    height=0.3,
    width=2
)

arrow_x = arrow(
    pos=vector(0,0,0),
    axis=vector(3,0,0)
)

arrow_y = arrow(
    pos=vector(0,0,0),
    axis=vector(0,3,0)
)

arrow_z = arrow(
    pos=vector(0,0,0),
    axis=vector(0,0,3)
)

while True:

    try:

        line = ser.readline().decode().strip()

        vals = line.split(",")

        if len(vals) != 9:
            continue

        ax,ay,az,gx,gy,gz,roll,pitch,yaw = map(float, vals)

        roll = math.radians(roll)
        pitch = math.radians(pitch)
        yaw = math.radians(yaw)

        cx = math.cos(roll)
        sx = math.sin(roll)

        cy = math.cos(pitch)
        sy = math.sin(pitch)

        cz = math.cos(yaw)
        sz = math.sin(yaw)

        R11 = cz*cy
        R12 = cz*sy*sx - sz*cx
        R13 = cz*sy*cx + sz*sx

        R21 = sz*cy
        R22 = sz*sy*sx + cz*cx
        R23 = sz*sy*cx - cz*sx

        R31 = -sy
        R32 = cy*sx
        R33 = cy*cx

        sensor.axis = vector(
            R11,
            R21,
            R31
        )

        sensor.up = vector(
            R13,
            R23,
            R33
        )

    except Exception as e:
        print(e)