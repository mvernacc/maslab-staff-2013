import arduino
import time

ard = arduino.Arduino()
left = arduino.Motor(ard, 3, 7, 6)
right = arduino.Motor(ard, 0, 13, 12)
roller = arduino.Motor(ard, 1, 11, 10)
tower = arduino.Motor(ard, 2, 9, 8) 
ard.start()
roller.setSpeed(10)
time.sleep(3)
roller.setSpeed(0)
time.sleep(3)
roller.setSpeed(10)
time.sleep(3)
roller.setSpeed(0)
time.sleep(3)
ard.stop()
time.sleep(3)
