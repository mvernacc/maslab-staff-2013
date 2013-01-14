import threading
import time
import arduino # Import the interface library
import robotBehavior


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
        robot.pause()
        ard.stop()
    timer = threading.Timer(360.0, halt)
        # Run the halt function after 360 seconds in a different thread
    timer.start() # Actually start the timer, the time counts from this point on                                                                                                                                       


    ####################################run code##############################
    timeout = 5
    speed = 70

    ard.run()  # Start the thread that interacts with the Arduino itself
    robot.run(timeout, speed)
        # wander at 5 second intervals, speed of "70"
    
    while running:
        try:
            feats = vis.get_feat()
            if len(feats) > 0:
                robot.ballFollow()
            else:
                print "No ball"                
                robot.wander(timeout,speed)
                robot.search(1.5*timeout,speed)
            #cv2.waitKey(20)???
        except KeyboardInterrupt:
            print "ending..."
            time.sleep(0.1)
            motor_right.setSpeed(0)
            motor_left.setSpeed(0)
            time.sleep(0.1)
            #ard.stop()
            halt()

        right = bump_right.getValue()
            # should return a TRUE if high, FALSE if low
        left = bump_left.getValue()
        # time.sleep(0.1)
        if right == True:
            robot.turn("left", speed)
        elif left == True:
            robot.turn("right", speed)
        else:
            pass

    
if __name__ == "__main__":
    main(sys.argv[1:])
