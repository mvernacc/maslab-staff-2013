# Learning to use OpenCV with python
# Matt Vernacchia
# MASLab team 4

import cv
cv.NamedWindow('a_window', cv.CV_WINDOW_AUTOSIZE)
image = cv.LoadImage('test.jpg', cv.CV_LOAD_IMAGE_COLOR)
cv.ShowImage('a_window', image)
cv.WaitKey(5000)
