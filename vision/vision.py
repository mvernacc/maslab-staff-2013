import os
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

    def __init__(self, debug = False, index = None):
        # Set up the thread
        threading.Thread.__init__(self)

        # Store the debug flag
        self.debug = debug

        # Load calibration settings
        _index, self.calibration = Calibrator().loadSettings()
        if index == None: index = _index

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

        # Set up debug windows
        if self.debug:
            cv.CV_GUI_NORMAL = 0x00000010
            self.windowOriginal = "Original Image"
            self.windowExtract = "Extracted Color"
            self.windowOpened = "Opened Regions"
            self.windowContour = "Selected Contour"
            cv2.namedWindow(self.windowOriginal, cv.CV_WINDOW_AUTOSIZE | cv.CV_GUI_NORMAL)
            cv2.namedWindow(self.windowExtract, cv.CV_WINDOW_AUTOSIZE | cv.CV_GUI_NORMAL)
            cv2.namedWindow(self.windowOpened, cv.CV_WINDOW_AUTOSIZE | cv.CV_GUI_NORMAL)
            cv2.namedWindow(self.windowContour, cv.CV_WINDOW_AUTOSIZE | cv.CV_GUI_NORMAL)
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
            size = int(imageIn.shape[1] * 0.01)
        erodeElement = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
        imageOut = cv2.erode(imageIn, erodeElement)
        # dilateElement = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * size, 2 * size))
        # imageOut = cv2.dilate(imageOut, dilateElement)
        imageOut = cv2.dilate(imageOut, erodeElement)
        imageOut = cv2.dilate(imageOut, erodeElement)
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
            # print l, r, t, b
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

    def getDetections(self):
        return self.detections.copy()

    def run(self):
        self.running = True
        while self.running:
            self.detections = self.detectObjects(self.features)
            time.sleep(0.01)

    def stop(self):
        self.running = False


class Calibrator:
 
    def __init__(self, index = 0):
        self.index = index
        self.mouse_hsv = [0, 0, 0]
        self.hue = [0, 180]
        self.sat = [0, 255]
        self.val = [0, 255]
        self.mode = Color.Red
        self.settings = []
        self.imageWindow = "Image"
        self.calibrationWindow = "Calibration"
        self.hsvNames = ("Hue Min", "Hue Max", "Sat Min", "Sat Max", "Val Min", "Val Max")
        self.filename = "hsv_calibration"

    def loadSettings(self):
        index = 0
        calibration = { }
        if os.path.isfile(self.filename):
            f = open(self.filename, "r")
            self.settings = f.readlines()
            print "".join(self.settings)
            index = int(self.settings.pop())
            for s in self.settings:
                args = s.split(' ')
                color = args[0]
                values = [int(x) for x in args[1:7]]
                calibration[color] = ((values[0], values[1]),
                                           (values[2], values[3]),
                                           (values[4], values[5]))
            f.close()
        return index, calibration

    def saveSettings(self):
        self.settings.sort()
        settings_string = "".join(self.settings) + str(self.index)
        f = open(self.filename, "w")
        f.write(settings_string)
        f.close()
        print settings_string

    def setHueMin(self, value):
        self.hue[0] = value
        return

    def setHueMax(self, value):
        self.hue[1] = value
        return

    def setSatMin(self, value):
        self.sat[0] = value
        return

    def setSatMax(self, value):
        self.sat[1] = value
        return

    def setValMin(self, value):
        self.val[0] = value
        return

    def setValMax(self, value):
        self.val[1] = value
        return

    def setHSVRange(self, hue_range, sat_range, val_range):
        cv2.setTrackbarPos(self.hsvNames[0], self.imageWindow, hue_range[0])
        cv2.setTrackbarPos(self.hsvNames[1], self.imageWindow, hue_range[1])
        cv2.setTrackbarPos(self.hsvNames[2], self.imageWindow, sat_range[0])
        cv2.setTrackbarPos(self.hsvNames[3], self.imageWindow, sat_range[1])
        cv2.setTrackbarPos(self.hsvNames[4], self.imageWindow, val_range[0])
        cv2.setTrackbarPos(self.hsvNames[5], self.imageWindow, val_range[1])

    def onMouse(self, event, x, y, a, b):
        h, s, v = self.hsv_image[y][x]
        self.mouse_hsv[0] = h
        self.mouse_hsv[1] = s
        self.mouse_hsv[2] = v
        if event == cv.CV_EVENT_LBUTTONDOWN:
            if self.mode == Color.Red:
                self.setHSVRange((max((h+90)%180-90,(self.hue[0]+90)%180-90,0), min((h-90)%180+90,(self.hue[1]-90)%180+90,180)),
                                 (min(s, self.sat[0]), max(s, self.sat[1])),
                                 (min(v, self.val[0]), max(v, self.val[1])))
            else:
                self.setHSVRange((min(h, self.hue[0]), max(h, self.hue[1])),
                                 (min(s, self.sat[0]), max(s, self.sat[1])),
                                 (min(v, self.val[0]), max(v, self.val[1])))

    def resetHSV(self):
        h, s, v = self.mouse_hsv
        self.setHSVRange((h, h), (s, s), (v, v))

    def loadHSV(self):
        for s in self.settings:
            if s[0] == self.mode:
                values = [int(x) for x in s.split(' ')[1:7]]
                self.setHSVRange((values[0], values[1]),
                                 (values[2], values[3]),
                                 (values[4], values[5]))
                return
        self.resetHSV()

    def saveHSV(self):
        new_setting = "{} {} {} {} {} {} {}\n".format(self.mode, self.hue[0], self.hue[1], self.sat[0], self.sat[1], self.val[0], self.val[1])
        print new_setting[:-1]
        seen = False
        for i, s in enumerate(self.settings):
            if s[0] == self.mode:
                self.settings[i] = new_setting
                seen = True
                break
        if seen == False:
            self.settings.append(new_setting)

    def run(self):
        cv.CV_GUI_NORMAL = 0x00000010
        cv2.namedWindow(self.imageWindow, cv.CV_WINDOW_AUTOSIZE | cv.CV_GUI_NORMAL)
        cv2.namedWindow(self.calibrationWindow, cv.CV_WINDOW_AUTOSIZE | cv.CV_GUI_NORMAL)
        cv2.moveWindow(self.imageWindow, 30, 30)
        cv2.moveWindow(self.calibrationWindow, 400, 30)
        cv.CreateTrackbar(self.hsvNames[0], self.imageWindow, 0, 180, self.setHueMin)
        cv.CreateTrackbar(self.hsvNames[1], self.imageWindow, 0, 180, self.setHueMax)
        cv.CreateTrackbar(self.hsvNames[2], self.imageWindow, 0, 255, self.setSatMin)
        cv.CreateTrackbar(self.hsvNames[3], self.imageWindow, 0, 255, self.setSatMax)
        cv.CreateTrackbar(self.hsvNames[4], self.imageWindow, 0, 255, self.setValMin)
        cv.CreateTrackbar(self.hsvNames[5], self.imageWindow, 0, 255, self.setValMax)
        cv.SetMouseCallback(self.imageWindow, self.onMouse)

        self.loadSettings()
        
        self.loadHSV()
        
        vis = Vision(False, self.index)
        key = None

        while key != 27:
            if key == 65470: # F1 (Load)
                self.loadHSV()
            if key == 65471: # F2 (Save)
                self.saveHSV()
            if key == 114: # R
                self.mode = Color.Red
                self.loadHSV()
                print "RED"
            if key == 103: # G
                self.mode = Color.Green
                self.loadHSV()
                print "GREEN"
            if key == 121: # Y
                self.mode = Color.Yellow
                self.loadHSV()
                print "YELLOW"
            if key == 112: # P
                self.mode = Color.Purple
                self.loadHSV()
                print "PURPLE"
            if key == 99: # C
                self.mode = Color.Cyan
                self.loadHSV()
                print "CYAN"
            if key == 32: # Space
                self.resetHSV()
            vis.grabFrame()
            cv2.imshow(self.imageWindow, vis.imageBGR)
            self.hsv_image = vis.imageHSV
            if self.mode == Color.Red:
                filtered_image = vis.filterHSV2(self.hue, self.sat, self.val)
            else:
                filtered_image = vis.filterHSV(self.hue, self.sat, self.val)
            cv2.imshow(self.calibrationWindow, filtered_image)
            key = cv2.waitKey(10)

        self.saveSettings()
