from vision.vision import Vision
from command.feature import Feature
import arduino
import cv2
import cv
import time
import sys, getopt

def main(argv):
    red_side = True

    try:
        opts, args = getopt.getopt(argv,'', ['color='])
    except getopt.GetoptError:
        print "usage: 'main.py --color=<c>', where <c> is 'red' or 'green'"
    for opt, arg in opts:
        if opt == '--color':
            if arg == 'green':
                red_side = False
                print 'looking for green balls'
            elif arg == 'red':
                print 'looking for red balls'

    ardu = arduino.Arduino()
    motor_left = arduino.Motor(ardu, 0, 8, 10) #current pin,. direction pin, pwm pin
    motor_right = arduino.Motor(ardu, 0, 7, 9)
    ardu.run() # start ardu comm thread

    vis = Vision(red_side, True)
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
            cv2.waitKey(20)
    except KeyboardInterrupt:
        print "ending..."
        time.sleep(0.1)
        motor_right.setSpeed(0)
        motor_left.setSpeed(0)
        time.sleep(0.1)
        ardu.stop()
        end_now = True

if __name__ == "__main__":
    main(sys.argv[1:])
