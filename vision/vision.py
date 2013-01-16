 # MASLab Team 4
# 8 Jan 2013
# Finding A Red Ball in an Image using OpenCV cv2 package

import cv2
import cv
import numpy as np
from command.feature import Feature

class Vision:
    def __init__(self, red_side, debug):
        """Makes a new instance of the Vision class.
           Arguments:
            - red_side - What side of the course the robot is on / what color
                the balls are. true --> look for red balls, false --> look
                for green balls.
            - debug - Whether the program produces debuggin output. true --> pro                gram draws images and prints output, false --> program does not
                draw images or print output (faster)"""
        self.capture = cv2.VideoCapture(1)
        self.capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, 320)
        self.capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
        self.image = None # the latest image
        self.red_side = red_side
        self.debug = debug # a boolean - true=debug mode, draws images
        if debug:
                self.win_orig = 'Original Image'
                self.win_color = 'Ball-Colored Regions'
                self.win_color_filt = 'Filtered Ball-Colored Regions'
                self.win_edges = 'Edges'
                cv2.namedWindow(self.win_orig)
                cv2.namedWindow(self.win_color)
                cv2.namedWindow(self.win_color_filt)
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
        sat = (150, 255) # range of saturation
        val = (5, 250)  # range of value
        red_hsv_min_1 = np.array([hue[0], sat[0], val[0]], np.uint8)
        red_hsv_max_1 = np.array([180, sat[1], val[1]],np.uint8)
        red_image_1 = cv2.inRange(hsv_image, red_hsv_min_1, red_hsv_max_1)
        red_hsv_min_2 = np.array([0, sat[0], val[0]], np.uint8)
        red_hsv_max_2 = np.array([hue[1], sat[1], val[1]],np.uint8)
        red_image_2 = cv2.inRange(hsv_image, red_hsv_min_2, red_hsv_max_2)
        return cv2.bitwise_or(red_image_1, red_image_2)

    def pick_green(self, image):
        """Picks Out the Green Portions of an image"""
        # convert the image to HSV, as this colorspace is more robust to changes in lighting
        hsv_image = cv2.cvtColor(image, cv.CV_BGR2HSV) 
        # Identify the green portions of the image. 
        hue = (45, 75) # range of hue (red is centered at 0 or 180)
        sat = (30, 255) # range of saturation
        val = (3, 250)  # range of value
        green_hsv_min = np.array([hue[0], sat[0], val[0]], np.uint8)
        green_hsv_max = np.array([hue[1], sat[1], val[1]], np.uint8)
        return cv2.inRange(hsv_image, green_hsv_min, green_hsv_max)

    def get_feat(self):
        """Grabs a new image an idenifies features in it"""
        self.grab_frame()
        #Identify the ball-colored regions
        ball_color_image = None
        if self.red_side:
            ball_color_image = self.pick_red(self.image)
        else:
            ball_color_image = self.pick_green(self.image)
        # show the ball-colored regions
        if self.debug: cv2.imshow(self.win_color, ball_color_image)
# Reduce Noise with morphological operations
        height, width= ball_color_image.shape
        print width
        morph_size = width/100
        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_size, morph_size))
        filtered_image = cv2.erode(ball_color_image, element)
        filtered_image = cv2.dilate(filtered_image, element)
        filtered_image = cv2.dilate(filtered_image, element)
# Show the noise-reduced image
        if self.debug: cv2.imshow(self.win_color_filt, filtered_image)

	M = cv2.moments(filtered_image)
	if M['m00'] == 0: return []
	cx = int(M['m10']/M['m00'])
	return [Feature(0, 30.0 * (1.0 - 2.0 * cx / width), Feature.BALL)]

	contours, hierarchy = cv2.findContours(filtered_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
	feats = []
	for contour in contours:
		M = cv2.moments(contour)
		cx = int(M['m10']/M['m00'])
		feats.append(Feature(0, 30.0 * (1.0 - 2.0 * cx / width), Feature.BALL))
	return feats

	cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])

	contours, hierarchy = cv2.findContours(filtered_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
	feats = []
	for contour in contours:
		print contour
		break
	        # angle = 30.0 * (1.0 - 2.0 * contour[0] / width)
        	# feats.append(Feature(0, angle, Feature.BALL) )
	return feats

# Do Canny
        edges = cv2.Canny(filtered_image, 0, 251)
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
        if self.debug: cv2.waitKey(10)
        return feats
# vis = Vision(True)
# while(True):
#     vis.get_feat()
#     cv2.waitKey(10)

