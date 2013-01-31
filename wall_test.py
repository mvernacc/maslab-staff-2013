# Test of Wall following
# uses pid to maintain a fixed distance from a wall on the left side of the robot
from robot import Robot
from vision.vision import Color, Feature
import time
import sys

def main(argv):
    robot = Robot()
    robot.vision.color = Color.Green
    robot.vision.features = Feature.Ball
    robot.start()
    time.sleep(1)
    robot.motors.left.setSpeed(80)
    robot.motors.right.setSpeed(80)
    robot.pid.start(2, 0, 0)

    while robot.ir.nirLeftValue == None or robot.ir.nirRightValue == None:
        pass
    # side = 'right'
    # if robot.ir.nirLeftValue < robot.ir.nirLeftValue:
    #     side = 'left'
    side = 'left'
        
    while robot.time.elapsed() < 20:
        if side == 'left':
            error = 30 - robot.ir.nirLeftValue
        else:
            error = robot.ir.nirRightValue - 30

        robot.pid.setError(int(error))
	# if robot.ir.wall == 'none':
        #     pass
        # if robot.ir.wall == 'front':
        #     if side == 'left':
        #         robot.motors.left.setSpeed(30)
        #         robot.motors.right.setSpeed(-30)
        #     else:
        #         robot.motors.left.setSpeed(-30)
        #         robot.motors.right.setSpeed(30)
        #     time.sleep(2)
    robot.motors.left.setSpeed(0)
    robot.motors.right.setSpeed(0)
    robot.pid.stop()
    robot.stop()
   
if __name__ == "__main__":
    main(sys.argv[1:])
