import threading
import time
import arduino # Import the interface library

from vision.vision import Vision
from command.feature import Feature
import cv2
import cv
import sys, getopt


class Robot():
    
    def __init__(self, arduino, vision):
        
        self.ard = arduino # Create the Arduino object

        # Create other actuators, sensors, etc.
        motorRight = arduino.Motor(ard, 0, 9, 8)
            # Motor with pwm output on pin 8, direction pin on digital pin 9, and current sensing pin on pin A0
        motorLeft = arduino.Motor(ard, 1, 11, 10)
            # Motor with pwm output on pin 10, direction pin on digital pin 11, and current sensing pin on pin A1
        #motorPickUp = arduino.Motor(ard, current, direction, pwm)
        #motorTower = arduino.Motor(ard, current, direction, pwm)

        #servoGate = arduino.Servo(ard, pwm)

        #bumpFrontRight = arduino.DigitalInput(ard, 22) # Digital input on pin 22
        #bumpFrontLeft = arduino.DigitalInput(ard, 25) # Digital input on pin 23
        #bumpBackRight = arduino.DigitalInput(ard, 26)
        #bumpBackLeft = arduino.DigitalInput(ard, 29)

        #onOff = arduino.DigitalInput(ard,)
        #redGreen = arduino.DigitalInput(ard,)

        #nirRight = arduino.AnalogInput(ard,)
        #nirLeft = arduino.AnalogInput(ard,)
        #firRight = arduino.AnalogInput(ard,)
        #firRight = arduino.AnalogInput(ard,)
        
        imuSCL = arduino.AnalogInput(ard, 5)  # Analog input on pin A5
        imuSDA = arduino.AnalogInput(ard, 4)  # Analog input on pin A4

        self.vis = vision

        self.searching = False
        self.running = True

    def forward(self, speed):
        # Sets motors to go forward
        self.motor_right.setSpeed(-speed)
        self.motor_left.setSpeed(-speed)

    def pause(self):
        # Stops motors, leaves any states (like searching). pauses 0.1 seconds to allow motors to stop
        self.motor_right.setSpeed(0)
        self.motor_right.setSpeed(0)
        self.searching = False
        time.sleep(0.1)

    def back_up(self, speed):
        # Back up robot
        self.pause()
        self.motor_right.setSpeed(speed)
        self.motor_left.setSpeed(speed)
        time.sleep(1)
        self.pause()

    def turn(self, side, speed):
        # turn robot
        if side == "left":
            self.motor_right.setSpeed(-speed)
            self.motor_left.setSpeed(speed)
            time.sleep(1)
        else:
            self.motor_right.setSpeed(speed)
            self.motor_left.setSpeed(-speed)
            time.sleep(1)
        self.pause()
        
    def wander(self):
        # Default robot movement (exploration)
        # Currently just moves forward for a set amount of time
        print "state = wander"
        duration = 2
        speed = 64
        self.forward(speed)
        cv2.waitKey(duration*1000)
        if self.running: 
            try:
                self.search()
            except KeyboardInterrupt:
                self.end()
        
    def search(self):
        # add angle parameter?
        # turns to look around for balls
        # Sets robot to "searching" state
        # switches to ballFollow stae if it sees a ball
        print "state = search"
        self.pause()
        feats = self.vis.get_feat()
        for i in range (5):
            if len(feats) > 0: break
            self.turn("left", 64)
            cv2.waitKey(500)
            self.pause()
            # looks for balls
            feats = self.vis.get_feat()
        # stop turning/searching if a ball is found
        self.pause()
        if self.running: 
            try:
                if len(feats) > 0: 
                    self.ballFollow()
                else:
                    self.wander()
            except KeyboardInterrupt:
                self.end()

    def ballFollow(self):
        print "state = ball follow"
        feats = self.vis.get_feat()
        while len(feats) > 0 and self.running:
            angle = int(feats[0].angle)
            print angle 
            self.motor_right.setSpeed( -64 - angle*4 ) #WHy negative?
            self.motor_left.setSpeed( -64 + angle*4 ) 
        # when we lose sight of the ball, go forward a bit so we hit the ball
        self.forward(64)
        time.sleep(0.5)
        # go back to the searching state
        if self.running: 
            try:
                self.search()
            except KeyboardInterrupt:
                self.end()

    def goTo(self, feat):
        # feats = self.vis.get_feat()
        # go to feature

    def goFarAway(self):
        # drives to place farthest away, while stopping in the middle and scanning
        # dest = farthest open space
        # drive half way
        # scan

    def pushButton(self):  # pushes the green button
        self.align()
        self.forward()

    def shoot(self):    # shoots balls from tower
        pass

    def doubleCheck():
        self.wallFollow()
        self.scan()

    def explore(self):
        if !repeatedBarcodes #unique barcodes
            self.wander()
        else:
            self.goFarAway()
            
    def end(self):
        print "robot stopping now!"
        self.running = False
        self.pause()
        

