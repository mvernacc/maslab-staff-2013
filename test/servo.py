import time, sys, getopt, os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from robot import Robot

def main(argv):
    try:
        opts, args = getopt.getopt(argv, '', ['gate=', 'bridge='])
    except getopt.GetoptError:
        print "Arguments: --gate=# --bridge="
    try:
        robot = Robot()
        robot.start()
        while robot.ready == False: pass
        for opt, arg in opts:
            if opt == '--gate':
                robot.servoGate.setAngle(int(arg))
            if opt == '--bridge':
                robot.servoBridge.setAngle(int(arg))
        time.sleep(0.5)
    except:
        pass
    robot.stop()

if __name__ == "__main__":
    main(sys.argv[1:])
