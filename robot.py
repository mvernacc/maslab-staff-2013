import arduino # Import the interface library
import threading, thread
import time
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
        # onOff = arduino.DigitalInput(ard,)
        # redGreen = arduino.DigitalInput(ard,)

    def run(self):
        self.ard.start()
        time.sleep(1)
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
        
        self.nirRight = arduino.DigitalInput(ard, 4)
        self.nirLeft = arduino.DigitalInput(ard, 5)
        #self.firRight = arduino.AnalogInput(ard, 6)
        #self.firLeft = arduino.AnalogInput(ard, 7)
        
        self.nirLeftVal = 0.0
        self.nirRightVal = 0.0
        #self.firLeftVal = 0.0
        #self.firRightVal = 0.0

    def run(self):
        self.running = True;
        while self.running:
            self.nirLeftVal = self.nirLeft.getValue();
            self.nirRightVal = self.nirRight.getValue();
            #self.firLeftVal = self.firLeft.getValue();
            #self.firRightVal = self.firRight.getValue();
    
    def stop(self):
        self.running = False
        

class Motors(threading.Thread):

    def __init__(self, ard):
        threading.Thread.__init__(self)
	""" Arduino must have left motor as 0th motor and right motor as 1st motor for PID. """
        # Pin format: Current, Direction, PWM
        self.left = arduino.Motor(ard, 0, 7, 6)
        self.right = arduino.Motor(ard, 1, 9, 8)
        # self.roller = arduino.Motor(ard, current, direction, pwm)
        self.tower = arduino.Motor(ard, 3, 12, 11)
        
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
            if self.currentRight.getValue() > 800:
                self.stallRight = True
            if self.currentRoller.getValue() > 800:
                self.stallRoller = True
            if self.currentTower.getValue() > 800:
                self.stallTower = True

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
