import time, sys, getopt, os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from robot import Robot

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'cod:', ['duration='])
    except getopt.GetoptError:
        print "Arguments: -c -o -d"
    try:
        robot = Robot()
        robot.start()
        while robot.ready == False: pass
        marker = time.time()
        duration = None
        delay = None
        for opt, arg in opts:
            if opt == '-c':
                robot.servoGate.setAngle(45)
                robot.servoBridge.setAngle(5)
            if opt == '-o':
                robot.servoGate.setAngle(15)
                robot.servoBridge.setAngle(150)
            if opt == '-d':
                robot.servoGate.setAngle(45)
                robot.servoBridge.setAngle(150)
                delay = int(arg)
            if opt == '--duration':
                duration = int(arg)
        robot.motors.roller.setSpeed(126)
        robot.motors.tower.setSpeed(-100)
        while duration == None or time.time() - marker < duration:
            time.sleep(0.1)
            if delay != None and time.time() - marker > delay:
                robot.servoGate.setAngle(15)
                delay = None
    except:
        pass
    robot.stop()

if __name__ == "__main__":
    main(sys.argv[1:])
