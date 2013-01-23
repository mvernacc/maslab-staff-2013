import cv
import cv2
import numpy as np

class Vision:
    def __init__(self, debug = False):
        self.debug = debug
        self.image = None
        self.hsv_image = None
        self.width = 320
        self.height = 240
        self.capture = cv2.VideoCapture(1)
        self.capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, self.height)

        # Load calibration settings
        self.calibration = dict()
        f = open("hsv_calibration", "r")
        settings = f.readlines()
        print "".join(settings)[:-1]
        for s in settings:
            args = s.split(' ')
            color = args[0]
            values = [int(x) for x in args[1:7]]
            self.calibration[color] = ((values[0], values[1]),
                                       (values[2], values[3]),
                                       (values[4], values[5]))
        f.close()
        self.extractFunction = {'R' : self.filterHSV2}

        # Set up debug windows
        if debug:
            self.win_orig = "Original Image"
            self.win_color = "Colored Regions"
            self.win_open = "Opened Regions"
            cv2.namedWindow(self.win_orig)
            cv2.namedWindow(self.win_color)
            cv2.namedWindow(self.win_open)
            cv2.moveWindow(self.win_orig, 600, 30)
            cv2.moveWindow(self.win_color, 600, 300)
            cv2.moveWindow(self.win_open, 600, 570)

    def grabFrame(self):
        retval, self.imageBGR = self.capture.read()
        self.imageHSV = cv2.cvtColor(self.imageBGR, cv.CV_BGR2HSV)

    def extractColor(self, color):
        hsv = self.calibration.get(color, ((0, 0), (0, 0), (0, 0)))
        return self.extractFunction.get(color, self.filterHSV)(hsv[0], hsv[1], hsv[2])

    def filterHSV(self, hue, sat, val):
        minHSV = np.array([hue[0], sat[0], val[0]], np.uint8)
        maxHSV = np.array([hue[1], sat[1], val[1]], np.uint8)
        return cv2.inRange(self.imageHSV, minHSV, maxHSV)

    def filterHSV2(self, hue, sat, val):
        low = self.filterHSV((0, hue[0]), sat, val)
        high = self.filterHSV((hue[1], 180), sat, val)
        return cv2.bitwise_or(low, high)

    def morphOpen(self, imageIn, size = None):
        if size == None:
            size = self.imageHSV.shape.width / 100
        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
        imageOut = cv2.erode(imageIn, element)
        imageOut = cv2.dilate(imageOut, element)
        imageOut = cv2.dilate(imageOut, element)
        if self.debug:
            cv2.imshow(self.win_open, imageOut)
        return imageOut

    def pickContour(self, imageIn):
        contours, hierarchy = cv2.findContours(imageIn, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        imageContour = np.zeros(self.image.shape, np.uint8)
        bestContour = None
        bestArea = 0
        result = None
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > bestArea:
                bestContour = contour
                bestArea = area
        if bestContour != None:
            moments = cv2.moments(bestContour)
            if moments["m00"] != 0:
                cx = int(moments["m10"] / moments["m00"])
                cy = int(moments["m01"] / moments["m00"])
                cv2.drawContours(imageContour, [bestContour], 0, (0, 255, 0), 1)
                cv2.circle(imageContour, (cx, cy), 5, (0, 0, 255), -1)
                result = (cx, cy, bestArea)
        if self.debug:
            cv2.imshow("Contour", imageContour)
        return result

    def grab_frame(self):
        retval, self.image = self.capture.read()

    def show_image(self):
        cv2.imshow(self.win_orig, self.image)

    def pick_hsv(self, hsv_image, hue, sat, val):
        hsv_min = np.array([hue[0], sat[0], val[0]], np.uint8)
        hsv_max = np.array([hue[1], sat[1], val[1]], np.uint8)
        return cv2.inRange(hsv_image, hsv_min, hsv_max)

    def pick_hsv_inverse(self, hsv_image, hue, sat, val):
        image_l = self.pick_hsv(hsv_image, (0, hue[0]), sat, val)
        image_h = self.pick_hsv(hsv_image, (hue[1], 180), sat, val)
        return cv2.bitwise_or(image_l, image_h)

    def pick_red(self, image):
        hsv_image = cv2.cvtColor(image, cv.CV_BGR2HSV) 
        hue = (5, 178)
        sat = (96, 204)
        val = (74, 255)
        return self.pick_hsv_inverse(hsv_image, hue, sat, val)

    def pick_green(self, image):
        hsv_image = cv2.cvtColor(image, cv.CV_BGR2HSV)
        hue = (55, 69)
        sat = (98, 178)
        val = (41, 222)
        return self.pick_hsv(hsv_image, hue, sat, val)

    def pick_yellow(self, image):
        hsv_image = cv2.cvtColor(image, cv.CV_BGR2HSV)
        hue = (26, 30)
        sat = (178, 244)
        val = (116, 254)
        return self.pick_hsv(hsv_image, hue, sat, val)

    def morph_opening(self, image_in, size):
        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
        image_out = cv2.erode(image_in, element)
        image_out = cv2.dilate(image_out, element)
        image_out = cv2.dilate(image_out, element)
        if self.debug:
            cv2.imshow(self.win_open, image_out)
        return image_out

    def detect_balls(self, color):
        # grab_frame() should be called first
        assert(self.image != None)
	if self.debug: self.show_image()
        # Pick the color
        if color == "red":
            color_image = self.pick_red(self.image)
        elif color == "green":
            color_image = self.pick_green(self.image)
        if self.debug:
            cv2.imshow(self.win_color, color_image)
        # Erode and dilate (opening)
        height, width = color_image.shape
        morph_size = width / 100
        filtered_image = self.morph_opening(color_image, morph_size)
 
        M = cv2.moments(filtered_image)
        if M['m00'] < 30000: return None
        cx = int(M['m10']/M['m00'])
        return -30.0 * (1.0 - 2.0 * cx / width)

    def detect_wall(self):
        assert(self.image != None)
	if self.debug: self.show_image()
        # Pick the color
        color_image = self.pick_yellow(self.image)
        if self.debug:
            cv2.imshow(self.win_color, color_image)
        # Erode and dilate (opening)
        height, width = color_image.shape
        morph_size = width / 100
        filtered_image = self.morph_opening(color_image, morph_size)

        M = cv2.moments(filtered_image)
        if M['m00'] < 50000: return None
        cx = int(M['m10']/M['m00'])
        return -30.0 * (1.0 - 2.0 * cx / width)

    def detect_contours(self, color):
        # grab_frame() should be called first
        assert(self.image != None)
	if self.debug: self.show_image()
        # Pick the color
        if color == "red":
            color_image = self.pick_red(self.image)
        elif color == "green":
            color_image = self.pick_green(self.image)
        if self.debug:
            cv2.imshow(self.win_color, color_image)
        # Erode and dilate (opening)
        height, width = color_image.shape
        morph_size = width / 100
        filtered_image = self.morph_opening(color_image, morph_size)
        
        contours,hierarchy = cv2.findContours(filtered_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        drawing = np.zeros(self.image.shape,np.uint8)
        best_contour = None
        best_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > best_area:
                best_contour = contour
                best_area = area
        if best_contour != None:
            moments = cv2.moments(best_contour)
            if moments['m00']!=0:
                cx = int(moments['m10']/moments['m00'])
                cy = int(moments['m01']/moments['m00'])
                cv2.drawContours(drawing,[best_contour],0,(0,255,0),1)
                cv2.circle(drawing,(cx,cy),1,(0,0,255),-1)
        cv2.imshow("Contour", drawing)

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

    # def detect_balls(self, color):
    #     """Grabs a new image an idenifies features in it"""
    #     self.grab_frame()
    #     # Identify the ball-colored regions
    #     color_image = None
    #     if self.red_side:
    #         color_image = self.pick_red(self.image)
    #     else:
    #         color_image = self.pick_green(self.image)
    #     # Show the ball-colored regions
    #     if self.debug: cv2.imshow(self.win_color, color_image)
    #     # Reduce Noise with morphological operations
    #     height, width= color_image.shape
    #     print width
    #     morph_size = width / 100
    #     element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_size, morph_size))
    #     filtered_image = cv2.erode(color_image, element)
    #     filtered_image = cv2.dilate(filtered_image, element)
    #     filtered_image = cv2.dilate(filtered_image, element)
    #     # Show the noise-reduced image
    #     if self.debug: cv2.imshow(self.win_open, filtered_image)

    #     M = cv2.moments(filtered_image)
    #     if M['m00'] == 0: return []
    #     cx = int(M['m10']/M['m00'])
    #     return [Feature(0, 30.0 * (1.0 - 2.0 * cx / width), Feature.BALL)]

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

