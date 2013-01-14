from vision.vision import Vision
from command.feature import Feature
import threading
import time
import arduino # Import the interface library
import robotBehavior
import sys, getopt

def main(argv):

    red_side = True

    try:
        opts, args = getopt.getopt(argv,'', ['color='])
    except getopt.GetoptError:
        print "usage: 'main.py --color=<c>', where <c> is 'red' or 'green'"
    for opt, arg in opts:
        if opt == '--color':
            if arg == 'green':
                red_side = False
                print 'looking for green balls'
            elif arg == 'red':
                print 'looking for red balls'    

    ################################## Arduino setup ############################
    ard = arduino.Arduino() # Create the Arduino object


    # Create other actuators, sensors, etc.
    motor_right = arduino.Motor(ard, 0, 7, 9)
        # Motor with pwm output on pin 9, direction pin on digital pin 7, and current sensing pin on pin A0
    motor_left = arduino.Motor(ard, 1, 8, 10)
        # Motor with pwm output on pin 10, direction pin on digital pin 8, and current sensing pin on pin A1
    bump_right = arduino.DigitalInput(ard, 22) # Digital input on pin 22
        # bump right
    bump_left = arduino.DigitalInput(ard, 23) # Digital input on pin 23
        # bump left
    #imu_SCL = arduino.AnalogInput(ard, 5)  # Analog input on pin A5
    #imu_SDA = arduino.AnalogInput(ard, 4)  # Analog input on pin A4

    vis = Vision(red_side, True)        
    robot = robotBehavior.Robot(arduino, motor_right, motor_left, vis)

    #################################### halt code ###############################
    # Global variable to control the main thread                                                                                                                                                                       
    running = True

    # Function to stop the main thread                                                                                                                                                                                 
    def halt():
        print "Stopping"
        global running
        running = False
        robot.end()
        ard.stop()
    timer = threading.Timer(60.0, halt)
        # Run the halt function after 180 seconds in a different thread
    timer.start() # Actually start the timer, the time counts from this point on                                                                                                                                       


    ####################################run code##############################

    ard.run()  # Start the thread that interacts with the Arduino itself
    robot.search() # start the robot out in the search state
   
if __name__ == "__main__":
    main(sys.argv[1:])
