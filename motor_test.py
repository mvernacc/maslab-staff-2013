from robot import Robot
import time

robot = Robot()
robot.start()
time.sleep(1)
# robot.motors.left.setSpeed(30)
# robot.motors.right.setSpeed(30)
robot.motors.tower.setSpeed(30)
time.sleep(3)
# robot.motors.left.setSpeed(0)
# robot.motors.right.setSpeed(0)
robot.motors.tower.setSpeed(0)
robot.stop()
