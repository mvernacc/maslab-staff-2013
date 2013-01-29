import time
import arduino
import random
import Robot
import threading
from vision.vision import Vision, Color, Feature

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
    def log(self, message):
        print "  " + message

class FiniteStateMachine:
    def __init__(self, color = "red"):
        # Store match properties
        self.color = color
        self.state = None
        # Store robot properties
        self.arduino = arduino.Arduino()
        self.robot = Robot.Robot(color)
#        self.motor_left = arduino.Motor(self.arduino, 0, 9, 8)
#        self.motor_right = arduino.Motor(self.arduino, 0, 7, 6)
#        self.motor_pickup = arduino.Motor(self.arduino, 0, 12, 11)
#        self.bump_left = arduino.DigitalInput(self.arduino, 23)
#        self.bump_right = arduino.DigitalInput(self.arduino, 22)
#        self.vision = Vision(True)

        # Start Arduino thread
        #self.arduino.run()
        self.robot.run()
        time.sleep(1)
        # a = time.time()
        # while time.time() - a < 5:
        #     print self.bump_left.getValue()
        #     print self.bump_right.getValue()

        #to do:  check tower current if there's a ball in the tower
        #if drive motors stall, go into reverse state (True) 

    def run(self):
        self.state = StartState(self)
        self.start_time = time.time()
        while self.time_elapsed() < 180:
            try:
                print self.state.__class__.__name__
                self.state = self.state.next_state()
            except KeyboardInterrupt:
                self.stop()
        self.stop()

    def stop(self):
        # Kill everything
        time.sleep(0.1)
        self.motor_right.setSpeed(0)
        self.motor_left.setSpeed(0)
        self.motor_pickup.setSpeed(0)
        self.motor_roller.setSpeed(0)
        time.sleep(0.1)
        self.robot.stop()
#        self.arduino.stop()

    def time_elapsed(self):
        return time.time() - self.start_time

### Temporary strategy used for Mock 1 (and Mock 2?)

class StartState(State):
    def next_state(self):
        start_code = self.robot.bumpers.bumped()        
        while start_code == 0:
            start_code = self.robot.bumpers.bumped()
        if start_code > 0:
            # right bumper gets hit
            self.robot.color = "green"
            self.log("green")
        else:
             # left bumper gets hit
            self.robot.color = "red"
            self.log("red")
        self.fsm.start_time = time.time()
        while self.fsm.time_elapsed() < 1:
            pass
        self.robot.motor.motorPickUp.setSpeed(60)
        self.robot.motor.motorTower.setSpeed(30)
        if self.robot.motor.stallPickUp():
            self.robot.motor.motorPickUp.setSpeed(0)
        if self.robot.motor.motorTower.stallTower:
            self.robot.motor.motorTower.setSpeed(0)
        return ScanState(self.fsm)

class ScanState(State):
    def next_state(self):
        # Rotate around
        direction = random.choice([-1, 1])
        self.robot.motorLeft.setSpeed(-direction * 40)
        self.robot.motorRight.setSpeed(direction * 40)
        # while self.state_time() < 0.5:
        #     pass
        while self.state_time() < 4:
            if self.fsm.time_elapsed() < 120:
                self.robot.vision.grabFrame()
                if self.robot.vision.detectObjects(Feature.Ball) != None:
                    return FollowBallState(self.fsm)
            else:
                self.robot.vision.grabFrame()
                if self.robot.vision.detectObjects(Feature.Wall) != None:
                    return FollowWallState(self.fsm)
        return WanderState(self.fsm)

class WanderState(State):
    def next_state(self):
        # Move forward
        self.robot.motorLeft.setSpeed(50)
        self.robot.motorRight.setSpeed(50)
        while self.state_time() < 4:
            if self.robot.bumpers.bumped != (False, False):
                return ReverseState(self.fsm, self.robot.bumpers.bumped)
            self.robot.vision.grabFrame()
            if self.robot.vision.detectObjects(Feature.Ball) != None:
                return FollowBallState(self.fsm)
        return ScanState(self.fsm)

class WallFollowWonderState(State):
    def next_state(self):
        # Use the IR to stay near the wall
        self.robot.motorLeft.setSpeed(50)
        self.robot.motorRight.setSpeed(50)
        while self.state_time() < 4:
            self.robot.nirRightVal
            
class GoFarAwayWonderState(State):
    def next_state(self):
        direction = random.choice([-1, 1])
        self.robot.motorLeft.setSpeed(50 - direction*5)
        self.robot.motorRight.setSpeed(50 + direction*5)
        while self.state_time() < 4:
            if self.robot.bumpers.bumped != (False, False):
                return ReverseState(self.fsm, self.robot.bumpers.bumped)
            if self.robot.vision.detectObjects(Feature.Ball) != None:
                return FollowBallState(self.fsm)
        return ScanState(self.fsm)

class ReverseState(State, bump):
    def next_state(self):
        bumped = bump
        self.robot.motorRight.setSpeed(-40)
        self.robot.motorLeft.setSpeed(-40)
        while self.state_time() < 1:
            pass
        if bumped == (True, False) or bumped == (True, True):
            #left bump sensor hit,turning scheme
            self.robot.motorRight.setSpeed(-40)
            self.robot.motorLeft.setSpeed(40)
            while self.state_time() < 0.5:
                pass
        else if bumped == (False, True):
            #right bump sensor hit
            self.robot.motorRight.setSpeed(-40)
            self.robot.motorLeft.setSpeed(40)
        return ScanState(self.fsm)

class FollowBallState(State):
    def next_state(self):
        # PID on ball's visual position
        while self.fsm.time_elapsed() < 120:
            if self.robot.bumpers.bumped != (False, False):
                return ReverseState(self.fsm, self.robot.bumpers.bumped)
            self.robot.vision.grabFrame()
            ball_pos = self.robot.vision.detectObjects(Feature.Ball)
            if ball_pos != None:
                angle = int(ball_pos)
                self.log(str(angle))
                self.robot.motorRight.setSpeed(60 - angle)
                self.robot.motorLeft.setSpeed(60 + angle)
            else:
                # Move forward short distance
                self.log("Charging...")
                start_time = time.time()
                while time.time() - start_time < 0.1:
                    self.robot.motorLeft.setSpeed(40)
                    self.robot.motorRight.setSpeed(40)
                    # check if the pick up motor is okay
                    if self.robot.motor.stallPickUp():
                        self.robot.motor.motorPickUp.setSpeed(0
                    return ScanState(self.fsm)
                return ScanState(self.fsm)
        return ScanState(self.fsm)

class FollowWallState(State):
    def next_state(self):
        # PID on wall's visual position
        while self.fsm.time_elapsed() < 180:
            if self.robot.bumpers.bumped != (False, False):
                return ReverseState(self.fsm, self.robot.bumpers.bumped)
            self.robot.vision.grabFrame()
            wall_pos = self.fsm.vision.detect_wall()
            if wall_pos != None:
                angle = int(wall_pos)
                self.log(str(angle))
                self.robot.motorRight.setSpeed(60 - angle)
                self.robot.motorLeft.setSpeed(60 + angle)
            else:
                # Move back short distance
                self.log("Reversing...")
                start_time = time.time()
                while time.time() - start_time < 2:
                    self.robot.motorLeft.setSpeed(-40)
                    self.robot.motorRight.setSpeed(-40)
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
