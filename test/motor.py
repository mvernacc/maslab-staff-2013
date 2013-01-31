import time, sys, getopt, os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from robot import Robot

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'lrot', ['left=', 'right=', 'roller=', 'tower=', 'duration='])
    except getopt.GetoptError:
        print "Arguments: -l -r -o -t --left=# --right=# --roller=# --tower=# --duration=#"
    try:
        robot = Robot()
        robot.start()
        while robot.ready == False: pass
        marker = time.time()
        speed = 50
        duration = None
        for opt, arg in opts:
            if opt == '-l':
                robot.motors.left.setSpeed(speed)
            if opt == '-r':
                robot.motors.right.setSpeed(speed)
            if opt == '-o':
                robot.motors.roller.setSpeed(speed)
            if opt == '-t':
                robot.motors.tower.setSpeed(speed)
            if opt == '--left':
                robot.motors.left.setSpeed(int(arg))
            if opt == '--right':
                robot.motors.right.setSpeed(int(arg))
            if opt == '--roller':
                robot.motors.roller.setSpeed(int(arg))
            if opt == '--tower':
                robot.motors.tower.setSpeed(int(arg))
            if opt == '--duration':
                duration = int(arg)
        while duration == None or time.time() - marker < duration:
            time.sleep(0.1)
    except:
        pass
    robot.stop()

if __name__ == "__main__":
    main(sys.argv[1:])
