import cv2
import os
import numpy as np
import sys
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from time import sleep


Form = uic.loadUiType(os.path.join(os.getcwd(), "mainwindow.ui"))[0]
# cascade_Path = os.path.join(os.getcwd(), 'fist.xml')
# fistCascade = cv2.CascadeClassifier(cascade_Path)
# video_capture = cv2.VideoCapture(0)


class IntroWindow(QMainWindow, Form):
    def __init__(self):
        Form.__init__(self)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.thread = PlotThread(0)

        self.Start_Pushbutton.clicked.connect(self.start)

        self.fig = Figure(frameon=False)
        self.ax = self.fig.add_subplot(111, frameon=False)
        x = np.linspace(0, 2*np.pi, 1000)
        self.line1, =  self.ax.plot(x, np.cos(x), 'r', markersize=20)
        self.canvas = FigureCanvas(self.fig)
        self.navi = NavigationToolbar(self.canvas, self)

        l = QVBoxLayout(self.matplotlib_widget)
        l.addWidget(self.canvas)
        l.addWidget(self.navi)

    def start(self):
        if self.thread.isRunning():
            return
        num = np.random.random()
        self.thread = PlotThread(num)
        self.thread.update_trigger.connect(self.update_plot)
        self.thread.start()

    def update_plot(self, n, x, y):
        self.line1.set_data(x, y)
        self.fig.canvas.draw()


class PlotThread(QtCore.QThread):
    update_trigger = QtCore.pyqtSignal(int, np.ndarray, np.ndarray)

    def __init__(self, decay):
        QtCore.QThread.__init__(self)
        self.decay = decay

    def run(self):
        x = np.linspace(0, 2*np.pi, 1000)
        for n in range(20):
            self.update_trigger.emit(n, x, np.cos(n*x)*np.exp(-x*self.decay))
            sleep(0.1)



# def show_plot(list_x, list_y, wid, hei):
#     plt.axis([0, wid, 0, hei])
#     plt.plot(list_x, list_y, 'ro',  markersize=20)
#     plt.show()


# position_x = []
# position_y = []
#
# while True:
#     ret, frame = video_capture.read()
#     if ret:
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         fists = fistCascade.detectMultiScale(
#             gray,
#             scaleFactor=1.2,
#             minNeighbors=8,
#             minSize=(40, 40),
#             flags=cv2.CASCADE_SCALE_IMAGE
#         )
#
#         for (x, y, w, h) in fists:
#             cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
#             position_x.append(np.size(frame, 1) - x)
#             position_y.append(np.size(frame, 0) - y)
#
#         frame = frame[:, ::-1]
#         # cv2.imshow('Video', frame)
#
#         app = QApplication(sys.argv)
#         # ############ setStyle("Fusion")
#         app.setStyle("Plastic")
#         window = IntroWindow(position_x, position_y)
#         window.show()
#         sys.exit(app.exec_())
#
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#
# ret, frame = video_capture.read()
#
# video_capture.release()
# cv2.destroyAllWindows()
#
# width = np.size(frame, 1)
# height = np.size(frame, 0)

# show_plot(position_x, position_y, width, height)

app = QApplication(sys.argv)
# ############ setStyle("Fusion")
app.setStyle("Plastic")
window = IntroWindow()
window.show()
sys.exit(app.exec_())




