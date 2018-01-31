import sys
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog,QApplication, QFileDialog
from PyQt5.uic import loadUi
import cv2


class Life2Coding(QDialog):
    def __init__(self):
        super(Life2Coding,self).__init__()
        loadUi("firstui.ui",self)

        self.image = None
        self.processImage = None
        self.loadButton.clicked.connect(self.loadClicked)
        self.saveButton.clicked.connect(self.saveClicked)
        self.cannyButton.clicked.connect(self.cannyClicked)
        self.hSlider.valueChanged.connect(self.cannyDisplay)

    @pyqtSlot()
    def loadClicked(self):
        fname, filter= QFileDialog().getOpenFileName(self, "Open File", "C:\\Users\Administrator\PycharmProjects\pyueye_example", "Image Files(*.jpg)")
        if fname:
            self.loadImage("picture1.jpg")
        else:
            print("Invalid image")

    @pyqtSlot()
    def saveClicked(self):
        fname, filter = QFileDialog.getSaveFileName(self, "Save File", "C:\\Users\Administrator\PycharmProjects\pyueye_example", "Image Files(*.jpg)")
        if fname:
            cv2.imwrite(fname, self.processImage)
        else:
            print("Error")

    @pyqtSlot()
    def cannyClicked(self):
        gray= cv2.cvtColor(self.processImage, cv2.COLOR_BGR2GRAY) if len(self.image.shape)>=3 else self.image
        self.processImage=cv2.Canny(gray, 100, 200)
        self.displayImage(2)

    @pyqtSlot()
    def cannyDisplay(self):
        gray= cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) if len(self.image.shape)>=3 else self.image
        self.processImage=cv2.Canny(gray, self.hSlider.value(), self.hSlider.value()*3)
        self.displayImage(2)


    def loadImage(self, fname):
        self.image = cv2.imread(fname)
        self.processImage = self.image.copy()
        self.displayImage(1)

    def displayImage(self, window = 1):
        qformat=QImage.Format_Indexed8
        if len(self.processImage.shape) == 3: #rows[0], col[1], channels[2]
            if(self.processImage.shape[2])==4:
                qformat=QImage.Format_RGBA8888
            else:
                qformat=QImage.Format_RGB888
        img=QImage(self.processImage, self.processImage.shape[1], self.processImage.shape[0],
                   self.processImage.strides[0], qformat)
        img = img.rgbSwapped()
        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(img))
            self.imgLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        if window == 2:
            self.processLabel.setPixmap(QPixmap.fromImage(img))
            self.processLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)


app=QApplication(sys.argv)
window = Life2Coding()
window.setWindowTitle("First UI")
window.setGeometry(200,200, 800, 800)
window.show()
sys.exit(app.exec_())


