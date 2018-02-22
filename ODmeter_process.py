import cv2
import numpy as np
from PyQt5 import QtGui

def process_image(self, image_data):
    pass
    # reshape the image data as 1dimensional array
    image = image_data.as_1d_image()
    #print(image_data.mem_info.width)


    #print(len(image_data.array), len(image_data.array[0]))
    # show the image with Qt
    return QtGui.QImage(image.data,
                        image_data.mem_info.width,
                        image_data.mem_info.height,
                        QtGui.QImage.Format_Grayscale8)