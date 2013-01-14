import threading
import time
import arduino # Import the interface library

from vision.vision import Vision
from command.feature import Feature
import arduino
import cv2
import cv
import sys, getopt


class Robot():
    
    def __init__(self, arduino, mRight, mLeft, vision):
        
        self.ard = arduino # Create the Arduino object

        self.motor_right = mRight
        self.motor_left = mLeft
        self.vis = vision
        self.searching = False

    def forward(self, speed):
        # Sets motors to go forward
        self.motor_right.setSpeed(speed)
        self.motor_left.setSpeed(speed)

    def pause(self):
        # Stops motors, leaves any states (like searching). pauses 0.1 seconds to allow motors to stop
        self.motor_right.setSpeed(0)
        self.motor_right.setSpeed(0)
        self.searching = False
        time.sleep(0.1)

    def turn(self, side, speed):
        # Back up robot
        self.pause()
        self.motor_right.setSpeed(-speed)
        self.motor_left.setSpeed(-speed)
        time.sleep(1)
        self.pause()
        # turn robot
        if side == "left":
            self.motor_right.setSpeed(speed)
            self.motor_left.setSpeed(-speed)
            time.sleep(3)
        else:
            self.motor_right.setSpeed(-speed)
            self.motor_left.setSpeed(speed)
            time.sleep(3)
        self.pause()
        
    def wander(self, duration, speed):
        # Default robot movement (exploration)
        # Currently just moves forward for a set amount of time
        self.forward(speed)
        time.sleep(duration)
        
    def search(self, duration, speed):
        # add angle parameter?
        # turns to look around for balls
        # Sets robot to "searching" state
        self.searching = True
        self.pause()
        # begins turning
        self.motor_right.setSpeed(speed)
        self.motor_left.setSpeed(-speed)
        # sets timer to stop searching/turning after duration reached
        timer = threading.Timer(duration, self.pause)
        while self.searching == True:
            # looks for balls
            feats = vis.get_feat()
            # stop turning/searching if a ball is found
            if len(feats) > 0:
                self.pause()

    def ballFollow(self):
        angle = int(feats[0].angle)
        print angle 
        self.motor_right.setSpeed( -64 - angle*4 ) #WHy negative?
        self.motor_left.setSpeed( -64 + angle*4 ) 

        

    
        

