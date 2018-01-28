#------------------------------------------------------------------------------
#                 ODmeter - gui module
#
# Copyright (c) 2018 by Chang Liu.
# All rights reserved.

#------------------------------------------------------------------------------
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

# from PyQt5.QtWidgets import QGraphicsScene, QApplication
# from PyQt5.QtWidgets import QGraphicsView
# from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QWidget

from pyueye import ueye

#Global constant for GUI
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
IMAGE_WIDTH = 600
IMAGE_HEIGHT = 600
IMAGE_X = 50
IMAGE_Y = 50


def get_qt_format(ueye_color_format):
    return {ueye.IS_CM_SENSOR_RAW8: QtGui.QImage.Format_Mono,
            ueye.IS_CM_MONO8: QtGui.QImage.Format_Mono,
            ueye.IS_CM_RGB8_PACKED: QtGui.QImage.Format_RGB888,
            ueye.IS_CM_BGR8_PACKED: QtGui.QImage.Format_RGB888,
            ueye.IS_CM_RGBA8_PACKED: QtGui.QImage.Format_RGB32,
            ueye.IS_CM_BGRA8_PACKED: QtGui.QImage.Format_RGB32
            }[ueye_color_format]


class PyuEyeQtView(QtWidgets.QWidget):
    update_signal = QtCore.pyqtSignal(QtGui.QImage, name="update_signal")

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.image = None

        self.graphics_view = QtWidgets.QGraphicsView(self)
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.h_layout = QtWidgets.QHBoxLayout()

        self.scene = QtWidgets.QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.v_layout.addWidget(self.graphics_view)

        self.scene.drawBackground = self.draw_background
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.update_signal.connect(self.update_image)

        self.processors = []
        self.resize(640, 512)

        self.v_layout.addLayout(self.h_layout)
        self.setLayout(self.v_layout)

    def on_update_canny_1_slider(self, value):
        pass  # print(value)

    def on_update_canny_2_slider(self, value):
        pass  # print(value)

    def draw_background(self, painter, rect):
        if self.image:
            image = self.image.scaled(rect.width(), rect.height(), QtCore.Qt.KeepAspectRatio)
            painter.drawImage(rect.x(), rect.y(), image)

    def update_image(self, image):
        self.scene.update()

    def user_callback(self, image_data):
        return image_data.as_cv_image()

    def handle(self, image_data):
        self.image = self.user_callback(self, image_data)

        self.update_signal.emit(self.image)

        # unlock the buffer so we can use it again
        image_data.unlock()

    def shutdown(self):
        self.close()

    def add_processor(self, callback):
        self.processors.append(callback)


class PyuEyeQtApp:
    def __init__(self, args=[]):
        self.qt_app = QtWidgets.QApplication(args)

    def exec_(self):
        self.qt_app.exec_()

    def exit_connect(self, method):
        self.qt_app.aboutToQuit.connect(method)