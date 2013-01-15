import sys
sys.path.append("../..")
import time

import arduino

# A simple example of using the arduino library to
# control a servo.

ard = arduino.Arduino()
servo = arduino.Servo(ard, 7)  # Create a Servo object
ard.run()  # Run the Arduino communication thread

while True:
    # Sweep the servo back and forth
    for i in range(0, 120, 10):
        servo.setAngle(i)
        print "Angle", i
        time.sleep(0.1)
    for i in range(120, 0, -10):
        servo.setAngle(i)
        print "Angle", i
        time.sleep(0.1)
    
