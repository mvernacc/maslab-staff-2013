import arduino # Import the interface library
import threading, thread
import time
import ir_dist
from vision.vision import Vision, Color, Feature

class Robot(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)

        # Arduino and sensor properties
        self.ard = arduino.Arduino()
        self.pid = arduino.PID(self.ard)
        self.motors = Motors(self.ard)
        self.bumpers = Bumpers(self.ard)
        self.ir = IR(self.ard)
        self.vision = Vision()
        self.vision.color = Color.Red
        self.vision.features = Feature.Ball
        self.time = Timer(self)
        self.servoBridge = arduino.Servo(self.ard, 6)
        self.servoGate = arduino.Servo(self.ard, 3)
        # self.bridgeBump = arduino.DigitalInput(self.ard, 27)

        # Properties for match
        self.ready = False
        self.scoring = False
        self.buttoned = False # Button has been pushed
        self.deployed = False # Bridge has been deployed
        self.map = {}
        self.tower = []
        self.wall = []
        self.repeatedBarcodes = False

    def run(self):
        self.ard.start()
        while self.ard.portOpened == False:
            time.sleep(0.05)

        # self.motors.start()
        self.servoGate.setAngle(45)
        self.servoBridge.setAngle(5)
        self.bumpers.start()
        self.ir.start()
        self.vision.start()

        self.ready = True

    def stop(self):
        self.pid.stop()
        # self.motors.stop()
        self.servoGate.setAngle(45)
        self.servoBridge.setAngle(5)
        self.bumpers.stop()
        self.ir.stop()
        self.vision.stop()
        time.sleep(1)
        self.ard.stop()
        
        self.ready = False

    def reverse(self, bumped):
        speed = 80
        # Reverse for 2 seconds
        self.motors.right.setSpeed(-speed)
        self.motors.left.setSpeed(-speed)
        time.sleep(2)
        # Rotate for 1 second
        if bumped[0] == True:
            # Left bump sensor hit
            self.motors.right.setSpeed(-speed)
            self.motors.left.setSpeed(speed)
        elif bumped[1] == True:
            # Right bump sensor hit
            self.motors.right.setSpeed(speed)
            self.motors.left.setSpeed(-speed)
        time.sleep(1)
        # Move forward for 1 second
        self.motors.right.setSpeed(speed)
        self.motors.left.setSpeed(speed)
        time.sleep(1)
        self.motors.right.setSpeed(0)
        self.motors.left.setSpeed(0)

    def getFarthestPoint(self):
        startAngle = ard.getHeading()
        firData = []
        self.ir.running = True
        self.motors.left.setSpeed(50)
        self.motors.right.setSpeed(-50)
        while self.time.elapsed() > 1 and ard.getHeading() - startAngle < 0.2:
            firData.append((self.ir.firRight.getValues(),
                            self.ir.firLeft.getValues(),
                            ard.getHeading()))
        # # find maximimum firRight or firLeft value
        # direction = max(firData, lambda x: max(x[0], x[1]))
        # if direction[0] > direction[1]:  # right sensor yields farthest distance
        #     self.robot.setDirection(direction[2]-45)
        # else:
        #     # left sensor yields farthest distance
        #     self.robot.setDirection(direction[2]+45)
        #     # or return direction

class Bumpers(threading.Thread):

    def __init__(self, ard):
        threading.Thread.__init__(self)

        self.right = arduino.DigitalInput(ard, 42)
        self.left = arduino.DigitalInput(ard, 36)

        self.bumped = (False, False) # (left, right)

    def run(self):
        self.running = True
        while self.running:
            self.bumped = (self.left.getValue(), self.right.getValue())
            time.sleep(0.05)

    def stop(self):
            self.running = False


class IR(threading.Thread):
    
    def __init__(self, ard):
        threading.Thread.__init__(self)
        
        self.nirLeftValue = None
        self.nirRightValue = None

        self.nirRight = ir_dist.IR_Dist(ard, 5, 'rightNIR')
        self.nirLeft = ir_dist.IR_Dist(ard, 4, 'leftNIR')
        self.firLeft = ir_dist.IR_Dist(ard, 7, 'leftFIR')

        self.nirLeft.load()
        self.nirRight.load()
        self.firLeft.load()

    def run(self):
        self.running = True;
        self.wall = 'none';
        
        while self.running:
            self.nirLeftValue = self.nirLeft.getDist()
            self.nirRightValue = self.nirRight.getDist()
            self.firLeftValue = self.firLeft.getDist()
            if self.firLeftValue < 20:
                self.wall = 'front'
            # elif self.nirLeftValue < 20 and self.nirRightValue > 20:
            #     self.wall = 'right'
            # elif self.nirLeftValue > 20 and self.nirRightValue < 20:
            #     self.wall = 'left'
            else:
                self.wall = 'none'
            time.sleep(0.05)

    def stop(self):
        self.running = False


class Motors(threading.Thread):

    def __init__(self, ard):
        threading.Thread.__init__(self)
	""" Arduino must have left motor as 0th motor and right motor as 1st motor for PID. """
        # Pin format: Current, Direction, PWM
        self.left = arduino.Motor(ard, 0, 43, 9)
        self.right = arduino.Motor(ard, 15, 37, 12)
        self.roller = arduino.Motor(ard, 14, 39, 10)
        self.tower = arduino.Motor(ard, 13, 41, 11)        

        self.left.setSpeed(0)
        self.right.setSpeed(0)
        self.roller.setSpeed(0)
        self.tower.setSpeed(0)

        self.currentLeft = arduino.AnalogInput(ard, 0)
        self.currentRight = arduino.AnalogInput(ard, 15)
        self.currentRoller = arduino.AnalogInput(ard, 14)
        self.currentTower = arduino.AnalogInput(ard, 13)

        self.stallLeft = False
        self.stallRight = False
        self.stallRoller = False
        self.stallTower = False

    def run(self):
        while self.currentLeft.getValue() == None or self.currentRight.getValue() == None or self.currentRoller.getValue() == None or self.currentTower.getValue() == None:
            time.sleep(0.1)
        self.running = True
        while self.running:
            print "Left: {0:4.0f}   Right: {1:4.0f}   Roller: {2:4.0f}   Tower: {3:4.0f}".format(self.currentLeft.getValue(), self.currentRight.getValue(), self.currentRoller.getValue(), self.currentTower.getValue())
            if self.currentLeft.getValue() > 800:
                print "Stalling left"
                self.stallLeft = True
                self.left.setSpeed(0)
            if self.currentRight.getValue() > 800:
                print "Stalling right"
                self.stallRight = True
                self.right.setSpeed(0)
            if self.currentRoller.getValue() > 300:
                print "Stalling roller"
                self.stallRoller = True
                self.roller.setSpeed(0)
                time.sleep(1)
                self.roller.setSpeed(-63)
                time.sleep(1)
                self.roller.setSpeed(0)
                time.sleep(1)
                self.roller.setSpeed(63)
                time.sleep(1)
                self.roller.setSpeed(126)
                self.stallRoller = False
            if self.currentTower.getValue() > 700:
                print "Stalling tower"
                self.stallTower = True
                self.tower.setSpeed(0)
            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.right.setSpeed(0)
        self.left.setSpeed(0)
        self.roller.setSpeed(0)
        self.tower.setSpeed(0)


class Timer(threading.Thread):
    def __init__(self, robot):
        threading.Thread.__init__(self)
        self.marker = None
        self.robot = robot
    def reset(self):
        self.marker = time.time()
    def run(self):
        self.marker = time.time()
        while self.elapsed() < 120:
            time.sleep(5)
        self.robot.scoring = True
        while self.elapsed() < 180:
            time.sleep(5)
        self.robot.stop()
    def elapsed(self):
        if self.marker == None: return 0
        return time.time() - self.marker
    def string(self):
        t = self.elapsed()
        return str(int(t / 60)) + ":" + str(int(t) % 60).zfill(2)
