#------------------------------------------------------------------------------
#                 ODmeter - main module
#
# Copyright (c) 2018 by Chang Liu.
# All rights reserved.

#------------------------------------------------------------------------------
import sys

#from ODmeter_camera import Camera
from pyueye_example_utils import FrameThread
from ODmeter_gui import ODMeterApp, ODMeterWindow
from PyQt5 import QtGui

from pyueye import ueye
from ODmeter_process import process_image

import cv2
import numpy as np



def main():

    # we need a QApplication, that runs our QT Gui Framework
    app = ODMeterApp()

    # init camera in the GUI window
    view = ODMeterWindow()
    view.show()
    view.user_callback = process_image


    view.cam.set_aoi(0, 0, 640, 480)
    view.cam.alloc()
    view.cam.capture_video()

    framerate = ueye.c_double()
    ueye.is_GetFramesPerSecond(view.cam.h_cam, framerate)
    print(framerate)


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
