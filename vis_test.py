from vision.vision import Vision
import cv
import cv2
import time
vis = Vision(False, True)
#vis.grab_frame()
#vis.show_img()
for i in range(200):
    vis.get_feat()
    cv2.waitKey(10)
