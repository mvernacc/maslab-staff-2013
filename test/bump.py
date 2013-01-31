import time, sys, getopt, os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from robot import Robot

def main(argv):
    try:
        opts, args = getopt.getopt(argv, '', ['duration='])
    except getopt.GetoptError:
        print "Arguments: --duration=#"
    duration = None
    analog = False
    for opt, arg in opts:
        if opt == '--duration':
            duration = int(arg)
    try:
        robot = Robot()
        robot.start()
        while robot.ready == False: pass
        marker = time.time()
        while duration == None or time.time() - marker < duration:
            print robot.bumpers.left.getValue(), robot.bumpers.right.getValue()
    except:
        pass
    robot.stop()

if __name__ == "__main__":
    main(sys.argv[1:])
