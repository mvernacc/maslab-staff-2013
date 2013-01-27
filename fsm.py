import time
import arduino
import random
import threading
from robot import Robot
from vision.vision import Vision, Color, Feature

class State:
    def __init__(self, robot, options = None):
        # Reference the robot to access properties
        self.robot = robot
        self.options = options
        self.start_time = time.time()
    def next_state(self):
        raise NotImplementedError
    def state_time(self):
        return time.time() - self.start_time
    def log(self, message):
        print self.robot.time.string() + "   " + message

class FiniteStateMachine:
    def __init__(self, color = Color.Red):
        # Store match properties
        self.color = color
        self.state = None

        # Store robot properties
        self.robot = Robot()
        self.robot.start()
        time.sleep(1)

    def start(self):
       # self.state = StartState(self.robot)
        self.state = ScanState(self.robot)
        while self.robot.time.elapsed() < 180:
            try:
                print self.robot.time.string() + " " + self.state.__class__.__name__
                self.state = self.state.next_state()
            except KeyboardInterrupt:
                self.stop()
        self.stop()

    def stop(self):
        # Kill everything
        self.robot.stop()
        time.sleep(0.1)

    def time_elapsed(self):
        return time.time() - self.start_time

### Temporary strategy used for Mock 1 (and Mock 2?)

class StartState(State):
    def next_state(self):
        start_code = (False, False)
        while start_code == (False, False):
            start_code = self.robot.bumpers.bumped
        if start_code[0]:
            self.robot.vision.color = Color.Green
            self.log("Playing for GREEN")
        elif start_code[1]:
            self.robot.vision.color = Color.Red
            self.log("Playing for RED")
        self.robot.time.reset()
        while self.robot.time.elapsed() < 1:
            pass
        # self.robot.motors.roller.setSpeed(60)
        return ScanState(self.robot)

class ScanState(State):
    def next_state(self):
        # Rotate around
        direction = random.choice([-1, 1])
        self.robot.motors.left.setSpeed(-direction * 40)
        self.robot.motors.right.setSpeed(direction * 40)
        # while self.state_time() < 0.5:
        #     pass
        self.robot.vision.features = Feature.Ball | Feature.Wall
        while self.state_time() < 4:
            if self.robot.time.elapsed() < 120:
                if Feature.Ball in self.robot.vision.detections:
                    return FollowBallState(self.robot)
            else:
                if Feature.Wall in self.robot.vision.detections:
                    return FollowWallState(self.robot)
        return WanderState(self.robot)

class WanderState(State):
    def next_state(self):
        # Move forward
        self.robot.motors.left.setSpeed(50)
        self.robot.motors.right.setSpeed(50)
        self.robot.vision.features = Feature.Ball
        while self.state_time() < 4:
            if True in self.robot.bumpers.bumped:
                return ReverseState(self.robot)
            if Feature.Ball in self.robot.vision.detections:
                return FollowBallState(self.robot)
        return ScanState(self.robot)

class ReverseState(State):
    def next_state(self):
        self.robot.motors.right.setSpeed(-40)
        self.robot.motors.left.setSpeed(-40)
        while self.state_time() < 1:
            pass
        return ScanState(self.robot)

class FollowBallState(State):
    def next_state(self):
        # PID on ball's visual position
        self.robot.vision.features = Feature.Ball
        while self.robot.time.elapsed() < 120:
            if True in self.robot.bumpers.bumped:
                return ReverseState(self.robot)
            if Feature.Ball in self.robot.vision.detections:
                ball_pos = 30 * (2 * self.robot.vision.detections[Feature.Ball][0] / self.robot.vision.width - 1)
                angle = int(ball_pos)
                self.log(str(angle))
                self.robot.motors.right.setSpeed(60 - angle)
                self.robot.motors.left.setSpeed(60 + angle)
            else:
                # Move forward short distance
                self.log("Charging...")
                start_time = time.time()
                while time.time() - start_time < 0.1:
                    self.robot.motors.left.setSpeed(40)
                    self.robot.motors.right.setSpeed(40)
                return ScanState(self.robot)
        return ScanState(self.robot)

class FollowWallState(State):
    def next_state(self):
        # PID on wall's visual position
        self.robot.vision.features = Feature.Wall
        while self.robot.time.elapsed() < 180:
            if True in self.robot.bumpers.bumped:
                return ReverseState(self.robot)
            if Feature.Wall in self.robot.vision.detections:
                wall_pos = 30 * (2 * self.robot.vision.detections[Feature.Wall][0] / self.robot.vision.width - 1)
                angle = int(wall_pos)
                self.log(str(angle))
                self.robot.motors.right.setSpeed(60 - angle)
                self.robot.motors.left.setSpeed(60 + angle)
            else:
                # Move back short distance
                self.log("Reversing...")
                start_time = time.time()
                while time.time() - start_time < 2:
                    self.robot.motors.left.setSpeed(-40)
                    self.robot.motors.right.setSpeed(-40)
                return ScanState(self.robot)
        return ScanState(self.robot)




# class ScanState(State):
#     def next_state(self):
#         # Rotate around
#         if "sees ball":
#             return FollowBallState(self.fsm)
#         elif "sees button":
#             return PushButtonState(self.fsm)
#         else:
#             return WanderState(self.fsm)

# class WanderState(State):
#     def next_state(self):
#         # Exploring strategy in first two minutes
#         if self.fsm.time_elapsed() < 120:
#             if "sees ball":
#                 return FollowBallState(self.fsm)
#             elif "sees button":
#                 return PushButtonState(self.fsm)
#             else:
#                 # Wall follow for short time
#                 return ScanState(self.fsm)
#         # Scoring strategy in last one minute
#         else:
#             if "sees tower":
#                 return AlignTowerState(self.fsm)
#             elif "sees yellow wall":
#                 return ApproachWallState(self.fsm)
#             else:
#                 # Go far away
#                 return ScanState(self.fsm)

# class FollowBallState(State):
#     def next_state(self):
#         # PID on ball's visual position
#         # Move forward short distance
#         return ScanState(self.fsm)

# class PushButtonState(State):
#     def next_state(self):
#         # Push button 4 times
#         return ScanState(self.fsm)

# class AlignTowerState(State):
#     def next_state(self):
#         if "aligned":
#             return ShootState(self.fsm)
#         else:
#             # PID on tower's visual (?) position
#             return AlignTowerState(self.fsm)
