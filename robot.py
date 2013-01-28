import arduino # Import the interface library
import threading, thread
import time
#import ir_dist
from vision.vision import Vision, Color, Feature

import cv2
import cv
import sys, getopt


class Robot(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.ard = arduino.Arduino() # Create the Arduino object
        self.pid = arduino.PID(self.ard)
        self.motors = Motors(self.ard)
        self.bumpers = Bumpers(self.ard)
        self.ir = IR(self.ard)
        self.vision = Vision()
        self.vision.color = Color.Red
        self.vision.features = Feature.Ball
        self.time = Timer()
        
        self.servoBridge = arduino.Servo(self.ard, 5)
        self.servoGate = arduino.Servo(self.ard, 4)
        self.bridgeBump = arduino.DigitalInput(self.ard, 27)
        self.go = arduino.DigitalInput(self.ard, 30)

        self.map = {}
        self.tower = []
        self.wall = []
        self.repeatedBarcodes = False

    def run(self):
        self.ard.start()
        # while self.ard.portOpened == False:
        #     time.sleep(0)
        time.sleep(1)

        # if code gets here, go.getValue() == True
        # self.time.reset() moved to fsm
        self.motors.start()
        self.servoBridge.setAngle(90)
        # self.bumpers.start()
        # self.ir.start()
        self.vision.start()
        running = True
        while running == True:
            if int(self.time.elapsed() % 5) <= 2 && self.time.elapsed() < 120:
                self.robot.vision.features = Feature.Tower | Feature.Wall | Feature.QRCode
                # add searching for QRCodes instead?
                if detections[Feature.QRCode] != None:
                    for QRcode in detections:
                        #self.map[QRcode] = respective angle...??
                if detections[Feature.Tower] != None:
                    self.tower.append((arduino.getHeading(ard), detections[Feature.Tower]))
                if detections[Feature.Wall] != None:
                    self.wall = ((arduino.getHeading(ard), detections[Feature.Wall]))
             
        

    def stop(self):
        self.pid.stop()
        self.motors.stop()
        self.bumpers.stop()
        self.ir.stop()
        self.vision.stop()
        # time.sleep(1)
        self.ard.stop()

    def reverse(self, bump):
        bumped = bump
        self.motor.right.setSpeed(-40)
        self.motor.left.setSpeed(-40)
        while self.state_time() < 1:
            pass
        if bumped == (True, False) or bumped == (True, True):
            #left bump sensor hit,turning scheme
            self.robot.motor.right.setSpeed(-40)
            self.robot.motor.left.setSpeed(40)
            while self.state_time() < 0.5:
                pass
        elif bumped == (False, True):
            #right bump sensor hit
            self.robot.motor.right.setSpeed(-40)
            self.robot.motor.left.setSpeed(40)
            
    # can we return to the state we came from?
    # This will require us to redo the infrastructure of our code,
    # or scan state can fix it...


    def getFarthestPoint(self):
        startAngle = ard.getHeading()
        firData = []
        self.ir.running = True
        self.motors.left.setSpeed(50)
        self.motors.right.setSpeed(-50)
        while self.time.elapsed() > 1 && ard.getHeading() - startAngle < 0.2:
            firData.append((self.ir.firRight.getValues(),
                            self.ir.firLeft.getValues(),
                            ard.getHeading()))
        # find maximimum firRight or firLeft value
        direction = max(firData, lambda x: max(x[0], x[1]))
        if direction[0] > direction[1]:  # right sensor yields farthest distance
            self.robot.setDirection(direction[2]-45)
        else:
            # left sensor yields farthest distance
            self.robot.setDirection(direction[2]+45)
            # or return direction

class Bumpers(threading.Thread):

    def __init__(self, ard):
        threading.Thread.__init__(self)

        self.right = arduino.DigitalInput(ard, 22) # Digital input on pin 22
        self.left = arduino.DigitalInput(ard, 23) # Digital input on pin 23
        # self.bumpBackRight = arduino.DigitalInput(ard, 26)
        # self.bumpBackLeft = arduino.DigitalInput(ard, 29)
        
        self.bumped = (False, False) # (left, right)

    def run(self):
        self.running = True
        while self.running:
            self.bumped = (self.left.getValue(), self.right.getValue())
            time.sleep(0)

    def stop(self):
            self.running = False


class IR(threading.Thread):
    
    def __init__(self, ard):
        threading.Thread.__init__(self)
        
        #self.nirRight = arduino.AnalogInput(ard, 4)
        #self.nirLeft = arduino.Analognput(ard, 5)        
        #self.firRight = arduino.AnalogInput(ard, 6)
        #self.firLeft = arduino.AnalogInput(ard, 7)

        # self.nirRight = ir_dist.IR_Dist(arduino, 4, nirRight)
        # self.nirRight.load()
        # self.nirLeft = ir_dist.IR_Dist(arduino, 5, nirLeft)
        # self.nirRight.load()
        # self.firRight = ir_dist.IR_Dist(arduino, 6, firRight)
            # fixed onto right side, looking left
        # self.firRight.load()
        # self.firLeft = ir_dist.IR_Dist(aruino, 7, firLeft)
        # self.firLeft.load()
        
        # self.nirLeftVal = self.nirLeft.getDist()
        # self.nirRightVal = self.nirRight.getDist()
        # self.firLeftVal = self.firRight.getDist()
        # self.firRightVal = self.firLeft.getDist()

        alpha = 0.35

    def run(self):
        self.running = True;
        self.wall = 'none';
        
        while self.running:
            time.sleep(0)
            #low pass filter
            self.nirLeftVal = (self.nirLeftVal*(1-alpha)
                               + self.nirLeft.getDist()*alpha)
            self.nirRightVal = (self.nirRightVal*(1-alpha)
                                + self.nirRight.getDist*alpha)
            self.firLeftVal = (self.firLeftVal*(1-alpha)
                               + self.firLeft.getDist()*alpha)
            # looking right
            
            self.firRightVal = (self.firRightVal*(1-alpha)
                                + self.firRight.getDist()*alpha)
            # looking left

            if self.firLeftVal < 12:
                self.wall = 'right'
            elif self.firRightVal < 12:
                self.wall = 'left'
            elif self.firRightVal < 12 && self.firLeftVal < 12:
                self.wall = 'front'
            else:
                self.wall = 'None'
            
    def stop(self):
        self.running = False
        

class Motors(threading.Thread):

    def __init__(self, ard):
        threading.Thread.__init__(self)
	""" Arduino must have left motor as 0th motor and right motor as 1st motor for PID. """
        # Pin format: Current, Direction, PWM
        self.left = arduino.Motor(ard, 3, 7, 6)
        self.right = arduino.Motor(ard, 0, 13, 12)
        self.roller = arduino.Motor(ard, 1, 11, 10)
        self.tower = arduino.Motor(ard, 2, 9, 8)
        
        self.currentLeft = arduino.AnalogInput(ard, 3)
        self.currentRight = arduino.AnalogInput(ard, 0)
        self.currentRoller = arduino.AnalogInput(ard, 1)
        self.currentTower = arduino.AnalogInput(ard, 2)

        self.stallLeft = False
        self.stallRight = False
        self.stallRoller = False
        self.stallTower = False

    def run(self):
        self.running = True
        while self.running:            
            if self.currentLeft.getValue() > 800:
                self.stallLeft = True
                self.left.setSpeed(0)
            if self.currentRight.getValue() > 800:
                self.stallRight = True
                self.right.setSpeed(0)
            if self.currentRoller.getValue() > 800:
                self.stallRoller = True
                self.roller.setSpeed(0)
            if self.currentTower.getValue() > 800:
                self.stallTower = True
                self.tower.setSpeed(0)
            time.sleep(0)

    def stop(self):
        self.running = False
        self.right.setSpeed(0)
        self.left.setSpeed(0)
        self.roller.setSpeed(0)
        self.tower.setSpeed(0)


import time

class Timer:
    def __init__(self):
        self.marker = time.time()
    def reset(self):
        self.marker = time.time()
    def elapsed(self):
        return time.time() - self.marker
    def string(self):
        t = self.elapsed()
        return str(int(t / 60)) + ":" + str(int(t) % 60).zfill(2)
