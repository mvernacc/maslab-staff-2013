import arduino
import time

ard = arduino.Arduino()
right = arduino.Motor(ard, 0, 13, 12)
left = arduino.Motor(ard, 3, 7, 6)
roller = arduino.Motor(ard, 1, 11, 10)
tower = arduino.Motor(ard, 2, 9, 8)

print "running"

ard.start()

print "starting"

tower.setSpeed(100)
time.sleep(3)
ard.stop()
time.sleep(3)
