import os
import cv
import cv2
from vision import Vision

mouse_hsv = [0, 0, 0]
hue = [0, 180]
sat = [0, 255]
val = [0, 255]

def setHueMin(value):
    hue[0] = value
    return
def setHueMax(value):
    hue[1] = value
    return
def setSatMin(value):
    sat[0] = value
    return
def setSatMax(value):
    sat[1] = value
    return
def setValMin(value):
    val[0] = value
    return
def setValMax(value):
    val[1] = value
    return
def setHSVRange(hue_range, sat_range, val_range):
    cv2.setTrackbarPos(hsvNames[0], toolWindow, hue_range[0])
    cv2.setTrackbarPos(hsvNames[1], toolWindow, hue_range[1])
    cv2.setTrackbarPos(hsvNames[2], toolWindow, sat_range[0])
    cv2.setTrackbarPos(hsvNames[3], toolWindow, sat_range[1])
    cv2.setTrackbarPos(hsvNames[4], toolWindow, val_range[0])
    cv2.setTrackbarPos(hsvNames[5], toolWindow, val_range[1])

def onMouse(event, x, y, a, b):
    h, s, v = hsv_image[y][x]
    mouse_hsv[0] = h
    mouse_hsv[1] = s
    mouse_hsv[2] = v
    if event == cv.CV_EVENT_LBUTTONDOWN:
        setHSVRange((min(h, hue[0]), max(h, hue[1])),
                    (min(s, sat[0]), max(s, sat[1])),
                    (min(v, val[0]), max(v, val[1])))
    if event == cv.CV_EVENT_RBUTTONDOWN:
        setHSVRange((max((h+90)%180-90,(hue[0]+90)%180-90,0), min((h-90)%180+90,(hue[1]-90)%180+90,180)),
                    (min(s, sat[0]), max(s, sat[1])),
                    (min(v, val[0]), max(v, val[1])))
    return

def resetHSV():
    h, s, v = mouse_hsv
    setHSVRange((h, h), (s, s), (v, v))

global mode
mode = 'R'

def loadHSV():
    for s in settings:
        if s[0] == mode:
            values = [int(x) for x in s.split(' ')[1:7]]
            setHSVRange((values[0], values[1]),
                        (values[2], values[3]),
                        (values[4], values[5]))
            return
    resetHSV()

def saveHSV():
    new_setting = "{} {} {} {} {} {} {}\n".format(mode, hue[0], hue[1], sat[0], sat[1], val[0], val[1])
    print new_setting[:-1]
    seen = False
    for i, s in enumerate(settings):
        if s[0] == mode:
            settings[i] = new_setting
            seen = True
            break
    if seen == False:
        settings.append(new_setting)
    
toolWindow = "Image"
normalWindow = "Calibration (Normal Hue)"
inverseWindow = "Calibration (Inverse Hue)"
hsvNames = ("Hue Min", "Hue Max", "Sat Min", "Sat Max", "Val Min", "Val Max")
cv.CV_GUI_NORMAL = 0x00000010
cv2.namedWindow(toolWindow, cv.CV_WINDOW_AUTOSIZE | cv.CV_GUI_NORMAL)
cv2.namedWindow(normalWindow, cv.CV_WINDOW_AUTOSIZE | cv.CV_GUI_NORMAL)
cv2.namedWindow(inverseWindow, cv.CV_WINDOW_AUTOSIZE | cv.CV_GUI_NORMAL)
cv2.moveWindow(toolWindow, 30, 30)
cv2.moveWindow(normalWindow, 400, 30)
cv2.moveWindow(inverseWindow, 400, 320)
cv.CreateTrackbar(hsvNames[0], toolWindow, 0, 180, setHueMin)
cv.CreateTrackbar(hsvNames[1], toolWindow, 0, 180, setHueMax)
cv.CreateTrackbar(hsvNames[2], toolWindow, 0, 255, setSatMin)
cv.CreateTrackbar(hsvNames[3], toolWindow, 0, 255, setSatMax)
cv.CreateTrackbar(hsvNames[4], toolWindow, 0, 255, setValMin)
cv.CreateTrackbar(hsvNames[5], toolWindow, 0, 255, setValMax)
cv.SetMouseCallback(toolWindow, onMouse)

filename = "hsv_calibration"
settings = []
if os.path.isfile(filename):
    f = open(filename, "r")
    settings = f.readlines()
    print "".join(settings)[:-1]
    f.close()
f = open(filename, "w")

loadHSV()

vis = Vision(False)
key = None

while key != 27:
    if key == 65470: # F1 (Load)
        loadHSV()
    if key == 65471: # F2 (Save)
        saveHSV()
    if key == 114: # R
        mode = 'R'
        print "RED"
    if key == 103: # G
        mode = 'G'
        print "GREEN"
    if key == 121: # Y
        mode = 'Y'
        print "YELLOW"
    if key == 112: # P
        mode = 'P'
        print "PURPLE"
    if key == 99: # C
        mode = 'C'
        print "CYAN"
    if key == 98: # B
        mode = 'B'
        print "BLACK"
    if key == 32: # Space
        resetHSV()
    vis.grab_frame()
    cv2.imshow(toolWindow, vis.image)
    hsv_image = cv2.cvtColor(vis.image, cv.CV_BGR2HSV)
    filtered_image = vis.pick_hsv(hsv_image, hue, sat, val)
    inverse_image = vis.pick_hsv_inverse(hsv_image, hue, sat, val)
    cv2.imshow(normalWindow, filtered_image)
    cv2.imshow(inverseWindow, inverse_image)
    key = cv2.waitKey(10)

settings.sort()
settings_string = "".join(settings)
f.write(settings_string)
f.close()
print settings_string[:-1]
