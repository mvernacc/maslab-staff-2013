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
    robot.motors.left.setSpeed(0)
    robot.motors.right.setSpeed(0)
    robot.pid.start(0.6, 0.0001, 100)
    while robot.time.elapsed() < 20:
        d = robot.ir.nirLeftValue # get the distance read by the left near ir sensor
        error = 30 - d    
        robot.pid.setError(int(error))
    robot.motors.left.setSpeed(0)
    robot.motors.right.setSpeed(0)
    robot.pid.stop()
    robot.stop()
   
if __name__ == "__main__":
    main(sys.argv[1:])
