import time
import arduino, PID
import random
import robot
import threading
from vision.vision import Vision, Color, Feature

# max abs(speed) = 126, by the way

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
        print self.robot.time.string() + " - " + message

class FiniteStateMachine:
    def __init__(self, color = Color.Red):
        # Store match properties
        self.color = color
        self.state = None
        self.scoring = False
        
        # Store robot properties
        self.robot = Robot()
        self.map = {}
        
    def start(self):
        self.state = ScanState(self.robot)
        self.robot.start()
        self.robot.time.reset()
        time.sleep(1)
        while self.robot.time.elapsed() < 180:
            try:
                print self.robot.time.string() + " " + self.state.__class__.__name__
                self.state = self.state.next_state()
            except KeyboardInterrupt:
                self.stop()
            if self.robot.time.elapsed() > 120:
                self.scoring = True
        self.stop()

    def stop(self):
        # Kill everything
        self.robot.stop()
        time.sleep(0.1)
        self.ard.stop()

class ScanState(State):
    def next_state(self):
        # Rotate around
        direction = random.choice([-1, 1])
        self.robot.motor.left.setSpeed(-direction * 40)
        self.robot.motor.right.setSpeed(direction * 40)
        
        #if self.robot.time.elasped() > 120:
        #else
        # see something in list to be searched for (tower, wall, button maybe)
        # maybe install a counter to see if we've collected all the balls
            # and then search for the button
        # take most recent barcode seen
        # take that off the list.
        # follow balls if they are seen

        if self.scoring == False:
            self.robot.vision.features = Feature.Ball | Feature.Button
            #if self.robot.time.elasped() % 10 == 0:
            #    self.robot.vision.features = Feature.Ball | Feature.Button | Feature.Tower | Feature.Wall
            while self.state_time() < 4:
                detections = self.robot.vision.detections
                #if detections[Feature.Tower] != None:
                #    if QRcodes != None:
                        #self.map[QRcodes[-1]] = ('tower', #size of tower in camera)
                #        pass
                #if detections[Feature.Wall] != None:
                #    if QRcodes != None:
                        #self.map[QRcodes[-1]] = ('tower', #size of wall in camera??)
                #        pass
                if True in self.robot.bumpers.bumped:
                    self.robot.reverse(self.robot.bumpers.bumped)
                
                if detections[Feature.Ball] != None:
                    return FollowBallState(self.robot)
                elif detections[Feature.Button] != None:
                    return PushButton(self.robot)
                else:
                    pass
            return WanderState(self.robot)
            
        else:
            self.robot.vision.features = Feature.Wall | Feature.Tower
            while self.state_time() < 4:
                detections = self.robot.vision.detections
                if True in self.robot.bumpers.bumped:
                    self.robot.reverse(self.robot.bumpers.bumped)
                if detections[Feature.Tower] != None:
                        return AlignTowerState(self.robot)
                elif detections[Feature.Wall] != None:
                        return YellowFollowWallState(self.robot)
                else:
                    pass
            return FindState(self.robot)

class WanderState(State):
    def next_state(self):
        # Move forward
        if self.robot.repeatedBarcodes == False:
            return WallFollow(self.robot)
        else:
            return GoFarAway(self.robot)
#        self.robot.motor.left.setSpeed(50)
#        self.robot.motor.right.setSpeed(50)
#        self.robot.vision.features = Feature.Ball
#        while self.state_time() < 4:
#            detections = self.robot.vision.detections
#            if True in self.robot.bumpers.bumped:
#                return ReverseState(self.robot, self.robot.bumpers.bumped)
#            if detections[Feature.Ball] != None:
#                return FollowBallState(self.robot)
#        return ScanState(self.robot)
    
    def WallFollow(self):
        # Use the IR to stay near the wall
        # IR distance reads from 5 cm to 50 cm
        speed = 50
        self.robot.motor.left.setSpeed(speed)
        self.robot.motor.right.setSpeed(speed)

        goal = 20   # 10 cm away from the wall

        self.robot.vision.features = Feature.Ball
        self.robot.pid.start(5, 0, 0)
        
        #if abs(goal - self.robot.ir.nirLeftVal) < abs(goal - self.robot.ir.nirRightVal):
        if self.robot.ir.nirLeftVal < self.robot.ir.nirRightVal:
            while self.state_time() < 10:
                error = goal - self.robot.ir.nirLeftVal
                self.robot.pid.setError(error)
                if True in self.robot.bumpers.bumped:
                    self.robot.reverse(self.robot.bumpers.bumped)
                if self.robot.vision.detections[Feature.Ball] != None:
                    self.robot.pid.stop()
                    return FollowBallState(self.robot)
            self.robot.pid.stop()
            return ScanState(self.robot)
        else:
            while self.state_time() < 10:
                error = self.robot.ir.nirRightVal - goal
                self.robot.pid.setError(error)
                if True in self.robot.bumpers.bumped:
                    self.robot.reverse(self.robot.bumpers.bumped)
                if self.robot.vision.detections[Feature.Ball] != None:
                    self.robot.pid.stop()
                    return FollowBallState(self.robot)
            self.robot.pid.stop()        
            return ScanState(self.robot)
            
    def GoFarAway(self):
        direction = random.choice([-1, 1])
        self.robot.motor.left.setSpeed(50 - direction*5)
        self.robot.motor.right.setSpeed(50 + direction*5)
        while self.state_time() < 7:
            if True in self.robot.bumpers.bumped:
                self.robot.reverse(self.robot.bumpers.bumped)
            if self.robot.vision.detections[Feature.Ball] != None:
                return FollowBallState(self.robot)
        self.repeatedBarcodes = False
        return ScanState(self.robot)

class FindState(State):
    # uses QR codes and mapping to determine where to code
    # (if tower or wall is closer)
    # maybe drives there too
    pass

class FollowBallState(State):
    def next_state(self):
        # PID on ball's visual position
        self.robot.vision.features = Feature.Ball
        self.robot.pid.start(0.5, 0.0001, 50)
        while True: # Possibly limit time spent following ball?
            detections = self.robot.vision.detections
            if True in self.robot.bumpers.bumped:
                self.robot.reverse(self.robot.bumpers.bumped)
            if detections[Feature.Ball] != None:
                error = int(126 * (2.0 * self.robot.vision.detections[Feature.Ball][0] / self.robot.vision.width - 1))
                # self.log(str(error))
                self.robot.pid.setError(error)
            else:
                # Move forward short distance
                self.log("Charging...")
                start_time = time.time()
                while time.time() - start_time < 0.1:
                    self.robot.motor.left.setSpeed(40)
                    self.robot.motor.right.setSpeed(40)
                self.robot.pid.stop()
                return ScanState(self.robot)
        # return ScanState(self.robot)

class PushButton(State):
    def next_state(self):
        aligned = 0
        self.robot.motors.left.setSpeed(0)
        self.robot.motors.right.setSpeed(0)
        self.robot.vision.features = Feature.Button
        self.robot.pid.start(0.7, 0, 50)
        while self.robot.time.elapsed() < 120:
            if aligned > 10:
                break
            detections = self.robot.vision.detection
            if True in self.robot.bumpers.bumped:
                self.robot.reverse(self.robot.bumpers.bumped)
            if detections[Feature.Button] != None:
                error = int(126 * (2.0 * detections[Feature.Button][0]/self.robot.vision.width - 1))
                if error != 0:
                    aligned = 0
                    self.robot.pid.setError(error)
                else:
                    aligned += 1
        self.robot.pid.stop()
        # ideally pushes the button 4 times
        counter = 0
        while counter < 4
        self.robot.motors.right.setSpeed(60)
        self.robot.motors.left.setSpeed(60)
        self.robot.time.delay(1)
        self.robot.motors.right.setSpeed(0)
        self.robot.motors.left.setSpeed(0)
        self.robot.motors.right.setSpeed(-60)
        self.roboo.motors.left.setSpeed(-60)
        self.robot.time.delay(1)
        self.robot.motors.right.setSpeed(0)
        self.robot.motors.left.setSpeed(0)
        return ScanState(self.robot)
            

class YellowWallFollowState(State):
    def next_state(self):
        # PID on wall's visual position
        self.robot.vision.features = Feature.Wall
        self.robot.motors.right.setSpeed(60)
        self.robot.motors.left.setSpeed(60)
        self.robot.pid.start(0.7, 0, 50)
        while self.robot.time.elapsed() < 180:
            detections = self.robot.vision.detections
            if True in self.robot.bumpers.bumped:
                self.robot.pid.stop()
                return TowerShoot(self.robot)
            if detections[Feature.Wall] != None:
                error = int(126 * (2.0 * detections[Feature.Wall][0] / self.robot.vision.width - 1))
                self.robot.pid.setError(error)
            else:
                self.robot.pid.stop()
                return ScanState(self.robot)
        self.robot.pid.stop()
        return ScanState(self.robot)

class AlignTower(State):
    def next_state(self):
        aligned = 0
        self.robot.motors.left.setSpeed(60)
        self.robot.motors.right.setSpeed(60)
        self.robot.vision.features = Feature.Button
        self.robot.pid.start(0.7, 0, 50)
        while self.robot.time.elapsed() < 120:
            if aligned > 10:
                break
            detections = self.robot.vision.detection
            if True in self.robot.bumpers.bumped:
                self.robot.reverse(self.robot.bumpers.bumped)
            if detections[Feature.Tower] != None:
                error = int(126 * (2.0 * detections[Feature.Tower][0]/self.robot.vision.width - 1))
                if error != 0:
                    aligned = 0
                    self.robot.pid.setError(error)
                else:
                    aligned += 1
        self.robot.pid.stop()
        # Lower the servo
        self.robot.servoBridge.setAngle(30) # ??? NEED TO CHECK ANGLE
        # Drive forward
        self.robot.motors.left.setSpeed(60)
        self.robot.motors.right.setSpeed(60)
        while self.robot.bridgeBump.getValue() == False and self.state_time() < 10:
            if True in self.robot.bumpers.bumped:
                self.robot.reverse(self.robot.bumpers.bumped)
            time.sleep(0)
        return TowerShoot(self.robot)
        # if self.robot.bumpers.shooter == True:
        #     return TowerShoot(self.robot)
        # elif True in self.robot.bumpers.bumped:
        #     self.robot.reverse(self.robot.bumpers.bumped)
        #     return AlignTower(self.robot)
        # else:
        #     # Back Up
        #     self.robot.reverse(self.robot.bumpers.bumped)
        #     return AlignTower(self.robot)
                
class TowerShoot(State):
    # bridge is already lowered
    self.robot.servoBridge.setAngle(30) # ??? NEED TO CHECK ANGLE
    self.robot.servoGate.setAngle(30) # ??? NEED TO CHECK ANGLE
    # top servo gate is lifted
    self.robot.motors.right.setSpeed(0)
    self.robot.motors.left.setSpeed(0)
    time.sleep(5)
    self.robot.servoBridge.setAngle(0) # ??? NEED TO CHECK ANGLE
    self.robot.servoGate.setAngle(0) # ??? NEED TO CHECK ANGLE
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
