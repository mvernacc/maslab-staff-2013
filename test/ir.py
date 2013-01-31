import time, sys, getopt, os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from robot import Robot

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'ad', ['analog', 'distance', 'duration='])
    except getopt.GetoptError:
        print "Arguments: -a -d --analog --distance --duration=#"
    duration = None
    analog = False
    for opt, arg in opts:
        if opt == '-a':
            analog = True
        if opt == '--analog':
            analog = True
        if opt == '--duration':
            duration = int(arg)
    try:
        robot = Robot()
        robot.start()
        while robot.ready == False: pass
        marker = time.time()
        if analog == True:
            while duration == None or time.time() - marker < duration:
                print "Analog: {0:6.1f} {1:6.1f} {2:6.1f}".format(robot.ir.nirLeft.ain.getValue(), robot.ir.nirRight.ain.getValue(), robot.ir.firLeft.ain.getValue())
        else:
            while duration == None or time.time() - marker < duration:
                print "Distance: {0:6.1f} {1:6.1f} {2:6.1f}".format(robot.ir.nirLeft.getDist(), robot.ir.nirRight.getDist(), robot.ir.firLeft.getDist())
    except:
        pass
    robot.stop()

if __name__ == "__main__":
    main(sys.argv[1:])
