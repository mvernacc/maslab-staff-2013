import state_machine.sm as sm
import robotBehavior as robot
import threading
import time


class robotSM (sm.SM):
    # main states:  exploring, scoring
        # exploring:  scan, wander, wall follow, go far away,
        #               ball following, button pressing
        # scoring:  search, found, double check

    # state:  main state, substate
    
    def __init__(self, robot)
        self.robot = robotBehavior.Robot()
        self.startState = ('exploring','scan')
        self.buttonCounter = 0
        self.moreBalls = True
        
    # inp = feature:  ball, tower, yellow wall, green square, None
    #   barcode undergoes separate processing
    def getNextValues(self, state, inp):
        newState = (state[0],state[1])
        if state[0] == 'exploring':
            if state[1] == 'button':
                self.robot.pushButton()
                if hit:  # the button is hit
                    self.buttonCounter += 1
                if self.buttonCounter < 4:
                    self.robot.pushButton()
                else:
                    self.moreBalls = False
            else:
                if inp == None:
                    self.robot.explore():
                    newState = ('exploring','wander')
                elif inp == 'ball':
                    self.robot.ballFollow()
                    newState = ('exploring','ball')
                elif inp == 'green square' and self.moreBalls:
                    self.robot.pushButton()
                    newState = ('exploring','button')
                else:
                    pass
            
        elif state[0] == 'exploring':
            if state[1] == 'search':                
                if inp == 'tower' or inp == 'yellow':
                    self.robot.goTo(inp)
                elif inp == None:
                    self.robot.goFarAway()
            elif state[1] == 'found'
                if inp == 'not aligned':
                        self.robot.align()
                    else:
                        self.robot.shoot()
            elif state[1] == 'double check':
                self.robot.doubleCheck()
        return newState, newState

    def done(self):
        self.robot.pause()
                
