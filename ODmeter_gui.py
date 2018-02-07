#------------------------------------------------------------------------------
#                 ODmeter - gui module
#
# Copyright (c) 2018 by Chang Liu.
# All rights reserved.

#------------------------------------------------------------------------------
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot

from PyQt5.QtWidgets import QGraphicsScene, QApplication
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QWidget, QMainWindow

from pyueye import ueye
from PyQt5.uic import loadUi

from ODmeter_camera import Camera

import ctypes
from ctypes.wintypes import HWND, MSG


class ODMeterWindow(QMainWindow):
    update_signal = QtCore.pyqtSignal(QtGui.QImage, name="update_signal")

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        loadUi("MainWindow.ui", self)
        self.dock_camera_setting = loadUi("dock_CameraSetting.ui")

        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_camera_setting)

        self.initUI()
        self.initCamera()
        self.updateCameraSetting()

        self.imageCounter = 0



    def initUI(self):
        self.scene = QGraphicsScene()
        self.camera_graphics_view.setScene(self.scene)
        self.scene.drawBackground = self.draw_background
        self.update_signal.connect(self.update_image)
        self.processors = []

    def initCamera(self):
        self.image = None
        #if there is no trigger setting, it's trigger off
        self.triggerMode = 0

        self.cam = Camera()
        self.cam.init()
        self.cam.set_colormode(ueye.IS_CM_BGR8_PACKED)

    def updateCameraSetting(self):
        self.dock_camera_setting.trigger_off_button.clicked.connect(self.trigger_off)
        self.dock_camera_setting.trigger_software_button.clicked.connect(self.trigger_software)
        self.dock_camera_setting.trigger_rising_button.clicked.connect(self.trigger_rising)
        self.dock_camera_setting.trigger_falling_button.clicked.connect(self.trigger_falling)



    @pyqtSlot()
    def trigger_off(self):
        self.triggerMode = 0
        self.cam.trigger_on(self.triggerMode)
        self.reset_image_counter()

    @pyqtSlot()
    def trigger_software(self):
        self.triggerMode = 1
        self.cam.trigger_on(self.triggerMode)
        self.reset_image_counter()

    @pyqtSlot()
    def trigger_rising(self):
        self.triggerMode = 2
        self.cam.trigger_on(self.triggerMode)
        self.reset_image_counter()


    @pyqtSlot()
    def trigger_falling(self):
        self.triggerMode = 3
        self.cam.trigger_on(self.triggerMode)
        self.reset_image_counter()


        #Update the Camera View background
    def draw_background(self, painter, rect):
        if self.image:
            #keep the image in the original size
            image = self.image.scaled(self.image.width(), self.image.height(), QtCore.Qt.KeepAspectRatio)
            painter.drawImage(rect.x(), rect.y(), image)

    def update_image(self, image):
        self.scene.update()

    def user_callback(self, image_data):
        print(image_data)
        return image_data.as_cv_image()

    def handle(self, image_data):
        if self.triggerMode == 2 or self.triggerMode == 3:
            self.imageCounter = self.imageCounter + 1
            print(self.imageCounter)



        self.image = self.user_callback(self, image_data)
        self.update_signal.emit(self.image)
        # unlock the buffer so we can use it again
        image_data.unlock()

    def shutdown(self):
        self.close()

    def add_processor(self, callback):
        self.processors.append(callback)

    # find the window to receive the message, not used
    def find_window(self, winName):
        User32 = ctypes.windll.LoadLibrary("User32.dll")

        User32.FindWindowW.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR]
        User32.FindWindowW.restypes = [ctypes.wintypes.HWND]
        wHWND = User32.FindWindowW(None, winName)
        return wHWND

    #reset the image counter
    def reset_image_counter(self):
        self.imageCounter = 0






class ODMeterApp:
    def __init__(self, args=[]):
        self.qt_app = QApplication(args)

    def exec_(self):
        self.qt_app.exec_()

    def exit_connect(self, method):
        self.qt_app.aboutToQuit.connect(method)



def get_qt_format(ueye_color_format):
    return {ueye.IS_CM_SENSOR_RAW8: QtGui.QImage.Format_Mono,
            ueye.IS_CM_MONO8: QtGui.QImage.Format_Mono,
            ueye.IS_CM_RGB8_PACKED: QtGui.QImage.Format_RGB888,
            ueye.IS_CM_BGR8_PACKED: QtGui.QImage.Format_RGB888,
            ueye.IS_CM_RGBA8_PACKED: QtGui.QImage.Format_RGB32,
            ueye.IS_CM_BGRA8_PACKED: QtGui.QImage.Format_RGB32
            }[ueye_color_format]
