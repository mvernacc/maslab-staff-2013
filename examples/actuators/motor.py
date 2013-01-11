import sys
sys.path.append("../..")
import time

import arduino

ard = arduino.Arduino()
m0 = arduino.Motor(ard, 0,7, 9)
ard.run()  # Start the Arduino communication thread

while True:
    m0.setSpeed(64)
    time.sleep(1)
    m0.setSpeed(0)
    time.sleep(1)
    m0.setSpeed(-64)
    time.sleep(1)
    m0.setSpeed(0)
    time.sleep(1)
