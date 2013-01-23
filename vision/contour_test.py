import cv
import cv2
import numpy
from vision import Vision, Color, Feature

def run():
    vis = Vision(True)
    vis.color = Color.Red
    while cv2.waitKey(10) == -1:
        print vis.detectObjects(Feature.Ball)
        # vis.grabFrame()
        # red = vis.extractColor('R')
        # red = vis.morphOpen(red)
        # print vis.pickContour(red)

import cProfile
cProfile.run("run()")
