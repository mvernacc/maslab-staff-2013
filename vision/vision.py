# MASLab Team 4
# 8 Jan 2013
# Finding A Red Ball in an Image using OpenCV cv2 package

import cv2
import cv
import numpy as np
import sys
from command.feature import Feature

class Vision:
    def __init__(self, debug):
        self.capture = cv2.VideoCapture(1)
        self.image = None # the latest image
        self.debug = debug # a boolean - true=debug mode, draws images
        if debug:
                self.win_orig = 'Original Image'
                self.win_red = 'Red Regions'
                self.win_red_noise = 'Red Regions Less Noise'
                self.win_edges = 'Edges'
                cv2.namedWindow(self.win_orig)
                cv2.namedWindow(self.win_red)
                cv2.namedWindow(self.win_red_noise)
                cv2.namedWindow(self.win_edges)
    def grab_frame(self):
        discard, self.image = self.capture.read()
    def show_img(self):
        cv2.imshow(self.win_orig, self.image)
    def pick_red(self, image):
        """Picks Out the Red Portions of an image"""
        # convert the image to HSV, as this colorspace is more robust to changes in lighting
        hsv_image = cv2.cvtColor(image, cv.CV_BGR2HSV) 
        # Identify the red portions of the image. Since red exists where the H numbers
        # HSV loop around from 180 to 0, this is a bit tricky
        hue = (170, 10) # range of hue (red is centered at 0 or 180)
        sat = (100, 255) # range of saturation
        val = (5, 250)  # range of value
        red_hsv_min_1 = np.array([hue[0], sat[0], val[0]], np.uint8)
        red_hsv_max_1 = np.array([180, sat[1], val[1]],np.uint8)
        red_image_1 = cv2.inRange(hsv_image, red_hsv_min_1, red_hsv_max_1)
        red_hsv_min_2 = np.array([0, sat[0], val[0]], np.uint8)
        red_hsv_max_2 = np.array([hue[1], sat[1], val[1]],np.uint8)
        red_image_2 = cv2.inRange(hsv_image, red_hsv_min_2, red_hsv_max_2)
        return cv2.bitwise_or(red_image_1, red_image_2)

    def get_feat(self):
        """Grabs a new image an idenifies features in it"""
        self.grab_frame()
        #Identify the red regions
        red_image = self.pick_red(self.image)
        # show the red regions
        if self.debug: cv2.imshow(self.win_red, red_image)
# Reduce Noise with morphological operations
        height, width= red_image.shape
        morph_size = width/100
        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_size, morph_size))
        red_morph_image = cv2.erode(red_image, element)
        red_morph_image = cv2.dilate(red_morph_image, element)
        red_morph_image = cv2.dilate(red_morph_image, element)
# Show the noise-reduced image
        if self.debug: cv2.imshow(self.win_red_noise, red_morph_image)
# Do Canny
        edges = cv2.Canny(red_morph_image, 0, 251)
        if self.debug: cv2.imshow(self.win_edges, edges)
# Do Hough Transform 
#circles = cv2.HoughCircles(edges, cv.CV_HOUGH_GRADIENT, 2, width/50 )
        circles = cv2.HoughCircles(edges, cv.CV_HOUGH_GRADIENT, 4, width/10,\
                   np.array([]), 254, 75, width/60, width/8)
        
        feats = []
        if circles != None:
            circles = circles[0]
            #print circles
            # Draw Hough Transform on original image
            for c in circles:
                x,y,r = c
                cv2.circle(self.image, (x,y), r, (0,255,0), 10)
                angle = 30.0*(1.0 - 2.0*x/width)
                feats.append( Feature(0, angle, Feature.BALL) )
        if self.debug: cv2.imshow(self.win_orig, self.image)
        return feats
# vis = Vision(True)
# while(True):
#     vis.get_feat()
#     cv2.waitKey(10)

