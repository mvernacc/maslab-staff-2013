from vision.vision import Vision, Feature
import cv
import cv2
import time
vis = Vision(True)
time_start = time.time()
while time.time() - time_start < 10:
    vis.detectObjects(Feature.Ball)
    cv2.waitKey(10)
