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

def onMouse(event, x, y, a, b):
    if event == cv.CV_EVENT_LBUTTONDOWN:
        h, s, v = hsv_image[y][x]
        mouse_hsv[0] = h
        mouse_hsv[1] = s
        mouse_hsv[2] = v
        cv2.setTrackbarPos("Hue Min", toolWindow, min(h, hue[0]))
        cv2.setTrackbarPos("Sat Min", toolWindow, min(s, sat[0]))
        cv2.setTrackbarPos("Val Min", toolWindow, min(v, val[0]))
        cv2.setTrackbarPos("Hue Max", toolWindow, max(h, hue[1]))
        cv2.setTrackbarPos("Sat Max", toolWindow, max(s, sat[1]))
        cv2.setTrackbarPos("Val Max", toolWindow, max(v, val[1]))
    if event == cv.CV_EVENT_RBUTTONDOWN:
        h, s, v = hsv_image[y][x]
        mouse_hsv[0] = h
        mouse_hsv[1] = s
        mouse_hsv[2] = v
        cv2.setTrackbarPos("Hue Min", toolWindow, max(h, hue[0]))
        cv2.setTrackbarPos("Sat Min", toolWindow, min(s, sat[0]))
        cv2.setTrackbarPos("Val Min", toolWindow, min(v, val[0]))
        cv2.setTrackbarPos("Hue Max", toolWindow, min(h, hue[1]))
        cv2.setTrackbarPos("Sat Max", toolWindow, max(s, sat[1]))
        cv2.setTrackbarPos("Val Max", toolWindow, max(v, val[1]))
    return

toolWindow = "Settings"
normalWindow = "Calibration (Normal Hue)"
inverseWindow = "Calibration (Inverse Hue)"
cv2.namedWindow(toolWindow)
cv2.namedWindow(normalWindow)
cv2.namedWindow(inverseWindow)
cv2.moveWindow(toolWindow, 30, 30)
cv2.moveWindow(normalWindow, 400, 30)
cv2.moveWindow(inverseWindow, 400, 320)

cv.CreateTrackbar("Hue Min", toolWindow,  10, 180, setHueMin)
cv.CreateTrackbar("Hue Max", toolWindow, 170, 180, setHueMax)
cv.CreateTrackbar("Sat Min", toolWindow, 150, 255, setSatMin)
cv.CreateTrackbar("Sat Max", toolWindow, 255, 255, setSatMax)
cv.CreateTrackbar("Val Min", toolWindow,   5, 255, setValMin)
cv.CreateTrackbar("Val Max", toolWindow, 250, 255, setValMax)

cv.SetMouseCallback(toolWindow, onMouse)

videoCapture = cv2.VideoCapture(1)
videoCapture.set(cv.CV_CAP_PROP_FRAME_WIDTH, 320)
videoCapture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
key = cv2.waitKey(10)
while key != 27:
    if key == 114:
        h, s, v = mouse_hsv
        cv2.setTrackbarPos("Hue Min", toolWindow, h)
        cv2.setTrackbarPos("Sat Min", toolWindow, s)
        cv2.setTrackbarPos("Val Min", toolWindow, v)
        cv2.setTrackbarPos("Hue Max", toolWindow, h)
        cv2.setTrackbarPos("Sat Max", toolWindow, s)
        cv2.setTrackbarPos("Val Max", toolWindow, v)
    retval, image = videoCapture.read()
    cv2.imshow(toolWindow, image)
    hsv_image = cv2.cvtColor(image, cv.CV_BGR2HSV)
    filtered_image = Vision.pick_hsv(hsv_image, hue, sat, val)
    inverse_image = Vision.pick_hsv_inverse(hsv_image, hue, sat, val)
    cv2.imshow(normalWindow, filtered_image)
    cv2.imshow(inverseWindow, inverse_image)
    key = cv2.waitKey(10)
