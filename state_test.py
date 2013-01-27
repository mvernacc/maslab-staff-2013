from robot import Robot
from fsm import *
import time, sys

def main(argv):
    if len(argv) > 0:
        class_name = argv[0]
        if class_name in globals():
            robot = Robot()
            robot.start()
            time.sleep(3)
            print "TESTING:", class_name
            globals()[class_name](robot).next_state()
            robot.stop()
   
if __name__ == "__main__":
    main(sys.argv[1:])
