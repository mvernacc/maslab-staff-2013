import arduino # Import the interface library
import threading, thread
from vision.vision import Vision, Color, Feature

import cv2
import cv
import sys, getopt


class Robot(threading.Thread):
    
    def __init__(self, color):
        # color = what color ball we're going for
        
        self.ard = arduino.Arduino() # Create the Arduino object
        self.bumpers = Bumpers()
        self.ir = IR()
        self.motors = Motors()
        self.vision = Vision()
        self.vision.color = color
        self.vision.features = Feature.Ball
        self.time = Timer()

        #servoGate = arduino.Servo(ard, pwm)
        #onOff = arduino.DigitalInput(ard,)
        #redGreen = arduino.DigitalInput(ard,)

    def run(self):
        self.ard.start()
        self.bumpers.start()
        self.ir.start()
        self.motor.start()
        self.vision.start()

    def stop(self):
        self.bumpers.stop()
        self.ir.stop()
        self.motor.stop()
        self.vision.stop()
        self.ard.stop()

        
class Bumpers(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.bumpFrontRight = arduino.DigitalInput(ard, 22) # Digital input on pin 22
        self.bumpFrontLeft = arduino.DigitalInput(ard, 23) # Digital input on pin 23
        # self.bumpBackRight = arduino.DigitalInput(ard, 26)
        # self.bumpBackLeft = arduino.DigitalInput(ard, 29)
        
        self.bumped = (False, False) # (left, right)

    def run(self):
        self.running = True
        while self.running:
            self.bumped = (bumpFrontLeft.getValue(), bumpFrontRight.getValue())

    def stop(self):
            self.running = False


class IR(threading.Thread):
    
    def __init__(self):
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

    def __init__(self):
        threading.Thread.__init__(self)
	""" Arduino must have left motor as 0th motor and right motor as 1st motor for PID. """
        self.motorLeft = arduino.Motor(ard, 1, 11, 10)
            # Motor with pwm output on pin 10, direction pin on digital pin 11, and current sensing pin on pin A1
        self.motorRight = arduino.Motor(ard, 0, 9, 8)
            # Motor with pwm output on pin 8, direction pin on digital pin 9, and current sensing pin on pin A0
        # self.motorPickUp = arduino.Motor(ard, current, direction, pwm)
        # self.motorTower = arduino.Motor(ard, current, direction, pwm)
        
        self.currentLeft = ard.AnalogInput(ard, 0)
        self.currentRight = ard.AnalogInput(ard, 1)
        self.currentPickUp = ard.AnalogInput(ard, 2)
        self.currentTower = ard.AnalogInput(ard, 3)

        self.stallLeft = False;
        self.stallRight = False;
        self.stallPickUp = False;
        self.stallTower = False;

    def run(self):
        self.running = True
        while running:            
            if self.currentLeft.getValue() > 800:
                self.stallLeft = True
            if self.currentRight.getValue() > 800:
                self.stallRight = True
            if self.currentPickUp.getValue() > 800:
                self.stallPickUp = True
            if self.currentTower.getValue() > 800:
                self.stallPickUp = True

    def stop(self):
        self.running = False
        self.motorRight.setSpeed(0)
        self.motorLeft.setSpeed(0)
        self.motorPickUp.setSpeed(0)
        self.motorTower.setSpeed(0)


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
