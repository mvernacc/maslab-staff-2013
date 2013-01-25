from robot import Robot
from vision.vision import Color, Feature
import time
import sys

def main(argv):
    robot = Robot()
    robot.vision.color = Color.Green
    robot.vision.features = Feature.Ball
    robot.start()
    robot.pid.reset(1, 0, 0)
    robot.motors.left.setSpeed(30)
    robot.motors.right.setSpeed(30)
    while robot.time.elapsed() < 10:
        detections = robot.vision.detections
        if robot.vision.detections[Feature.Ball] != None:
            # print robot.vision.detections[Feature.Ball]
            relPos = 2.0 * robot.vision.detections[Feature.Ball][0] / robot.vision.width - 1
            # print int(30 * relPos)
            robot.pid.setError(int(30 * relPos))
    # robot.motors.left.setSpeed(0)
    # robot.motors.right.setSpeed(0)
    # robot.motors.tower.setSpeed(0)
    robot.pid.stop()
    robot.stop()
   
if __name__ == "__main__":
    main(sys.argv[1:])
