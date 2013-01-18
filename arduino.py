import sys
sys.path.append("../../lib")

import serial, time
import threading, thread

# Class that handles communication with the arduino
# The general idea is to have a thread that constantly sends actuator commands
# based on arrays and receives sensor data into arrays. The rest of the code
# can then interface with the arduino by reading to and writing from these
# arrays.
class Arduino(threading.Thread):

    # Arrays for keeping track of input / output
    digitalInputs = []
    analogInputs = []
    digitalOutputs = []
    analogOutputs = []
    motorSpeeds = []
    stepperSteps = []
    servoAngles = []
    imuVals = []

    # Arrays for keeping track of ports
    digitalInputPorts = []
    analogInputPorts = []
    digitalOutputPorts = []
    analogOutputPorts = []
    motorPorts = []
    stepperPorts = []
    servoPorts = []
    imus = []

    # Initialize the thread and variables
    def __init__(self):
        threading.Thread.__init__(self)
        self.portOpened = False
        self.killReceived = False

    # Start the connection and the thread that communicates with the arduino
    def run(self):
        self.portOpened = self.connect()
        if (self.portOpened):
            self.sendInitData()
            self.readWriteThread = threading.Thread(target=self.checkPorts)
            self.readWriteThread.start()

    # Stop the thread
    def stop(self):
        # This should tell the thread to finish
        self.killReceived = True
        self.readWriteThread.join()

    # Create the serial connection to the arduino
    def connect(self):
        print "Connecting"
        if self.portOpened: self.close()
        # Loop through possible values of ACMX, and try to connect on each one
        for i in range(4):
            try:
                # Try to create the serial connection
                self.port=serial.Serial(port='/dev/ttyACM{0}'.format(i), baudrate=9600, timeout=0.5)
                if self.port.isOpen():
                    time.sleep(2) # Wait for Arduino to initialize
                    print "Connected"
                    return True
            except:
                # Some debugging prints
                print "Arduino not connected on ACM{0}".format(i)
        print "Failed to connect"
        return False

    # This function builds and writes the output packet to be
    # sent to the arduino
    def writeOutputPacket(self):
        # Build the command packet
        # Command packet format:
        # An1234Bm5678;
        # A, B = Command modes (M - motor command, S - servo command, ...)
        #        Command modes tell the arduino how to interpret what comes
        #        after it.
        # n, m = Number of arguments. This tells the arduino how many
        #        arguments to look for and parse.
        # 1234, 5678 = Arguments. These depend on the command, but specify
        #        things like motor speed and servo angle. Note - in many
        #        places we add 1 before sending an argument and subtract
        #        1 on the other end. This is because we can't send the null
        #        character across.
        # ; = Special command mode that means "end of packet"
        output = ""
        output += "M" + chr(len(self.motorSpeeds))
        for i in self.motorSpeeds:
            output += chr(i)
        output += "T" + chr(len(self.stepperSteps))
        for step in self.stepperSteps:
            output += chr(int(step))
        output += "S" + chr(len(self.servoAngles))
        for i in self.servoAngles:
            output += chr(i) # Make it unsigned and send
        output += "D" + chr(len(self.digitalOutputs))
        for i in self.digitalOutputs:
            output += chr(i)
        output += "A" + chr(len(self.analogOutputs))
        for i in self.analogOutputs:
            output += chr(i)
        output += ";"
        self.port.write(output)
        #print output

    # This function reads and interprets a packet received from the arduino
    # and saves any input data into the appropriate arrays
    def readInputPacket(self):
        # Read in the data packet that the arduino sends back
        # Data packet format is identical to the command packet format,
        # except the modes are different (ex. 'D' for digital instead of
        # 'M' for motor)
        # Possible modes:
        #     'D' - Digital sensor data
        #     'A' - Analog sensor data
        done = False
        while (not done):
            # Read in the mode
            #print "Reading mode"
            mode = self.serialRead()
            if (mode == chr(0)):
                print "Timeout"
                break
            #print "Got:", mode

            # Process arguments based on mode
            # Digital
            if (mode == 'D'):
                length = ord(self.serialRead())
                # Fill the digitalSensors array with incoming data
                for i in range(length):
                    # If we read in a 1, then the digital input is HIGH
                    self.digitalInputs[i] = ord(self.serialRead())==1
            # Analog
            elif (mode == 'A'):
                length = ord(self.serialRead())
                # Fill the analogSensors array with incoming data
                for i in range(length):
                    byte0 = ord(self.serialRead())
                    byte1 = ord(self.serialRead())
                    self.analogInputs[i] = byte1 * 256 + byte0
            # IMU
            elif (mode == 'U'):
                # Read compass (2 bytes)
                byte0 = ord(self.serialRead())
                byte1 = ord(self.serialRead())
                compass = byte1 * 256 + byte0
                # Read accel (3 bytes)
                x = ord(self.serialRead())
                y = ord(self.serialRead())
                z = ord(self.serialRead())
                # Read gyro (1 byte)
                byte0 = ord(self.serialRead())
                byte1 = ord(self.serialRead())
                yaw = byte1 * 256 + byte0
                self.imuVals[0] = (compass, x, y, z, yaw)
            # End of packet
            elif (mode == ';'):
                done = True

    # This function constantly sends out a command packet to the arduino
    # (based on the states of all the arrays) then blocks until it receives
    # a data packet in response (and sets the appropriate arrays based on it).
    # Thus changing the actuator-related arrays and reading from the sensor-
    # related arrays is enough to interact with the arduino.
    def checkPorts(self):
        # If killReceived is set to true, we want to kill this thread
        while not self.killReceived:
            #print "Packet -- writing"
            self.writeOutputPacket()

            #print "Packet -- reading"
            self.readInputPacket()

        # If we get here, we received the kill signal
        self.cleanup()

    # Send initializing data to the arduino, so that it can dynamically set up
    # the actuators and sensors in memory
    def sendInitData(self):
        # The 'I' command mode means initializing data
        output = ""
        output += "I"
        # Motor component of initializing
        output += "M"
        numMotors = len(self.motorPorts)
        output += chr(numMotors)
        for i in range(numMotors):
            current, direction, pwm = self.motorPorts[i]
            output += chr(current)
            output += chr(direction)
            output += chr(pwm)
        # Stepper component of initializing
        output += "T"
        numSteppers = len(self.stepperPorts)
        output += chr(numSteppers)
        for i in range(numSteppers):
            stepPin, enablePin = self.stepperPorts[i]
            output += chr(stepPin)
            output += chr(enablePin)
        # Servo component of initializing
        output += "S"
        numServos = len(self.servoPorts)
        output += chr(numServos)
        for i in range(numServos):
            output+= chr(self.servoPorts[i])
        # Digital input component of initializing
        output += "DI"
        numDigital = len(self.digitalInputPorts)
        output += chr(numDigital)
        for i in range(numDigital):
            output+= chr(self.digitalInputPorts[i])
        # Analog input component of initializing
        output += "AI"
        numAnalog = len(self.analogInputPorts)
        output += chr(numAnalog)
        for i in range(numAnalog):
            output += chr(self.analogInputPorts[i])
        # Digital output component of initializing
        output += "DO"
        numDigital = len(self.digitalOutputPorts)
        output += chr(numDigital)
        for i in range(numDigital):
            output+= chr(self.digitalOutputPorts[i])
        # Analog input component of initializing
        output += "AO"
        numAnalog = len(self.analogOutputPorts)
        output += chr(numAnalog)
        for i in range(numAnalog):
            output += chr(self.analogOutputPorts[i])
        # IMU component of initializing
        if len(self.imus) > 0:
            output += "U"
        # Terminate the command packet
        output += ";"

        self.port.write(output)
        self.port.flush()

        print "Init", output

    # Build a packet that stops all motors and actuators and
    # flush it. This is called when the arduino thread is
    # about to die. It resolves the problem of the motor
    # controller continuing to run the motors after the
    # Arduino stops sending commands.
    def cleanup(self):
        # First, set all of our arrays to reasonable end values
        def zero(val):
            return 0
        self.digitalOutputs = map(zero, self.digitalOutputs)
        self.analogOutputs = map(zero, self.analogOutputs)
        self.motorSpeeds = map(zero, self.motorSpeeds)
        self.stepperSteps = map(zero, self.stepperSteps)
        # Don't modify servos, since this will cause them to move,
        # rather than stop.
        
        # Now send the final output packet
        self.writeOutputPacket()
        # And flush the serial connection
        self.port.flush()
    
    # Wrapper on port.read that checks for debugging
    # messages from the Arduino and prints them out
    def serialRead(self, size=1):
        inp = self.port.read(size)
        if (len(inp) < size):
            return chr(0)
        #while (inp == "/"):
        #    while inp != "\\":
        #        sys.stdout.write(inp)
        #        inp = self.port.read()
        #    inp = self.port.read(size)
        return inp


    # Getting and setting values for sensors and actuators
    def setMotorSpeed(self, motorNum, speed):
        self.motorSpeeds[motorNum] = speed
    def stepStepper(self, stepperNum, step):
        self.stepperSteps[stepperNum] = step
    def setServoAngle(self, servoNum, angle):
        self.servoAngles[servoNum] = angle
    def setDigitalOutput(self, index, value):
        # Digitize value
        if value == 0:
            self.digitalOutputs[index] = 0
        else:
            self.digitalOutputs[index] = 1
    def setAnalogOutput(self, index, value):
        # Clamp value to [0, 1]
        if value <= 0:
            self.digitalOutputs[index] = 0
        elif value >= 1:
            self.digitalOutputs[index] = 1
        else:
            self.digitalOutputs[index] = value
    def getDigitalInput(self, index):
        return self.digitalInputs[index]
    def getAnalogInput(self, index):
        return self.analogInputs[index]
    def getIMUVals(self, index):
        return self.imuVals[index]

    # Functions to set up the components (these are called through the classes
    # below, don't call these yourself!)
    def addMotor(self, currentPort, directionPort, pwmPort):
        self.motorPorts.append((currentPort, directionPort, pwmPort))
        self.motorSpeeds.append(0)
        return len(self.motorSpeeds) - 1
    def addStepper(self, stepPort, enablePort):
        self.stepperPorts.append((stepPort, enablePort))
        self.stepperSteps.append(0)
        return len(self.stepperPorts) - 1
    def addDigitalInput(self, port):
        self.digitalInputPorts.append(port)
        self.digitalInputs.append(None)
        return len(self.digitalInputPorts) - 1
    def addAnalogInput(self, port):
        self.analogInputPorts.append(port)
        self.analogInputs.append(None)
        return len(self.analogInputPorts) - 1
    def addDigitalOutput(self, port):
        self.digitalOutputPorts.append(port)
        self.digitalOutputs.append(0)
        return len(self.digitalOutputPorts) - 1
    def addAnalogOutput(self, port):
        self.analogOutputPorts.append(port)
        self.analogOutputs.append(0)
        return len(self.digitalOutputPorts) - 1
    def addServo(self, port):
        self.servoPorts.append(port)
        self.servoAngles.append(0)
        return len(self.servoPorts) - 1
    def addIMU(self):
        # If we already have an IMU, we can only have one, so just
        # return the index to that
        if len(self.imus) > 0:
            return 0
        else:
            self.imus = [True]
            self.imuVals = [(0, 0, 0, 0)]
            return 0

# Class to interact with a servo
class Servo:
    def __init__(self, arduino, port):
        self.arduino = arduino
        self.index = self.arduino.addServo(port)
    def setAngle(self, angle):
        # Clamp to [0, 180]
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
        self.arduino.setServoAngle(self.index, angle)

# Class to interact with a motor
class Motor:
    def __init__(self, arduino, currentPin, directionPin, pwmPin):
        self.arduino = arduino
        self.index = self.arduino.addMotor(currentPin, directionPin, pwmPin)
    def setSpeed(self, speed):
        # Clamp to [-126, 126]
        if speed < -126:
            speed = -126
        elif speed > 126:
            speed = 126
        # Modify the -126 to 127 range to be 0 to 255 for the Arduino
        speed = speed % 255
        self.arduino.setMotorSpeed(self.index, speed)

class Stepper:
    def __init__(self, arduino, stepPort, enablePort):
        self.arduino = arduino
        self.stepPort = stepPort
        self.enablePort = enablePort
        self.index = self.arduino.addStepper(stepPort, enablePort)
    def step(self, step):
        self.arduino.stepStepper(self.index, step)

# Class to interact with a digital sensor
class DigitalInput:
    def __init__ (self, arduino, port):
        self.arduino = arduino
        self.port = port
        self.index = self.arduino.addDigitalInput(port)
    def getValue(self):
        return self.arduino.getDigitalInput(self.index)

# Class to interact with an analog sensor
class AnalogInput:
    def __init__(self, arduino, port):
        self.arduino = arduino
        self.port = port
        self.index = self.arduino.addAnalogInput(port)
    def getValue(self):
        return self.arduino.getAnalogInput(self.index)

# Class to interact with a digital output
class DigitalOutput:
    def __init__ (self, arduino, port):
        self.arduino = arduino
        self.port = port
        self.index = self.arduino.addDigitalOutput(port)
    def setValue(self, value):
        self.arduino.setDigitalOutput(self.index, value)

# Class to interact with an analog output
class AnalogOutput:
    def __init__ (self, arduino, port):
        self.arduino = arduino
        self.port = port
        self.index = self.arduino.addAnalogOutput(port)
    def setValue(self, value):
        self.arduino.setAnalogOutput(self.index, value)

# Class to interact with an IMU
class IMU:
    def __init__ (self, arduino):
        self.arduino = arduino
        self.index = self.arduino.addIMU()
    def getRawValues(self):
        return self.arduino.getIMUVals(self.index)
