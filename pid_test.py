from robot import Robot
from vision.vision import Color, Feature
import time
import sys

def main(argv):
    robot = Robot()
    robot.vision.color = Color.Red
    robot.vision.features = Feature.Ball
    robot.start()
    time.sleep(1)
    robot.motors.left.setSpeed(40)
    robot.motors.right.setSpeed(40)
    robot.pid.start(1.113, 0, 0.00001)
    while robot.time.elapsed() < 10:
        detections = robot.vision.detections
        if detections[Feature.Ball] != None:
            # print detections[Feature.Ball]
            relPos = 2.0 * detections[Feature.Ball][0] / robot.vision.width - 1
            # print int(40 * relPos)
            robot.pid.setError(int(40 * relPos))
    # robot.motors.left.setSpeed(0)
    # robot.motors.right.setSpeed(0)
    # robot.motors.tower.setSpeed(0)
    # robot.pid.stop()
    robot.stop()
   
if __name__ == "__main__":
    main(sys.argv[1:])
