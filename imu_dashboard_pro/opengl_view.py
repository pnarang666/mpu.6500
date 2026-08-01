from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, pyqtSignal
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class IMUOpenGLView(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.quat = [1, 0, 0, 0] # w, x, y, z
        self.zoom = -10.0
        self.rot_x = 20
        self.rot_y = -45
        self.last_mouse_pos = None

    def set_orientation(self, quat):
        self.quat = quat
        self.update()

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glClearColor(0.05, 0.05, 0.07, 1.0) # Dark gray background
        
        glLightfv(GL_LIGHT0, GL_POSITION, [10, 10, 10, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h > 0 else 1, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        glTranslatef(0, 0, self.zoom)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)
        
        # Draw Floor Grid
        self.draw_grid()
        
        # Draw World Axes
        self.draw_axes(length=3, width=2)
        
        # Apply orientation rotation
        self.apply_quaternion_rotation(self.quat)
        
        # Draw Sensor Cube
        self.draw_cube()
        
        # Draw Sensor Axes (shorter)
        self.draw_axes(length=1.5, width=4)

    def draw_grid(self):
        glBegin(GL_LINES)
        glColor4f(0.2, 0.2, 0.2, 1.0)
        for i in range(-5, 6):
            glVertex3f(i, 0, -5)
            glVertex3f(i, 0, 5)
            glVertex3f(-5, 0, i)
            glVertex3f(5, 0, i)
        glEnd()

    def draw_axes(self, length=1.0, width=1.0):
        glLineWidth(width)
        glBegin(GL_LINES)
        # X - Red
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(length, 0, 0)
        # Y - Green
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, length, 0)
        # Z - Blue
        glColor3f(0.2, 0.4, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, length)
        glEnd()
        glLineWidth(1.0)

    def draw_cube(self):
        glBegin(GL_QUADS)
        
        # Colors for faces
        colors = [
            (0.1, 0.4, 0.8), (0.1, 0.4, 0.8), # Front/Back
            (0.1, 0.5, 0.9), (0.1, 0.5, 0.9), # Top/Bottom
            (0.2, 0.6, 1.0), (0.2, 0.6, 1.0)  # Sides
        ]
        
        # Vertices for a rectangle box
        v = [
            [ 1,  0.2,  0.5], [-1,  0.2,  0.5], [-1, -0.2,  0.5], [ 1, -0.2,  0.5], # Front
            [ 1,  0.2, -0.5], [-1,  0.2, -0.5], [-1, -0.2, -0.5], [ 1, -0.2, -0.5], # Back
            [ 1,  0.2,  0.5], [-1,  0.2,  0.5], [-1,  0.2, -0.5], [ 1,  0.2, -0.5], # Top
            [ 1, -0.2,  0.5], [-1, -0.2,  0.5], [-1, -0.2, -0.5], [ 1, -0.2, -0.5], # Bottom
            [ 1,  0.2,  0.5], [ 1, -0.2,  0.5], [ 1, -0.2, -0.5], [ 1,  0.2, -0.5], # Right
            [-1,  0.2,  0.5], [-1, -0.2,  0.5], [-1, -0.2, -0.5], [-1,  0.2, -0.5]  # Left
        ]
        
        for i in range(6):
            glColor3fv(colors[i])
            for j in range(4):
                glVertex3fv(v[i*4 + j])
        glEnd()
        
        # Wireframe edges
        glColor3f(1, 1, 1)
        glBegin(GL_LINES)
        for i in range(6):
            for j in range(4):
                glVertex3fv(v[i*4 + j])
                glVertex3fv(v[i*4 + (j+1)%4])
        glEnd()

    def apply_quaternion_rotation(self, q):
        # Convert quat [w, x, y, z] to rotation matrix
        w, x, y, z = q
        xx, yy, zz = x*x, y*y, z*z
        xy, xz, yz = x*y, x*z, y*z
        xw, yw, zw = x*w, y*w, z*w

        matrix = [
            1 - 2*(yy + zz),     2*(xy - zw),     2*(xz + yw), 0,
                2*(xy + zw), 1 - 2*(xx + zz),     2*(yz - xw), 0,
                2*(xz - yw),     2*(yz + xw), 1 - 2*(xx + yy), 0,
                          0,               0,               0, 1
        ]
        glMultMatrixf(matrix)

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            
            self.rot_y += dx * 0.5
            self.rot_x += dy * 0.5
            self.last_mouse_pos = event.pos()
            self.update()

    def wheelEvent(self, event):
        self.zoom += event.angleDelta().y() / 120.0
        self.update()
