import time
import arduino, PID
import random
import robot
import threading
from vision.vision import Vision, Color, Feature

# max abs(speed) = 126, by the way

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
    def __init__(self, color = Color.Red):
        # Store match properties
        self.color = color
        self.state = None
        
        # Store robot properties
        self.robot = Robot()
        self.robot.start()
        time.sleep(1)
        

    def start(self):
        #self.state = StartState(self.robot)
        self.state = scanState(self.robot)
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
#        self.motor_right.setSpeed(0)
#        self.motor_left.setSpeed(0)
#        self.motor_pickup.setSpeed(0)
#        self.motor_roller.setSpeed(0)
#        time.sleep(0.1)
#        self.robot.stop()
#        self.arduino.stop()

#    def time_elapsed(self):
#        return time.time() - self.start_time

### Temporary strategy used for Mock 1 (and Mock 2?)

#class StartState(State):
#    def next_state(self):
#        start_code = self.robot.bumpers.bumped()        
#        while start_code == 0:
#            start_code = self.robot.bumpers.bumped()
#        if start_code > 0:
#            # right bumper gets hit
#            self.robot.color = "green"
#            self.log("green")
#        else:
#             # left bumper gets hit
#            self.robot.color = "red"
#            self.log("red")
#        self.fsm.start_time = time.time()
#        while self.fsm.time_elapsed() < 1:
#            pass
#        self.robot.motor.roller.setSpeed(60)
#        self.robot.motor.tower.setSpeed(30)
        # redundant bc in the robot class?
        #if self.robot.motor.stallRoller:
        #    self.robot.motor.roller.setSpeed(0)
        #if self.robot.motor.stallTower:
        #    self.robot.motor.tower.setSpeed(0)
#        return ScanState(self.fsm)

class ScanState(State):
    def next_state(self):
        # Rotate around
        direction = random.choice([-1, 1])
        self.robot.motor.left.setSpeed(-direction * 40)
        self.robot.motor.right.setSpeed(direction * 40)
        # while self.state_time() < 0.5:
        #     pass
        self.robot.vision.features = Feature.Ball | Feature.Wall
        while self.state_time() < 4:
            detections = self.robot.vision.detections:
            if self.robot.time.elasped() < 120:
                if Feature.Ball in detection:
                    return FollowBallState(self.robot)
                elif Feature.Ball in detection:
                    return PushButton(self.robot)
            else:
                if Feature.Tower in detections:
                    return AlignTowerState(self.robot)
                elif Feature.Wall in detections:
                    return YellowFollowWallState(self.robot)
                else:
                    return ScanState(self.robot)
        return WanderState(self.robot)

class WanderState(State):
    def next_state(self):
        # Move forward
        self.robot.motor.left.setSpeed(50)
        self.robot.motor.right.setSpeed(50)
        self.robot.vision.features = Feature.Ball
        while self.state_time() < 4:
            if True in self.robot.bumpers.bumped:
                return ReverseState(self.robot, self.robot.bumpers.bumped)
            if Feature.Ball in self.robot.vision.detections:
                return FollowBallState(self.robot)
        return ScanState(self.robot)

class WallFollowWonderState(State):
    def next_state(self):
        # Use the IR to stay near the wall
        # IR distance reads from 5 cm to 50 cm
        speed = 50
        self.robot.motor.left.setSpeed(speed)
        self.robot.motor.right.setSpeed(speed)

        goal = 10   # 10 cm away from the wall
        correction = 4

        # pid = PID.PID()
        # pid.start()
        
        if abs(10-self.robot.ir.nirLeftVal) < abs(10-self.robot.ir.nirRightVal):    
            while self.state_time() < 4:
                error = self.robot.ir.nirLeftVal - goal
                # PID.setError(error)
                self.robot.motor.left.setSpeed(speed - correction*error)
                self.robot.motor.right.setSpeed(speed + correction*error)
                self.robot.vision.grabFrame()
                if self.robot.vision.detectObjects(Feature.Ball) != None:
                    return FollowBallState(self.robot)
            # pid.stop()
            return ScanState(self.robot)
        else:
            while self.state_time() < 4:
                # pid.setError(error)
                error = self.robot.ir.nirRightVal - goal
                self.robot.motor.left.setSpeed(speed + correction*error)
                self.robot.motor.right.setSpeed(speed - correction*error)
                self.robot.vision.grabFrame()
                if self.robot.vision.detectObjects(Feature.Ball) != None:
                    return FollowBallState(self.robot)
            # pid.stop()        
            return ScanState(self.robot)

            
class GoFarAwayWonderState(State):
    def next_state(self):
        direction = random.choice([-1, 1])
        self.robot.motor.left.setSpeed(50 - direction*5)
        self.robot.motor.right.setSpeed(50 + direction*5)
        while self.state_time() < 4:
            if True in self.robot.bumpers.bumped:
                return ReverseState(self.fsm, self.robot.bumpers.bumped)
            if Feature.Ball in self.robot.vision.detections:
                return FollowBallState(self.robot)
        return ScanState(self.robot)

class ReverseState(State, bump):
    def next_state(self):
        bumped = bump
        self.robot.motor.right.setSpeed(-40)
        self.robot.motor.left.setSpeed(-40)
        while self.state_time() < 1:
            pass
        if bumped == (True, False) or bumped == (True, True):
            #left bump sensor hit,turning scheme
            self.robot.motor.right.setSpeed(-40)
            self.robot.motor.left.setSpeed(40)
            while self.state_time() < 0.5:
                pass
        else if bumped == (False, True):
            #right bump sensor hit
            self.robot.motor.right.setSpeed(-40)
            self.robot.motor.left.setSpeed(40)
        return ScanState(self.robot)

class FollowBallState(State):
    def next_state(self):
        # PID on ball's visual position
        self.robot.vision.features = Feature.Ball
        while self.fsm.time_elapsed() < 180:
            detections = self.robot.vision.detection
            if True in self.robot.bumpers.bumped:
                return ReverseState(self.fsm, self.robot.bumpers.bumped)
            if Feature.Ball in detections:
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
                    self.robot.motor.left.setSpeed(40)
                    self.robot.motor.right.setSpeed(40)
                    # check if the pick up motor is okay
                    if self.robot.motor.stallPickUp():
                        self.robot.motor.motorPickUp.setSpeed(0)
                    return ScanState(self.robot)
                return ScanState(self.robot)
        return ScanState(self.robot)

class PushButton(State):
    def next_state(self):
        aligned = False:
        self.robot.vision.features = Feature.Button
        while self.robot.time.elapsed() < 120:
            detections = self.robot.vision.detection
            if True in self.robot.bumpers.bumped:
                return ReverseState(self.robot, self.robot.bumpers.bumped)
            if Feature.Button in detections:
                if aligned == False:
                    button_pos = 30 * (2 * self.robot.vision.detections[Feature.Button][0]/self.robot.vision.width - 1)
                    angle = int(button_pos)
                    self.log(str(angle))
                    self.robot.motors.right.setSpeed(60 - angle)
                    self.robot.motors.left.setSpeed(60 + angle)
                    if angle == 0:
                        aligned = True
        if aligned == True:
            # ideally pushes the button 4 times
            counter = 0
            while counter < 4
            self.robot.motors.right.setSpeed(60)
            self.robot.motors.left.setSpeed(60)
            self.robot.time.delay(0.5)
            self.robot.motors.stop()
            self.robot.motors.right.setSpeed(-60)
            self.roboto.motors.left.setSpeed(60)
            self.robot.motors.left.setSpeed(60)
            self.robot.motors.stop()
            time.delay(0.5)
            

class YellowWallFollowState(State):
    def next_state(self):
        # PID on wall's visual position
        self.robot.vision.features = Feature.Wall
        while self.robot.time.elapsed() < 180:
            if True in self.robot.bumpers.bumped:
                return ReverseState(self.robot, self.robot.bumpers.bumped)
            if Feature.Wall in self.robot.vision.detections:
                wall_pos = 30 * (2 * self.robot.vision.detections[Feature.Wall][0] / self.robot.vision.width - 1)
                angle = int(wall_pos)
                self.log(str(angle))
                self.robot.motors.right.setSpeed(60-angle)
                self.robot.motor.left.setSpeed(60 + angle)
            else:
                # Move back short distance
                self.log("Reversing...")
                start_time = time.time()
                while time.time() - start_time < 2:
                    self.robot.motor.left.setSpeed(-40)
                    self.robot.motor.right.setSpeed(-40)
                return ScanState(self.robot)
        return ScanState(self.robot)

class AlignTower(State):
    def next_state(self):
        aligned = False:
        while self.robot.time.elapsed() < 180:  # necessary???
            #PID
            if True in self.robot.bumpers.bumped:
                return ReverseState(self.robot, self.robot.bumpers.bumped)
            if Feature.Towerin self.robot.vision.detections:
                while aligned == False:
                    tower_pos = 30 * (2 * self.robot.vision.detections[Feature.Tower][0] / self.robot.vision.width - 1)
                    angle = int(wall_pos)
                    self.log(str(angle))
                    self.robot.motors.right.setSpeed(60 - angle)
                    self.robot.motors.left.setSpeed(60 + angle)
                    if angle == 0:
                        aligned = True:
        # Lower the servo
        # Drive forward
        if self.robot.bumpers.shooter == True:
            return TowerShoot(self.robot)
        else:
            return AlignTower(self.robot)
                
class TowerShoot(State):
    # bridge is already lowered
    # top servo gate is lifted
    self.robot.motors.right.setSpeed(0)
    self.robot.motors.left.setSpeed(0)
    return ScanState(self.robot)    #slightly modified to be explicitly double checking?


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
