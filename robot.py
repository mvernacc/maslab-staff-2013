import arduino # Import the interface library
import threading, thread
import time
#import ir_dist
from vision.vision import Vision, Color, Feature

import cv2
import cv
import sys, getopt
import ir_dist

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
#        servoBridge = arduino.Servo(ard, 5)
#        servoGate = arduino.Servo(ard, 4)
#        bridgeBump = arduino.DigitalInput(ard, 27)

    def run(self):
        self.ard.start()
        # while self.ard.portOpened == False:
        #     time.sleep(0)
        time.sleep(1)

        # chosen = False
        # print "Choose color:  Right = red, Left = green"
        # while chosen == False:
        #     if self.bumpers.right.getValue() == True:
        #         #Right bump sensor
        #         self.color = Color.Red
        #         chosen = True
        #     elif self.bumpers.left.getValue() == True:
        #         # Left bump sensor
        #         self.color = Color.Green
        #         chosen = True
        #     else:
        #         pass

#        while go.getValue() == False:
#            print "waiting"

        # if code gets here, go.getValue() == True
        # self.time.reset() moved to fsm
        self.motors.start()
        # self.servoBridge.setAngle(90)
        self.bumpers.start()
        self.ir.start()
        self.vision.start()
#        running = True
#        while running == True:
#            if int(self.time.elapsed() % 5) <= 2 && self.time.elapsed() < 120:
#                self.robot.vision.features = Feature.Tower | Feature.Wall | Feature.QRCode
#                if detections[Feature.Tower] != None:
#                    self.tower.append((arduino.getHeading(ard), detections[Feature.Tower]))
#                if detections[Feature.Wall] != None:
#                    self.wall = ((arduino.getHeading(ard), detections[Feature.Wall]))
             
        

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
#        direction = max(firData, lambda x: max(x[0], x[1]))
#        if direction[0] > direction[1]:  # right sensor yields farthest distance
#            self.robot.setDirection(direction[2]-45)
#        else:
            # left sensor yields farthest distance
 #           self.robot.setDirection(direction[2]+45)
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
            time.sleep(0.0001)

    def stop(self):
            self.running = False


class IR(threading.Thread):
    
    def __init__(self, ard):
        threading.Thread.__init__(self)
        
        self.nirRight = ir_dist.IR_Dist(ard, 5, 'near')
        self.nirLeft = ir_dist.IR_Dist(ard, 4, 'near')        
        #self.firRight = arduino.AnalogInput(ard, 6)
        #self.firLeft = arduino.AnalogInput(ard, 7)

        self.nirLeft.load()
        self.nirRight.load()
        # self.firRight.load()
        # self.firLeft.load()

    def run(self):
        self.running = True;
        self.wall = 'none';
        
        while self.running:
            time.sleep(0.0001)
            self.nirLeftVal = self.nirLeft.getDist()
            self.nirRightVal = self.nirRight.getDist()
            print 'IR readings: left= ' + str(self.nirLeftVal) + ' cm, right = ' + str(self.nirRightVal) + ' cm'

    def stop(self):
        self.running = False
        

class Motors(threading.Thread):

    def __init__(self, ard):
        threading.Thread.__init__(self)
	""" Arduino must have left motor as 0th motor and right motor as 1st motor for PID. """
        # Pin format: Current, Direction, PWM
        self.left = arduino.Motor(ard, 3, 7, 6)
        self.right = arduino.Motor(ard, 0, 13, 12)
        # self.roller = arduino.Motor(ard, 1, 5, 4)
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
            print self.currentTower.getValue()
            if self.currentLeft.getValue() > 800:
                print "Stalling left"
                self.stallLeft = True
                self.left.setSpeed(0)
            if self.currentRight.getValue() > 800:
                print "Stalling right"
                self.stallRight = True
                self.right.setSpeed(0)
            if self.currentRoller.getValue() > 800:
                print "Stalling roller"
                self.stallRoller = True
                self.roller.setSpeed(0)
            if self.currentTower.getValue() > 800:
                print "Stalling tower"
                self.stallTower = True
                self.tower.setSpeed(0)
            time.sleep(0)

    def stop(self):
        self.running = False
        self.right.setSpeed(0)
        self.left.setSpeed(0)
        # self.roller.setSpeed(0)
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
