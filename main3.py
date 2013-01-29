from vision.vision import Vision
from command.feature import Feature
import arduino
import cv2
import cv
import time
import sys, getopt

def main(argv):
    # side = "red"

    # try:
    #     opts, args = getopt.getopt(argv,'', ['color='])
    # except getopt.GetoptError:
    #     print "usage: 'main.py --color=<c>', where <c> is 'red' or 'green'"
    # for opt, arg in opts:
    #     if opt == '--color':
    #         if arg == 'green':
    #             side = "green"
    #             print 'looking for green balls'
    #         elif arg == 'red':
    #             print 'looking for red balls'

    ardu = arduino.Arduino()
    motor_left = arduino.Motor(ardu, 0, 9, 8) # current pin, direction pin, pwm pin
    motor_right = arduino.Motor(ardu, 0, 7, 6)
    motor_pickup = arduino.Motor(ardu, 0, 12, 11)
    bump_right = arduino.DigitalInput(ardu, 22)
    bump_left = arduino.DigitalInput(ardu, 23)
    ardu.run()

    vis = Vision(True)
    end_now = False

    start_code = bump_left.getValue() - bump_right.getValue()
    while start_code == 0:
        start_code = bump_left.getValue() - bump_right.getValue()
    if start_code > 0:
        side = "green"
        print "green"
    else:
        side = "red"
        print "red"
    cv2.waitKey(1000)

    motor_pickup.setSpeed(60)

    start_time = time.time()
    try:
        while not end_now:
            time_elapsed = time.time() - start_time
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
            if time_elapsed < 120:
                feat_pos = vis.detect_balls(side)
            else:
                feat_pos = vis.detect_walls()
            if feat_pos != None:
                angle = int(feat_pos)
                print angle 
                motor_right.setSpeed(60 - angle)
                motor_left.setSpeed(60 + angle)
            else:
                print "No ball"
                motor_right.setSpeed(-40)
                motor_left.setSpeed(40)
            cv2.waitKey(20)
            if time_elapsed > 170:
                end_now = True
                break
    except KeyboardInterrupt:
        print "ending..."
    time.sleep(0.1)
    motor_right.setSpeed(0)
    motor_left.setSpeed(0)
    motor_pickup.setSpeed(0)
    time.sleep(0.1)
    ardu.stop()
   
if __name__ == "__main__":
    main(sys.argv[1:])
