import serial
import serial.tools.list_ports
import threading
import time
import collections

class SerialReader(threading.Thread):
    def __init__(self, baudrate=115200):
        super().__init__()
        self.port = None
        self.baudrate = baudrate
        self.ser = None
        self.running = False
        self.connected = False
        self.data_callback = None
        self.error_callback = None
        
        # Buffer for incoming data
        self.line_buffer = ""
        
    def find_esp32_port(self):
        """Specifically look for macOS USB serial ports"""
        ports = serial.tools.list_ports.comports()
        
        # Check for the user's specific port first
        for p in ports:
            if p.device == "/dev/cu.usbserial-0001":
                return p.device
                
        for p in ports:
            # Common patterns for ESP32 on macOS
            if "usbserial" in p.device.lower() or "cu.SLAB_USBtoUART" in p.device or "cu.wchusbserial" in p.device:
                return p.device
        # Fallback to any usbserial if specific ones not found
        for p in ports:
            if "usbserial" in p.device.lower():
                return p.device
        return None

    def connect(self, port=None):
        if port is None:
            port = self.find_esp32_port()
        
        if not port:
            return False, "No ESP32 detected"
        
        try:
            self.ser = serial.Serial(port, self.baudrate, timeout=0.1)
            self.port = port
            self.connected = True
            self.running = True
            if not self.is_alive():
                self.start()
            return True, port
        except Exception as e:
            return False, str(e)

    def disconnect(self):
        self.running = False
        if self.ser:
            self.ser.close()
        self.connected = False

    def run(self):
        while self.running:
            if not self.ser or not self.ser.is_open:
                time.sleep(0.1)
                continue
                
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self.process_line(line)
            except Exception as e:
                if self.error_callback:
                    self.error_callback(str(e))
                self.connected = False
                time.sleep(1) # Wait before retry or status update

    def process_line(self, line):
        """Expects: timestamp_us,ax,ay,az,gx,gy,gz"""
        try:
            parts = line.split(',')
            if len(parts) == 7:
                data = [float(x) for x in parts]
                if self.data_callback:
                    self.data_callback(data)
        except Exception:
            pass # Ignore malformed lines