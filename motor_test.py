from robot import Robot
import sys
import time

def main(argv):
    robot = Robot()
    robot.ard.start()
    while robot.ard.portOpened == False: pass
    # if len(argv) == 0:
    #     argv = ['-l', '-r', '-p', '-t']
    if '-l' in argv:
        robot.motors.left.setSpeed(80)
    if '-r' in argv:
        robot.motors.right.setSpeed(80)
    if '-p' in argv:
        robot.motors.roller.setSpeed(20)
    if '-t' in argv:
        robot.motors.tower.setSpeed(100)
    time.sleep(5)
    # robot.motors.left.setSpeed(0)
    # robot.motors.right.setSpeed(0)
    # robot.motors.roller.setSpeed(0)
    # robot.motors.tower.setSpeed(0)
    robot.ard.stop()
   
if __name__ == "__main__":
    main(sys.argv[1:])

