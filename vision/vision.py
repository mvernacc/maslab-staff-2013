import cv
import cv2
import numpy as np
import time
import threading

class Color:
    Red    = 'R'
    Green  = 'G'
    Yellow = 'Y'
    Cyan   = 'C'
    Purple = 'P'

class Feature:
    Ball   = 0b0001
    Wall   = 0b0010
    Button = 0b0100
    Tower  = 0b1000

class Vision(threading.Thread):
    def __init__(self, debug = False, index = 0):
        # Set up the thread
        threading.Thread.__init__(self)

        # Store the debug flag
        self.debug = debug

        # Set up the video camera
        self.width = 320
        self.height = 240
        self.capture = cv2.VideoCapture(index)
        self.capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, self.height)

        # Set up the default vision properties
        self.color = Color.Red
        self.features = 0
        self.detections = { Feature.Ball : None, Feature.Wall : None, Feature.Button : None, Feature.Tower : None }

        # Load calibration settings
        self.calibration = { }
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

        # Set up debug windows
        if self.debug:
            self.windowOriginal = "Original Image"
            self.windowExtract = "Extracted Color"
            self.windowOpened = "Opened Regions"
            self.windowContour = "Selected Contour"
            cv2.namedWindow(self.windowOriginal)
            cv2.namedWindow(self.windowExtract)
            cv2.namedWindow(self.windowOpened)
            cv2.namedWindow(self.windowContour)
            cv2.moveWindow(self.windowOriginal, 400, 50)
            cv2.moveWindow(self.windowExtract, 800, 50)
            cv2.moveWindow(self.windowOpened, 400, 400)
            cv2.moveWindow(self.windowContour, 800, 400)

        self.image = None
        self.hsv_image = None

    def extractFunction(self, color):
        return {Color.Red : self.filterHSV2}.get(color, self.filterHSV)

    def grabFrame(self):
        retval, self.imageBGR = self.capture.read()
        self.imageHSV = cv2.cvtColor(self.imageBGR, cv.CV_BGR2HSV)
        if self.debug:
            cv2.imshow(self.windowOriginal, self.imageBGR)

    def extractColor(self, color):
        hsv = self.calibration.get(color, ((0, 0), (0, 0), (0, 0)))
        imageExtract = self.extractFunction(color)(hsv[0], hsv[1], hsv[2])
        if self.debug:
            cv2.imshow(self.windowExtract, imageExtract)
        return imageExtract

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
            size = imageIn.shape[1] / 100
        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
        imageOut = cv2.erode(imageIn, element)
        imageOut = cv2.dilate(imageOut, element)
        imageOut = cv2.dilate(imageOut, element)
        if self.debug:
            cv2.imshow(self.windowOpened, imageOut)
        return imageOut

    def contourCentroid(self, imageIn):
        contours, hierarchy = cv2.findContours(imageIn, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        bestContour = None
        bestArea = 0
        result = None
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > bestArea:
                bestContour = contour
                bestArea = area
        if bestContour != None:
            # print bestArea
            moments = cv2.moments(bestContour)
            # if moments["m00"] != 0:
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            if self.debug:
                imageContour = np.zeros(self.imageHSV.shape, np.uint8)
                cv2.drawContours(imageContour, [bestContour], 0, (0, 255, 0), 1)
                cv2.circle(imageContour, (cx, cy), 1, (0, 0, 255), -1)
                cv2.imshow(self.windowContour, imageContour)
            result = (cx, cy, bestArea)
        return result

    def contourMidpoint(self, imageIn):
        contours, hierarchy = cv2.findContours(imageIn, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        bestContour = None
        bestArea = 0
        result = None
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > bestArea:
                bestContour = contour
                bestArea = area
        if bestContour != None:
            # print bestArea
            l = bestContour[bestContour[:,:,0].argmin()][0][0]
            r = bestContour[bestContour[:,:,0].argmax()][0][0]
            t = bestContour[bestContour[:,:,1].argmin()][0][1]
            b = bestContour[bestContour[:,:,1].argmax()][0][1]
            print l, r, t, b
            cx = (l + r) / 2
            cy = (t + b) / 2
            if self.debug:
                imageContour = np.zeros(self.imageHSV.shape, np.uint8)
                cv2.drawContours(imageContour, [bestContour], 0, (0, 255, 0), 1)
                cv2.circle(imageContour, (cx, cy), 1, (0, 0, 255), -1)
                cv2.imshow(self.windowContour, imageContour)
            result = (cx, cy, bestArea)
        return result

    # Helper functions for object detection
    def _detectObjectCentroid(self, color):
        obj = self.extractColor(color)
        obj = self.morphOpen(obj)
        return self.contourCentroid(obj)
    def _detectObjectMidpoint(self, color):
        obj = self.extractColor(color)
        obj = self.morphOpen(obj)
        return self.contourMidpoint(obj)

    def detectObjects(self, features):
        detections = { Feature.Ball : None, Feature.Wall : None, Feature.Button : None, Feature.Tower : None }
        self.grabFrame()
        if (features & Feature.Ball):
            detections[Feature.Ball] = self._detectObjectCentroid(self.color)
        if (features & Feature.Wall):
            detections[Feature.Wall] = self._detectObjectMidpoint(Color.Yellow)
        if (features & Feature.Button):
            detections[Feature.Button] = self._detectObjectCentroid(Color.Cyan)
        if (features & Feature.Tower):
            objects[Feature.Tower] = self._detectObjectMidpoint(Color.Purple)
        return detections

    def run(self):
        self.running = True
        while self.running:
            self.detections = self.detectObjects(self.features)
            time.sleep(0.01)

    def stop(self):
        self.running = False
