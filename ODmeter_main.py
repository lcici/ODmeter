#------------------------------------------------------------------------------
#                 ODmeter - main module
#
# Copyright (c) 2018 by Chang Liu.
# All rights reserved.

#------------------------------------------------------------------------------
import sys

from ODmeter_camera import Camera
from pyueye_example_utils import FrameThread
from ODmeter_gui import ODMeterApp, ODMeterWindow
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

    print(image_data)
    # show the image with Qt
    return QtGui.QImage(image.data,
                        image_data.mem_info.width,
                        image_data.mem_info.height,
                        QtGui.QImage.Format_RGB888)

def main():

    # we need a QApplication, that runs our QT Gui Framework
    app = ODMeterApp()

    # init camera in the GUI window
    view = ODMeterWindow()
    view.show()
    view.user_callback = process_image



    view.cam.set_aoi(0, 0,640, 480)
    view.cam.alloc()
    view.cam.capture_video()


    # a thread that waits for new images and processes all connected views
    thread = FrameThread(view.cam, view)
    thread.start()


    # cleanup
    app.exit_connect(thread.stop)
    sys.exit(app.exec_())

    thread.stop()
    thread.join()

    view.cam.stop_video()
    view.cam.exit()

if __name__ == "__main__":
    main()
