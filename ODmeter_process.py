import cv2
import numpy as np
from PyQt5 import QtGui

def process_image(self, image_data):
    # reshape the image data as 1dimensional array
    image = image_data.as_1d_image()
    # make a gray image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # image = cv2.medianBlur(image,5)
    # find circles in the image
    circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1.2, 100)
    # make a color image again to mark the circles in green
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(image, (x, y), r, (0, 255, 0), 6)

    print(len(image_data.array), len(image_data.array[0]))
    # show the image with Qt
    return QtGui.QImage(image.data,
                        image_data.mem_info.width,
                        image_data.mem_info.height,
                        QtGui.QImage.Format_RGB888)