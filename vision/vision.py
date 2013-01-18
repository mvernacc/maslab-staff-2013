import cv
import cv2
import numpy as np

class Vision:
    def __init__(self, debug = False):
        self.debug = debug
        self.image = None
        self.capture = cv2.VideoCapture(1)
        self.capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, 320)
        self.capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 240)

        if debug:
                self.win_orig = "Original Image"
                self.win_color = "Ball-Colored Regions"
                self.win_color_filt = "Filtered Ball-Colored Regions"
                self.win_edges = "Edges"
                cv2.namedWindow(self.win_orig)
                cv2.namedWindow(self.win_color)
                cv2.namedWindow(self.win_color_filt)
                cv2.namedWindow(self.win_edges)

    def grab_frame(self):
        retval, self.image = self.capture.read()

    def show_image(self):
        cv2.imshow(self.win_orig, self.image)

    @staticmethod
    def pick_hsv(hsv_image, hue, sat, val):
        hsv_min = np.array([hue[0], sat[0], val[0]], np.uint8)
        hsv_max = np.array([hue[1], sat[1], val[1]], np.uint8)
        return cv2.inRange(hsv_image, hsv_min, hsv_max)

    @staticmethod
    def pick_hsv_inverse(hsv_image, hue, sat, val):
        image_l = Vision.pick_hsv(hsv_image, (0, hue[0]), sat, val)
        image_h = Vision.pick_hsv(hsv_image, (hue[1], 180), sat, val)
        return cv2.bitwise_or(image_l, image_l)

    def pick_red(self, image):
        hsv_image = cv2.cvtColor(image, cv.CV_BGR2HSV) 
        hue = (170, 10)
        sat = (150, 255)
        val = (5, 250)
        return self.pick_hsv_inverse(hsv_image, hue, sat, val)

    def pick_green(self, image):
        hsv_image = cv2.cvtColor(image, cv.CV_BGR2HSV)
        hue = (45, 75)
        sat = (30, 255)
        val = (3, 250)
        return self.pick_hsv(hsv_image, hue, sat, val)

    def detect_balls(self, color):
        # grab_frame() should be called first
        assert(self.image != None)
        # Pick the color
        if color == "red":
            ball_color_image = self.pick_red(self.image)
        elif color == "green":
            ball_color_image = self.pick_green(self.image)
        if self.debug:
            cv2.imshow(self.win_color, ball_color_image)
        # Erode and dilate
        height, width = ball_color_image.shape
        morph_size = width / 100
        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_size, morph_size))
        filtered_image = cv2.erode(ball_color_image, element)
        filtered_image = cv2.dilate(filtered_image, element)
        filtered_image = cv2.dilate(filtered_image, element)
        if self.debug:
            cv2.imshow(self.win_color_filt, filtered_image)
        # Take the centre of mass
	M = cv2.moments(filtered_image)
	if M['m00'] == 0: return []
	cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
	return [(1 - 2 * cx / width, 1 - 2 * cy / height)]

#     def get_feat(self):
#         """Grabs a new image an idenifies features in it"""
#         self.grab_frame()
#         #Identify the ball-colored regions
#         ball_color_image = None
#         if self.red_side:
#             ball_color_image = self.pick_red(self.image)
#         else:
#             ball_color_image = self.pick_green(self.image)
#         # show the ball-colored regions
#         if self.debug: cv2.imshow(self.win_color, ball_color_image)
# # Reduce Noise with morphological operations
#         height, width= ball_color_image.shape
#         print width
#         morph_size = width/100
#         element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_size, morph_size))
#         filtered_image = cv2.erode(ball_color_image, element)
#         filtered_image = cv2.dilate(filtered_image, element)
#         filtered_image = cv2.dilate(filtered_image, element)
# # Show the noise-reduced image
#         if self.debug: cv2.imshow(self.win_color_filt, filtered_image)

# 	M = cv2.moments(filtered_image)
# 	if M['m00'] == 0: return []
# 	cx = int(M['m10']/M['m00'])
# 	return [Feature(0, 30.0 * (1.0 - 2.0 * cx / width), Feature.BALL)]

# 	contours, hierarchy = cv2.findContours(filtered_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# 	feats = []
# 	for contour in contours:
# 		M = cv2.moments(contour)
# 		cx = int(M['m10']/M['m00'])
# 		feats.append(Feature(0, 30.0 * (1.0 - 2.0 * cx / width), Feature.BALL))
# 	return feats

# 	cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])

# 	contours, hierarchy = cv2.findContours(filtered_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# 	feats = []
# 	for contour in contours:
# 		print contour
# 		break
# 	        # angle = 30.0 * (1.0 - 2.0 * contour[0] / width)
#         	# feats.append(Feature(0, angle, Feature.BALL) )
# 	return feats

# # Do Canny
#         edges = cv2.Canny(filtered_image, 0, 251)
#         if self.debug: cv2.imshow(self.win_edges, edges)

# # Do Hough Transform 
# #circles = cv2.HoughCircles(edges, cv.CV_HOUGH_GRADIENT, 2, width/50 )
#         circles = cv2.HoughCircles(edges, cv.CV_HOUGH_GRADIENT, 4, width/10,\
#                    np.array([]), 254, 75, width/60, width/8)
        
#         feats = []
#         if circles != None:
#             circles = circles[0]
#             #print circles
#             # Draw Hough Transform on original image
#             for c in circles:
#                 x,y,r = c
#                 cv2.circle(self.image, (x,y), r, (0,255,0), 10)
#                 angle = 30.0*(1.0 - 2.0*x/width)
#                 feats.append( Feature(0, angle, Feature.BALL) )
#         if self.debug: cv2.imshow(self.win_orig, self.image)
#         if self.debug: cv2.waitKey(10)
#         return feats
# # vis = Vision(True)
# # while(True):
# #     vis.get_feat()
# #     cv2.waitKey(10)

