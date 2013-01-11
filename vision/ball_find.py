# MASLab Team 4
# 8 Jan 2013
# Finding A Red Ball in an Image using OpenCV cv2 package

import cv2
import cv
import numpy as np

# load the image from a file
image = cv2.imread('../reference_images/3.jpg')
# create a new window and show the original image in that file
cv2.namedWindow('BF: Original', cv.CV_WINDOW_NORMAL)
cv2.imshow('BF: Original', image)
# convert the image to HSV, as this colorspace is more robust to changes in lighting
hsv_image = cv2.cvtColor(image, cv.CV_BGR2HSV) 
# Identify the red portions of the image. Since red exists where the H numbers
# HSV loop around from 180 to 0, we do this by finding the not-red pixels,
# then inverting the image
not_red_hsv_min = np.array([10,0,0],np.uint8) # bottom of range of hsv to be rejected
not_red_hsv_max = np.array([170, 255, 255],np.uint8) # top of range of hsv to be rejected
red_image = cv2.inRange(hsv_image, not_red_hsv_min, not_red_hsv_max)
red_image = cv2.bitwise_not(red_image)
# show the red regions
cv2.namedWindow('BF: Red Regions', cv.CV_WINDOW_NORMAL)
cv2.imshow('BF: Red Regions', red_image)
# Reduce Noise with morphological operations
height, width= red_image.shape
morph_size = width/100
element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_size, morph_size))
red_morph_image = cv2.erode(red_image, element)
red_morph_image = cv2.dilate(red_morph_image, element)
red_morph_image = cv2.dilate(red_morph_image, element)
# Show the niose-reduced image
cv2.namedWindow('BF: Red less Noise', cv.CV_WINDOW_NORMAL)
cv2.imshow('BF: Red less Noise', red_morph_image)
# Do Canny
edges = cv2.Canny(red_morph_image, 0, 251)
cv2.namedWindow('Edges', cv.CV_WINDOW_NORMAL)
cv2.imshow("Edges", edges)
# Do Hough Transform 
#circles = cv2.HoughCircles(edges, cv.CV_HOUGH_GRADIENT, 2, width/50 )
circles = cv2.HoughCircles(edges, cv.CV_HOUGH_GRADIENT, 4, width/10, np.array([]), \
254, 150, width/40, width/8)
if circles != None:
	circles = circles[0]
	print circles
	# Draw Hough Transform on original image
	circle_image = np.copy(image)
	for c in circles:
		x,y,r = c
		cv2.circle(circle_image, (x,y), r, (0,255,0), 10)
	cv2.namedWindow('BF: Circles', cv.CV_WINDOW_NORMAL)
	cv2.imshow('BF: Circles', circle_image)  
cv2.waitKey(-1)
