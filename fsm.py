import time
import arduino
from vision.vision2 import Vision
from gnc.pid import PIDController

class State:
    def __init__(self, fsm):
        # Reference the FSM to access properties
        self.fsm = fsm
    def next_state(self):
        raise NotImplementedError

class FiniteStateMachine:
    def __init__(self, color):
        # Store match properties
        self.color = color
        # Store robot properties
        self.arduino = arduino.Arduino()
        self.motor_left = arduino.Motor(self.arduino, 0, 8, 10)
        self.motor_right = arduino.Motor(self.arduino, 0, 7, 9)
        self.bump_left = arduino.DigitalInput(self.arduino, 23)
        self.bump_right = arduino.DigitalInput(self.arduino, 22)
        self.vision = Vision()
        # Start Arduino thread
        self.arduino.run()
    def run(self):
        self.state = ScanState(self)
        self.start_time = time.time()
        while self.time_elapsed() < 180:
            self.state = self.state.next_state()
        self.stop()
    def stop(self):
        # Kill everything
        self.arduino.stop()
    def time_elapsed(self):
        return time.time() - self.start_time

### Temporary strategy used for Mock 1 (and Mock 2?)

class ScanState(State):
    def next_state(self):
        # Rotate around
        self.fsm.motor_left.setSpeed(100)
        self.fsm.motor_right.setSpeed(-100)
        start_time = time.time()
        while time.time() - start_time < 5:
            if len(self.fsm.vision.detect_balls(self.fsm.color)) > 0:
                return FollowBallState(self.fsm)
        return WanderState(self.fsm)

class WanderState(State):
    def next_state(self):
        # Move forward
        self.fsm.motor_left.setSpeed(100)
        self.fsm.motor_right.setSpeed(100)
        start_time = time.time()
        while time.time() - start_time < 5:
            if len(self.fsm.vision.detect_balls(self.fsm.color)) > 0:
                return FollowBallState(self.fsm)
        return ScanState(self.fsm)

class FollowBallState(State):
    def next_state(self):
        # PID on ball's visual position
        ball_pid = PIDController(1, 1, 1)
        self.fsm.vision.grab_frame()
        ball_list = self.fsm.vision.detect_balls(self.fsm.color)
        while len(ball_list) > 0:
            ball_pid.send_value(ball_list[0][0])
            self.fsm.motor_left.setSpeed(100 + ball_pid.adjusted_value)
            self.fsm.motor_right.setSpeed(100 - ball_pid.adjusted_value)
            self.fsm.vision.grab_frame()
            ball_list = self.fsm.vision.detect_balls(self.fsm.color)
        # Move forward short distance
        start_time = time.time()
        while time.time() - start_time < 1:
            self.fsm.motor_left.setSpeed(100)
            self.fsm.motor_right.setSpeed(100)
        return ScanState(self.fsm)

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
