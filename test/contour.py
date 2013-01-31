import time, sys, getopt, os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import cProfile
import cv, cv2
from vision.vision import Vision, Color

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'rgycp')
    except getopt.GetoptError:
        print "Arguments: -r -g -y -c -p"
    color = Color.Red
    for opt, arg in opts:
        if opt == '-r':
            color = Color.Red
        if opt == '-g':
            color = Color.Green
        if opt == '-y':
            color = Color.Yellow
        if opt == '-c':
            color = Color.Cyan
        if opt == '-p':
            color = Color.Purple
    try:
        vis = Vision(True)
        while cv2.waitKey(10) == -1:
            vis.grabFrame()
            print vis._detectObjectCentroid(color)
    except:
        pass

if __name__ == "__main__":
    cProfile.run("main(sys.argv[1:])")
