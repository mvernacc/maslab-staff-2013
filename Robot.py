import arduino # Import the interface library
import threading, thread
from vision.vision import Vision, Color, Feature

import cv2
import cv
import sys, getopt


class Robot(threading.Thread):
    
    def __init__(self, arduino, color):
        # color = what color ball we're going for
        
        self.ard = arduino # Create the Arduino object
        self.bumpers = Bumper()
        self.ir = IR()
        self.motor = Motor()
        self.visBall = Vision(color)


        #servoGate = arduino.Servo(ard, pwm)

        
        #onOff = arduino.DigitalInput(ard,)
        #redGreen = arduino.DigitalInput(ard,)

    def run(self):
        self.ard.run()
        self.bumpers.run()
        self.ir.run()
        self.motor.run()
        self.visBall.detectObjects(Feature.Ball)

    def stop(self):    
        self.motorRight.setSpeed(0)
        self.motorLeft.setSpeed(0)
        self.ard.stop()
        self.bumpers.stop()
        self.vision.stop()
        self.ir.stop()

        
class Bumper(threading.Thread):
    def __init__(self):

        self.bumpFrontRight = arduino.DigitalInput(ard, 22) # Digital input on pin 22
        self.bumpFrontLeft = arduino.DigitalInput(ard, 23) # Digital input on pin 23
        #self.bumpBackRight = arduino.DigitalInput(ard, 26)
        #self.bumpBackLeft = arduino.DigitalInput(ard, 29)
        
        self.bumped = (False, False)
            # (Left, Right)

    def run(self):
        while self.bumped == (False, False):
            self.bumped = (bumpFrontLeft.getValue(), bumpFrontRight.getValue())
        while self.bumped == (True, False):
            self.bumped = (True, bumpFrontRight.getValue())
        while self.bumped == (False, True):
            self.bumped = (bumpFrontLeft.getValue(), True)

    def stop(self):
            self.bumped == (False, False);


class IR(threading.Thread):
    
    def __init__(self):
        
        self.nirRight = arduino.AnalogInput(ard, 4)
        self.nirLeft = arduino.AnalogInput(ard, 5)
        #self.firRight = arduino.AnalogInput(ard, 6)
        #self.firRight = arduino.AnalogInput(ard, 7)
        
        self.nirLeftVal = 0.0
        self.nirRightVal = 0.0
        #self.firLeftVal = 0.0
        #self.firRightVal = 0.0
        self.running = True;

    def run(self):
        while self.running:
            self.nirLeftVal = self.nirLeft.getValue();
            self.nirRightVal = self.nirRight.getValue();
            #self.firLeftVal = self.firLeft.getValue();
            #self.firRightVal = self.firRight.getValue();
    
    def stop(self):
        self.running = False
        

class Motors(threading.Thread):
    def __init__(self):
         # Create other actuators, sensors, etc.
        self.motorRight = arduino.Motor(ard, 0, 9, 8)
            # Motor with pwm output on pin 8, direction pin on digital pin 9, and current sensing pin on pin A0
        self.motorLeft = arduino.Motor(ard, 1, 11, 10)
            # Motor with pwm output on pin 10, direction pin on digital pin 11, and current sensing pin on pin A1
        self.motorPickUp = arduino.Motor(ard, current, direction, pwm)
        self.motorTower = arduino.Motor(ard, current, direction, pwm)
        
        self.LeftCurrent = ard.AnalogInput(ard, 0)
        self.RightCurrent = ard.AnalogInput(ard, 1)
        self.PickUpCurrent = ard.AnalogInput(ard, 2)
        self.RollerCurrent = ard.AnalogInput(ard, 3)

        self.stallLeft = False;
        self.stallRight = False;
        self.stallPickUp = False;
        self.stallPickUp = False;

        self.running = True

    def run(self):
        while running:            
            if self.LeftCurrent.getValue() > 800:
                self.stallLeft = True
            if self.RightCurrent.getValue() > 800:
                self.stallRight = True
            if PickUpCurrent.getValue() > 800:
                self.stallPickUp = True
            if RollerCurrent.getValue() > 800:
                self.stalPickUp = True

    def stop(self):
        self.running = False
