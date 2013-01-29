import arduino
import time

ard = arduino.Arduino()
motor_pickup = arduino.Motor(ard, 0, 12, 11)
ard.run()
motor_pickup.setSpeed(-100)
time.sleep(5)
motor_pickup.setSpeed(0)
time.sleep(0.1)
ard.stop()
