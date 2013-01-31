import time, sys, getopt, os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from robot import Robot

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'p:i:d:s:g:t:lr', ['goal=', 'side=', 'duration='])
    except getopt.GetoptError:
        print "Arguments: -p# -i# -d# -s# -t# --duration=#"
    kp = 0
    ki = 0
    kd = 0
    speed = 50
    goal = 30
    side = 'left'
    duration = None
    for opt, arg in opts:
        if opt == '-p':
            kp = float(arg)
        if opt == '-i':
            ki = float(arg)
        if opt == '-d':
            kd = float(arg)
        if opt == '-s':
            speed = int(arg)
        if opt == '-g':
            goal = int(arg)
        if opt == '-l':
            side = 'left'
        if opt == '-r':
            side = 'right'
        if opt == '-t':
            duration = int(arg)
        if opt == '--goal':
            goal = int(arg)
        if opt == '--side':
            if arg.lower() == 'left':
                side = 'left'
            if arg.lower() == 'right':
                side = 'right'
        if opt == '--duration':
            duration = int(arg)
    try:
        robot = Robot()
        robot.start()
        while robot.ready == False: pass
        while robot.ir.nirLeftValue == None or robot.ir.nirRightValue == None: pass
        marker = time.time()
        robot.motors.left.setSpeed(speed)
        robot.motors.right.setSpeed(speed)
        robot.pid.start(kp, ki, kd)
        while duration == None or time.time() - marker < duration:
            error = 0
            if side == 'left':
                error = goal - robot.ir.nirLeftValue
            if side == 'right':
                error = robot.ir.nirRightValue - goal
            robot.pid.setError(int(error))
    except:
        pass
    robot.stop()

if __name__ == "__main__":
    main(sys.argv[1:])
