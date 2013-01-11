from vision.vision import Vision
from command.feature import Feature
import arduino
import time

ardu = arduino.Arduino()
motor_left = arduino.Motor(ardu, 0, 8, 10) #current pin,. direction pin, pwm pin
motor_right = arduino.Motor(ardu, 0, 7, 9)
ardu.run() # start ardu comm thread

vis = Vision(True)
end_now = False
try:
    while not end_now:
        feats = vis.get_feat()
        if len(feats) >0:
            angle = int(feats[0].angle)
            print angle 
            motor_right.setSpeed( -64 - angle*4 )
            motor_left.setSpeed( -64 + angle*4 )
        else:
            print "No ball"
            motor_right.setSpeed(0)
            motor_left.setSpeed(0)
        time.sleep(0.1)
except KeyboardInterrupt:
    print "ending..."
    time.sleep(0.1)
    motor_right.setSpeed(0)
    motor_left.setSpeed(0)
    time.sleep(0.1)
    ardu.stop()
    end_now = True
