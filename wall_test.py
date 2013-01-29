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
    # robot.motors.left.setSpeed(100)
    # robot.motors.right.setSpeed(100)
    # robot.pid.start(0.4, 0.0001, 100)
    while robot.time.elapsed() < 20:
        detections = robot.vision.detections
        if detections[Feature.Ball] != None:
            # print detections[Feature.Ball]
            relPos = 2.0 * detections[Feature.Ball][0] / robot.vision.width - 1
            print relPos
            robot.pid.setError(int(126 * relPos))
        # else:
        #     robot.motors.left.setSpeed(0)
        #     robot.motors.right.setSpeed(0)
        #     robot.pid.reset(0, 0, 0)
    # robot.motors.left.setSpeed(0)
    # robot.motors.right.setSpeed(0)
    # robot.motors.tower.setSpeed(0)
    # robot.pid.stop()
    robot.stop()
   
if __name__ == "__main__":
    main(sys.argv[1:])
