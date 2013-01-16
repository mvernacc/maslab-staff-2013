# A simple example that set up an IMU and prints out the raw values received from it
import sys
sys.path.append("../..")
import time
import arduino

ard = arduino.Arduino()
imu = arduino.IMU(ard)
ard.run()

while True:
    print imu.getRawValues()
    time.sleep(0.05)
