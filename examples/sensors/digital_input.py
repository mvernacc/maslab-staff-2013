import time
import sys
sys.path.append("../..")

import arduino

# Example code to read digital input (from an encoder, for example)

ard = arduino.Arduino()  # Create the Arduino object
d2 = arduino.DigitalInput(ard, 22)  # Create a digital input at pin 2
ard.run()  # Start the thread which communicates with the Arduino

# Main loop -- check the sensor and update the digital output
while True:
    print d2.getValue()
    time.sleep(0.1)
