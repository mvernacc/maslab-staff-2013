from vision.vision import Vision
from command.feature import Feature
import arduino
import cv2
import cv
import time
import sys, getopt

def main(argv):
    ardu = arduino.Arduino()
    motor_left = arduino.Motor(ardu, 0, 9, 8) # current pin, direction pin, pwm pin
    motor_right = arduino.Motor(ardu, 0, 7, 6)
    bump_right = arduino.DigitalInput(ardu, 22)
    bump_left = arduino.DigitalInput(ardu, 23)
    ardu.run() # start ardu comm thread

    vis = Vision(True)
    end_now = False
    start_time = time.time()
    try:
        while not end_now:
            if time.time() - start_time  > 180:
                break
            if bump_right.getValue():
                print 'right bump'
                motor_right.setSpeed(-200)
                motor_left.setSpeed(-50)
                cv2.waitKey(1000)
                motor_right.setSpeed(-100)
                motor_left.setSpeed(100)
                cv2.waitKey(500)
                motor_right.setSpeed(0)
                motor_left.setSpeed(0)
            if bump_left.getValue():
                print 'left bump'
                motor_right.setSpeed(-50)
                motor_left.setSpeed(-200)
                cv2.waitKey(1000)
                motor_right.setSpeed(100)
                motor_left.setSpeed(-100)
                cv2.waitKey(500)
                motor_right.setSpeed(0)
                motor_left.setSpeed(0)
            vis.grab_frame()
            feats = vis.detect_balls(side)
            if len(feats) >0:
                angle = int(feats[0].angle)
                print angle 
                motor_right.setSpeed( 64 - angle*4 )
                motor_left.setSpeed( 64 + angle*4 )
            else:
                print "No ball"
                motor_right.setSpeed(-50)
                motor_left.setSpeed(50)
            cv2.waitKey(20)
    except KeyboardInterrupt:
        print "ending..."
    time.sleep(0.1)
    motor_right.setSpeed(0)
    motor_left.setSpeed(0)
    time.sleep(0.1)
    ardu.stop()
   
if __name__ == "__main__":
    main(sys.argv[1:])
