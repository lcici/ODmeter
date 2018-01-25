#------------------------------------------------------------------------------
#                 ODmeter - main module
#
# Copyright (c) 2018 by Chang Liu.
# All rights reserved.

#------------------------------------------------------------------------------

from pyueye_example_camera import Camera
from pyueye_example_utils import FrameThread
from ODmeter_gui import PyuEyeQtApp, PyuEyeQtView
from PyQt5 import QtGui

from pyueye import ueye

import cv2
import numpy as np

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

    # show the image with Qt
    return QtGui.QImage(image.data,
                        image_data.mem_info.width,
                        image_data.mem_info.height,
                        QtGui.QImage.Format_RGB888)

def main():

    # we need a QApplication, that runs our QT Gui Framework
    app = PyuEyeQtApp()

    # a basic qt window
    view = PyuEyeQtView()
    view.show()
    view.user_callback = process_image

    # camera class to simplify uEye API access
    cam = Camera()
    cam.init()
    cam.set_colormode(ueye.IS_CM_BGR8_PACKED)

    #get Image size and position from GUI setting
    width, height, x, y = view.image_size_position()

    cam.set_aoi(x, y, width, height)
    cam.alloc()
    cam.capture_video()
    #cam.freeze_video(500000)


    # a thread that waits for new images and processes all connected views
    thread = FrameThread(cam, view)
    thread.start()

    # cleanup
    app.exit_connect(thread.stop)
    app.exec_()

    thread.stop()
    thread.join()

    cam.stop_video()
    cam.exit()

if __name__ == "__main__":
    main()
