# Learning to use OpenCV with python
# Matt Vernacchia
# MASLab team 4

import cv
cv.NamedWindow('a_window', cv.CV_WINDOW_AUTOSIZE)
capture = cv.CaptureFromCAM(1)
image = cv.QueryFrame(capture)
cv.ShowImage('a_window', image)
cv.WaitKey(5000)
