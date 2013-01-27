obot,import arduino # Import the interface library
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
        self.motors = Motors(self.ard)
        self.bumpers = Bumpers(self.ard)
        self.ir = IR(self.ard)
        self.pid = arduino.PID(self.ard)
        self.vision = Vision()
        self.vision.color = Color.Red
        self.vision.features = Feature.Ball
        self.time = Timer()

        # servoGate = arduino.Servo(ard, pwm)
        go = arduino.DigitalInput(ard,30)
        # redGreen = arduino.DigitalInput(ard,)

    def run(self):
        self.ard.start()
        time.sleep(1)
        chosen = False
        print "Choose color:  Right = red, Left = green"
        while chosen == False:
            if arduino.DigitalInput(ard, 22) == True:
                #Right bump sensor
                self.color = Color.Red
                chosen = True
            elif arduino.DigitalInput(ard,23) == True:
                # Left bump sensor
                self.color = Color.Green
                chosen = True
            else:
                pass

        while go.getValue() == False:
            print "waiting"

        # if code gets here, go.getValue() == True
        self.time.start()
        self.motors.start()
        self.bumpers.start()
        self.ir.start()
        self.vision.start()

    def stop(self):
        self.motors.stop()
        self.bumpers.stop()
        self.ir.stop()
        self.vision.stop()
        time.sleep(1)
        self.ard.stop()

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
        
        # self.nirLeftVal = self.nirLeft.getDist()
        # self.nirRightVal = self.nirRight.getDist()

        alpha = 0.35

    def run(self):
        self.running = True;
        while self.running:
            pass
            #low pass filter
            # self.nirLeftVal = (self.nirLeftVal*(1-alpha)
            #                    + self.nirLeft.getDist()*alpha)
            # self.nirRightVal = (self.nirRightval*(1-alpha)
            #                     + self.nirRight.getDist*alpha)
            
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
        
        self.currentLeft = arduino.AnalogInput(ard, 0)
        self.currentRight = arduino.AnalogInput(ard, 1)
        self.currentRoller = arduino.AnalogInput(ard, 2)
        self.currentTower = arduino.AnalogInput(ard, 3)

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
                self.tower.setSpeed(0)
            if self.currentTower.getValue() > 800:
                self.stallTower = True
                self.tower.setSpeed(0)

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
