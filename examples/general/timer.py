# This code exemplifies stopping commands after some amount of time.

import sys
sys.path.append("../..")
import threading
import time
import arduino # Staff library


# Global variable to control the main thread
running = True

# Function to stop the main thread
def halt():
    print "Stopping"
    global running
    running = False
timer = threading.Timer(20.0, halt) # Run the halt function after 20 seconds in a different thread
timer.start() # Actually start the timer, the time counts from this point on

# Setup the Arduino
ard = arduino.Arduino()
d2 = arduino.DigitalInput(ard, 2)
ard.run()

# Normal execution -- same as the digital input example,
# just print the value of a digital input
while running:
    print d2.getValue()
    time.sleep(0.1)
# If we get here, halt was called
# Stop the arduino code, this should automatically stop the motors
ard.stop()
