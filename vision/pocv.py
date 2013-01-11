# Learning to use OpenCV with python
# Matt Vernacchia
# MASLab team 4

import cv
cv.NamedWindow('image', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('red', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('mask', cv.CV_WINDOW_NORMAL)
image = cv.LoadImage('test.jpg', cv.CV_LOAD_IMAGE_COLOR)
hsv = cv.CreateImage(cv.GetSize(image), 8, 3)
red = cv.CreateImage(cv.GetSize(hsv), 8, 1)
cv.CvtColor(image, hsv, cv.CV_BGR2HSV)
cv.InRangeS(hsv, (10, 0, 0), (170, 255, 255), red)
cv.Not(red, red)
mask = cv.CreateImage(cv.GetSize(red), 8, 1)
cv.Erode(red, mask, None, 8)
cv.Dilate(mask, mask, None, 10)
cv.ShowImage('image', image)
cv.ShowImage('red', red)
cv.ShowImage('mask', mask)
cv.WaitKey(10000)

