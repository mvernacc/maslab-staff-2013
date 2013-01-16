import sys
sys.path.append("../..")
import arduino # Import the interface library
import threading
import time
import serial

ard = arduino.Arduino()
imu = arduino.IMU(ard)
test = arduino.AnalogInput(ard, 4)
bump = arduino.DigitalInput(ard, 22)

running = True

def halt():
    print "Stopping"
    running = False
    ard.stop()

timer = threading.Timer(5.0, halt)
timer.start()

ard.run()

while running:
    print imu.getRawValues()
    print bump.getValue()
    print test.getValue()
    time.sleep(0.1)

ard.stop()

