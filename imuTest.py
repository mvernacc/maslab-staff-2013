import sys
sys.path.append("../..")
import arduino # Import the interface library
import threading
import time
import serial

ard = arduino.Arduino()
imu = arduino.IMU(ard)

start_time = time.time()

ard.run()

while time.time() - start_time < 20:
    print imu.getRawValues()
    # print clock.getValue()
    # print test.getValue()
    # time.sleep(0.1)

ard.stop()

