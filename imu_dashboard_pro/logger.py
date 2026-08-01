import csv
import time
import os

class IMULogger:
    def __init__(self):
        self.file = None
        self.writer = None
        self.logging = False
        self.start_time = 0
        
    def start(self, filename=None):
        if filename is None:
            filename = f"imu_log_{int(time.time())}.csv"
        
        try:
            self.file = open(filename, 'w', newline='')
            self.writer = csv.writer(self.file)
            # Header
            self.writer.writerow([
                "timestamp_us", "ax", "ay", "az", "gx", "gy", "gz", 
                "roll", "pitch", "yaw"
            ])
            self.logging = True
            self.start_time = time.time()
            return True, filename
        except Exception as e:
            return False, str(e)

    def log(self, data_list):
        if self.logging and self.writer:
            try:
                self.writer.writerow(data_list)
            except Exception:
                pass

    def stop(self):
        self.logging = False
        if self.file:
            self.file.close()
            self.file = None
            self.writer = None
