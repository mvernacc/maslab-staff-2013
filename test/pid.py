import time, sys, getopt, os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from robot import Robot
from vision.vision import Color, Feature

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'p:i:d:s:t:rg', ['color=', 'duration='])
    except getopt.GetoptError:
        print "Arguments: -p# -i# -d# -s# -t# -r -g --duration=#"
    kp = 0
    ki = 0
    kd = 0
    speed = 0
    color = Color.Red
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
        if opt == '-t':
            duration = int(arg)
        if opt == '-r':
            color = Color.Red
        if opt == '-g':
            color = Color.Green
        if opt == '--color':
            if arg.lower() == 'red':
                color = Color.Red
            if arg.lower() == 'green':
                color = Color.Green
        if opt == '--duration':
            duration = int(arg)
    try:
        robot = Robot()
        robot.start()
        while robot.ready == False: pass
        marker = time.time()
        robot.vision.color = color
        robot.vision.features = Feature.Ball
        robot.motors.left.setSpeed(speed)
        robot.motors.right.setSpeed(speed)
        robot.pid.start(kp, ki, kd)
        while duration == None or time.time() - marker < duration:
            detections = robot.vision.detections
            if detections[Feature.Ball] != None:
                relPos = 2.0 * detections[Feature.Ball][0] / robot.vision.width - 1
                robot.pid.setError(int(126 * relPos))
    except:
        pass
    robot.stop()

if __name__ == "__main__":
    main(sys.argv[1:])
