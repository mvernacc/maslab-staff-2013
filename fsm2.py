import time
import arduino
import random
from vision.vision import Vision

class State:
    def __init__(self, fsm, options = None):
        # Reference the FSM to access properties
        self.fsm = fsm
        self.options = options
        self.start_time = time.time()
    def next_state(self):
        raise NotImplementedError
    def state_time(self):
        return time.time() - self.start_time

class FiniteStateMachine:
    def __init__(self, color = "red"):
        # Store match properties
        self.color = color
        # Store robot properties
        self.arduino = arduino.Arduino()
        self.motor_left = arduino.Motor(self.arduino, 0, 9, 8)
        self.motor_right = arduino.Motor(self.arduino, 0, 7, 6)
        self.motor_pickup = arduino.Motor(self.arduino, 0, 12, 11)
        self.bump_left = arduino.DigitalInput(self.arduino, 23)
        self.bump_right = arduino.DigitalInput(self.arduino, 22)
        self.vision = Vision()
        # Start Arduino thread
        self.arduino.run()
        self.bump_left.getValue()
        self.bump_right.getValue()

    def run(self):
        self.state = StartState(self)
        self.start_time = time.time()
        while self.time_elapsed() < 180:
            try:
                print self.state.__class__.__name__
                self.state = self.state.next_state()
            except:
                self.stop()
        self.stop()

    def stop(self):
        # Kill everything
        time.sleep(0.1)
        self.motor_right.setSpeed(0)
        self.motor_left.setSpeed(0)
        self.motor_pickup.setSpeed(0)
        time.sleep(0.1)
        self.arduino.stop()

    def time_elapsed(self):
        return time.time() - self.start_time

    def start_state(self):
        start_code = self.fsm.bump_left.getValue() - self.fsm.bump_right.getValue()
        while start_code == 0:
            start_code = self.fsm.bump_left.getValue() - self.fsm.bump_right.getValue()
            print start_code, self.fsm.bump_left.getValue(), self.fsm.bump_right.getValue()
        if start_code > 0:
            self.fsm.color = "green"
            print "green"
        else:
            self.fsm.color = "red"
            print "red"
        self.fsm.start_time = time.time()
        while self.fsm.elapsed_time() < 1:
            pass
        return ScanState(self.fsm)

    def scan_state(self):
        # Rotate around
        direction = random.choice([-1, 1])
        self.fsm.motor_left.setSpeed(-direction * 50)
        self.fsm.motor_right.setSpeed(direction * 50)
        while self.state_time() < 0.5:
            pass
        while self.state_time() < 5:
            if self.fsm.time_elapsed() < 120:
                if len(self.fsm.vision.detect_balls(self.fsm.color)) > 0:
                    return FollowBallState(self.fsm)
            else:
                return FollowWallState(self.fsm)
        return WanderState(self.fsm)

    def wander_state(self):
        # Move forward
        self.fsm.motor_left.setSpeed(100)
        self.fsm.motor_right.setSpeed(100)
        while self.state_time() < 5:
            if self.fsm.bumper_left.getValue() or self.fsm.bumper_right.getValue():
                return ReverseState(self.fsm)
            if len(self.fsm.vision.detect_balls(self.fsm.color)) > 0:
                return FollowBallState(self.fsm)
        return ScanState(self.fsm)

    def reverse_state(self):
        self.fsm.motor_right.setSpeed(-40)
        self.fsm.motor_left.setSpeed(-40)
        while self.state_time() < 1:
            pass
        return ScanState(self.fsm)

    def follow_ball_state(self):
        # PID on ball's visual position
        while self.fsm.time_elapsed() < 120:
            if self.fsm.bumper_left.getValue() or self.fsm.bumper_right.getValue():
                return ReverseState(self.fsm)
            ball_pos = self.fsm.vision.detect_balls(self.fsm.color)
            if ball_pos != None:
                angle = int(ball_pos.angle)
                self.fsm.motor_right.setSpeed(60 - angle)
                self.fsm.motor_left.setSpeed(60 + angle)
            else:
                # Move forward short distance
                start_time = time.time()
                while time.time() - start_time < 1:
                    self.fsm.motor_left.setSpeed(40)
                    self.fsm.motor_right.setSpeed(40)
                return ScanState(self.fsm)
        return ScanState(self.fsm)

    def follow_wall_state(self):
        # PID on wall's visual position
        while self.fsm.time_elapsed() < 120:
            if self.fsm.bumper_left.getValue() or self.fsm.bumper_right.getValue():
                return ReverseState(self.fsm)
            wall_pos = self.fsm.vision.detect_wall()
            if wall_pos != None:
                angle = int(wall_pos)
                self.fsm.motor_right.setSpeed(60 - angle)
                self.fsm.motor_left.setSpeed(60 + angle)
            else:
                # Move forward short distance
                start_time = time.time()
                while time.time() - start_time < 1:
                    self.fsm.motor_left.setSpeed(40)
                    self.fsm.motor_right.setSpeed(40)
                return ScanState(self.fsm)
        return ScanState(self.fsm)



maslab_fsm = FiniteStateMachine()
maslab_fsm.run()



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
