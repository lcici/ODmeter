import cv2
import numpy as np
from PyQt5 import QtGui
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def process_image_view(self, image_data):
    # reshape the image data as 1dimensional array
    image = image_data.as_1d_image()

    process_image_sum(image_data)

    # show the image with Qt
    return QtGui.QImage(image.data,
                        image_data.mem_info.width,
                        image_data.mem_info.height,
                        QtGui.QImage.Format_Grayscale8)

def process_image_sum(image_data):
    image = image_data.as_1d_image()
    image_horizontal = np.sum(image, axis=0)
    image_vertical = np.sum(image, axis=1)

   # plot_data_h = np.arange(image_horizontal.size)
  #  plot_data_h = np.append(plot_data_h, image_horizontal, axis=0)
  #  plot_data_h = np.reshape(plot_data_h, (2, -1))

  #  plot_data_v = np.arange(image_vertical.size)
  #  plot_data_v = np.append(plot_data_h, image_vertical, axis=0)
 #   plot_data_v = np.reshape(plot_data_h, (2, -1))

    return image_horizontal, image_vertical

class Figure_Canvas(FigureCanvas):
    def __init__(self, parent= None):
        fig = Figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        self.axes = fig.add_subplot(111)

    def plot(self, x, y):
        self.axes.plot(x, y)





