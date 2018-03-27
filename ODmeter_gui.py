#------------------------------------------------------------------------------
#                 ODmeter - gui module
#
# Copyright (c) 2018 by Chang Liu.
# All rights reserved.

#------------------------------------------------------------------------------
from PyQt5 import QtCore
from PyQt5 import QtGui
#from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot

from PyQt5.QtWidgets import QGraphicsScene, QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QImage
#from PyQt5.QtWidgets import QGraphicsView
#from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSlider, QWidget,

from pyueye import ueye
from PyQt5.uic import loadUi

from ODmeter_camera import Camera
from pyueye_example_utils import Rect
from ODmeter_process import process_image_view, process_image_sum

import numpy as np
import pyqtgraph


#import ctypes
#from ctypes.wintypes import HWND, MSG


class ODMeterWindow(QMainWindow):
    update_signal = QtCore.pyqtSignal(QtGui.QImage, name="update_signal")

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        loadUi("MainWindow.ui", self)

        #dock widget (not used)
        #self.dock_camera_setting = loadUi("dock_CameraSetting.ui")
        #self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_camera_setting)

        self.initUI()
        self.initCamera()
        self.init_section_data()

        self.updateAOISetting()
        self.updateTriggerSetting()
        self.updateCameraInfo()
        self.updateCameraTiming()

        self.imageCounter = 0

    def initUI(self):
        self.scene = QGraphicsScene()
        self.camera_graphics_view.setScene(self.scene)
        self.scene.drawBackground = self.draw_background
        self.update_signal.connect(self.update_image)

        self.restartButton.clicked.connect(self.restart_capture)
        self.stopButton.clicked.connect(self.stop_capture)
        self.saveButton.clicked.connect(self.save_image_file)

        self.processors = []
        self.init_section_data()

    def init_section_data(self):
        pyqtgraph.setConfigOption('background', 'w')
        self.x_section_plot.plotItem.showGrid(True, True, 0.7)
        self.y_section_plot.plotItem.showGrid(True, True, 0.7)


    def initCamera(self):
        self.image = None
        #if there is no trigger setting, it's trigger off
        self.triggerMode = 0

        self.cam = Camera()
        self.cam.init()
        self.cam.set_colormode(ueye.IS_CM_MONO8)

    def updateAOISetting(self):
        #set AOI
        self.aoi_rect = Rect()
        self.ratio_subsampling = 1
        self.ratio_binning = 1

        #self.AOIComboBox.currentIndexChanged.connect(self.aoi_setting)
        self.binning_ComboBox.currentIndexChanged.connect(self.binning_setting)
        self.subsampling_ComboBox.currentIndexChanged.connect(self.subsampling_setting)
        self.gain_spinBox.valueChanged.connect(self.update_gain)

    def updateTriggerSetting(self):
        #self.dock_camera_setting.trigger_off_button.clicked.connect(self.trigger_off)
        self.trigger_off_button.clicked.connect(self.trigger_off)
        self.trigger_software_button.clicked.connect(self.trigger_software)
        self.trigger_rising_button.clicked.connect(self.trigger_rising)
        self.trigger_falling_button.clicked.connect(self.trigger_falling)

    def updateCameraInfo(self):
        #print(sensor_info.SensorID, sensor_info.nMaxWidth)
        #print(sensor_info.SensorID, sensor_info.nMaxWidth)
        cam_info = self.cam.get_cam_info()
        self.sensor_info = self.cam.get_sensor_info()

        #update camera info on GUI
        self.SNInfo.setText(cam_info.SerNo.decode("utf-8"))

        #update sensor info on GUI
        self.typeInfo.setText(self.sensor_info.strSensorName.decode("utf-8"))
        self.widthInfo.setText(str(self.sensor_info.nMaxWidth))
        self.heightInfo.setText(str(self.sensor_info.nMaxHeight))

        self.aoi_rect.width = self.sensor_info.nMaxWidth
        self.aoi_rect.height = self.sensor_info.nMaxHeight

        if ord(self.sensor_info.nColorMode) == ueye.IS_COLORMODE_MONOCHROME:
            color_mode = "Monochrome"
        else:
            color_mode = "Color"
        self.colorInfo.setText(color_mode)

        #update pixel rate
        pixel_rate = self.cam.get_pixel_clock_rate()
        self.clockInfo.setText(str(pixel_rate))
        pixel_rate_min, pixel_rate_max = self.cam.get_pixel_clock_range()
        self.clockMaxInfo.setText(str(pixel_rate_max))

        self.frame_rate_update()
        self.update_frame_rate_button.clicked.connect(self.frame_rate_update)


    def updateCameraTiming(self):
        self.CLK_spinBox.valueChanged.connect(self.update_pixel_rate)
        self.exposure_time_spinBox.valueChanged.connect(self.update_exposure_time)


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

    @pyqtSlot()
    def binning_setting(self):
        if self.binning_ComboBox.currentText() == "1 x":
            self.ratio_binning = 1
            mode_H = ueye.IS_BINNING_DISABLE
            mode_V = ueye.IS_BINNING_DISABLE
        elif self.binning_ComboBox.currentText() == "2 x":
            self.ratio_binning = 2
            mode_H = ueye.IS_BINNING_2X_HORIZONTAL
            mode_V = ueye.IS_BINNING_2X_VERTICAL
            print(mode_H, mode_V)
        elif self.binning_ComboBox.currentText() == "4 x":
            self.ratio_binning = 4
            mode_H = ueye.IS_BINNING_4X_HORIZONTAL
            mode_V = ueye.IS_BINNING_4X_VERTICAL
        elif self.binning_ComboBox.currentText() == "8 x":
            self.ratio_binning = 8
            mode_H = ueye.IS_BINNING_8X_HORIZONTAL
            mode_V = ueye.IS_BINNING_8X_VERTICAL

        self.cam.set_binning(mode_H, mode_V)
        print(self.ratio_binning)
        print("start AOI setting")
        self.aoi_setting()

    @pyqtSlot()
    def subsampling_setting(self):
        if self.subsampling_ComboBox.currentText() == "1 x":
            self.ratio_subsampling = 1
            mode_H = ueye.IS_SUBSAMPLING_DISABLE
            mode_V = ueye.IS_SUBSAMPLING_DISABLE
        elif self.subsampling_ComboBox.currentText() == "2 x":
            self.ratio_subsampling = 2
            mode_H = ueye.IS_SUBSAMPLING_2X_HORIZONTAL
            mode_V = ueye.IS_SUBSAMPLING_2X_VERTICAL
            print(mode_H, mode_V)
        elif self.subsampling_ComboBox.currentText() == "4 x":
            self.ratio_subsampling = 4
            mode_H = ueye.IS_SUBSAMPLING_4X_HORIZONTAL
            mode_V = ueye.IS_SUBSAMPLING_4X_VERTICAL
        elif self.subsampling_ComboBox.currentText() == "6 x":
            self.ratio_subsampling = 6
            mode_H = ueye.IS_SUBSAMPLING_8X_HORIZONTAL
            mode_V = ueye.IS_SUBSAMPLING_8X_VERTICAL
        elif self.subsampling_ComboBox.currentText() == "8 x":
            self.ratio_subsampling = 8
            mode_H = ueye.IS_SUBSAMPLING_8X_HORIZONTAL
            mode_V = ueye.IS_SUBSAMPLING_8X_VERTICAL

        self.cam.set_subsampling(mode_H, mode_V)
        print(self.ratio_subsampling)
        self.aoi_setting()


    @pyqtSlot()
    def frame_rate_update(self):
        #update the current frame rate by clicking the "update" button
        framerate = self.cam.get_frame_rate()
        self.frameRateInfo.setText(str("%.2f" % framerate))

        pixel_rate = self.cam.get_pixel_clock_rate()
        self.CLK_current_Info.setText(str(pixel_rate))

        pixel_rate_min, pixel_rate_max = self.cam.get_pixel_clock_range()
        self.clockMaxInfo.setText(str(pixel_rate_max))

        exposure_time = self.cam.get_exposure_time()
        self.exposure_current_Info.setText(str("%.3f" % exposure_time))

    @pyqtSlot()
    def update_pixel_rate(self):
        rate = self.CLK_spinBox.value()
        print(rate)
        self.cam.set_pixel_clock_rate(rate)

    @pyqtSlot()
    def update_exposure_time(self):
        time = self.exposure_time_spinBox.value()
        self.cam.set_exposure_time(time)

    @pyqtSlot()
    def update_gain(self):
        factor = self.gain_spinBox.value()
        self.cam.set_gain(factor)

    @pyqtSlot()
    def restart_capture(self):
        pass

    @pyqtSlot()
    def stop_capture(self):
        pass

    @pyqtSlot()
    def save_image_file(self):
        pass

        #Update the Camera View background
    def draw_background(self, painter, rect):
        if self.image:
            #keep the image as the same window size
            image = self.image.scaled(self.camera_graphics_view.width(), self.camera_graphics_view.height())
            painter.drawImage(rect.x(), rect.y(), image)

    def update_image(self, image):
        self.scene.update()

    def update_data(self, image):
        if image:
            plot_data_h, plot_data_v = process_image_sum(image)

            h_axis = np.arange(self.aoi_rect.width)
            v_axis = np.arange(self.aoi_rect.height)

            self.x_section_plot.plot(h_axis, plot_data_h, clear = True)
            self.y_section_plot.plot(v_axis, plot_data_v, clear = True)

    def user_callback(self, image_data):
        return image_data.as_cv_image()

    def handle(self, image_data):
        if self.triggerMode == 2 or self.triggerMode == 3:
            self.imageCounter = self.imageCounter + 1
        #self.image = self.user_callback(self, image_data)
        self.image = process_image_view(self, image_data)
        self.update_signal.emit(self.image)


        self.update_data(image_data)

        if self.imageCounter == 1:
            self.image_first = self.image
        elif self.imageCounter == 2:
            self.image_second = self.image
        elif self.imageCounter == 3:
            self.image_third = self.image
            self.reset_image_counter()
          #update when all three images are collected
            self.display_buffer_image(self.image_first, 1)
            self.display_buffer_image(self.image_second, 2)
            self.display_buffer_image(self.image_third, 3)


        # unlock the buffer so we can use it again
        image_data.unlock()
        
    def shutdown(self):
        self.close()

    def add_processor(self, callback):
        self.processors.append(callback)

    #reset the image counter
    def reset_image_counter(self):
        self.imageCounter = 0

    def aoi_setting(self):
        #update AOI setting after binning parameter changed
        #update the current infomation after camera init
        self.aoi_rect.x, self.aoi_rect.y = 0, 0
        self.aoi_rect.width = int(round((self.sensor_info.nMaxWidth / self.ratio_binning) / self.ratio_subsampling))
        self.aoi_rect.height = int(round((self.sensor_info.nMaxHeight / self.ratio_binning) / self.ratio_subsampling))

        self.profile_info_label.setText(str(self.aoi_rect.width) + " x " + str(self.aoi_rect.height))
        self.cam.set_aoi(self.aoi_rect.x, self.aoi_rect.y, self.aoi_rect.width, self.aoi_rect.height)

        #update the CLK tuning range
        if self.aoi_rect.height == 1920:
            self.CLK_range_label.setText('(5 to 30)')
            self.CLK_spinBox.setMaximum(30)

        elif self.aoi_rect.height == 960:
            self.CLK_range_label.setText('(5 to 43)')
            self.CLK_spinBox.setMaximum(43)

        elif self.aoi_rect.height == 480:
            self.CLK_range_label.setText('(5 to 43)')
            self.CLK_spinBox.setMaximum(43)

        elif self.aoi_rect.height == 240:
            self.CLK_range_label.setText('(5 to 43)')
            self.CLK_spinBox.setMaximum(43)

    def display_buffer_image(self, image_data, window):
        pixmap = QPixmap.fromImage(image_data)
        #resize the image to fit with the window size
        pixmap_resize = pixmap.scaled(self.image_first_label.width(), self.image_first_label.height())
        if window == 1:
            self.image_first_label.setPixmap(pixmap_resize)

        elif window == 2:
            self.image_second_label.setPixmap(pixmap_resize)

        elif window == 3:
            self.image_third_label.setPixmap(pixmap_resize)




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
