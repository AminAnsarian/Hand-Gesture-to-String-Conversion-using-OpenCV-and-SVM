import TrainAndTest
import cv2
import os
import numpy as np
import sys
from time import sleep
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


Form = uic.loadUiType(os.path.join(os.getcwd(), "mainwindow.ui"))[0]
cascade_Path = os.path.join(os.getcwd(), 'fist.xml')
fistCascade = cv2.CascadeClassifier(cascade_Path)



#this function is used because save_fig and process should not be called more than once
def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper


class ControlWindow(QMainWindow, Form):

    def __init__(self):
        QMainWindow.__init__(self)
        Form.__init__(self)
        self.setupUi(self)
        self.capture = None
        self.thread = PlotThread(0, 0)
        self.fig = Figure(frameon=False)
        self.ax = self.fig.add_subplot(111, frameon=False)
        x = np.linspace(0, 2 * np.pi, 1000)
        self.ax.set_ylim([0, 480])
        self.ax.set_xlim([0, 640])
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.line1, = self.ax.plot(x, np.cos(x), 'r.', markersize=20)
        self.canvas = FigureCanvas(self.fig)
        self.navi = NavigationToolbar(self.canvas, self)
        self.x_position = []
        self.y_position = []
        self.start_capture()
        self.processAction = run_once(TrainAndTest.main)
        self.saveAction = run_once(self.save_fig)

        l = QVBoxLayout(self.matplotlib_widget)
        l.addWidget(self.canvas)
        l.addWidget(self.navi)

    def start_capture(self):
        if not self.capture:
            self.capture = QtCapture(0, self.vid_label, self.x_position, self.y_position)
        self.capture.start()
        if self.thread.isRunning():
            return
        self.thread = PlotThread(self.x_position, self.y_position)
        self.thread.update_trigger.connect(self.update_plot)
        self.thread.start()

    def update_plot(self, x, y, clear, string):
        if clear:
            self.ax.cla() #clear ax
            self.string_label.setText('')
            self.ax.set_ylim([0, 480])
            self.ax.set_xlim([0, 640])
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            z = np.linspace(0, 2 * np.pi, 1000)
            self.line1, = self.ax.plot(z, np.cos(z), 'r.', markersize=20)
            self.fig.canvas.draw()
        elif string: #processing the detection
            self.saveAction()
            if(len(x) > 20):
                outString = self.processAction('output.png')

                if outString:
                    self.string_label.setText(outString)
            else:
                x.clear()
                y.clear()
                return



        else: #regular realtime ploting
            self.line1.set_data(np.array(x)*1.1, np.array(y)*1.1)
            self.fig.canvas.draw()
            self.processAction.has_run = False
            self.saveAction.has_run = False

    def save_fig(self):
        self.fig.savefig('output.png')





class QtCapture(QMainWindow, Form):

    def __init__(self, *args):
        QMainWindow.__init__(self)
        self.fps = 24
        self.cap = cv2.VideoCapture(args[0])
        self.xPos = args[2]
        self.yPos = args[3]
        self.video_frame = args[1]
        lay = QVBoxLayout()
        lay.addWidget(self.video_frame)
        self.timer = QtCore.QTimer()

    def next_frame_slot(self): #image processing section
        ret, frame = self.cap.read()
        if ret:
            cv2.rectangle(frame, (0, 0), (150, 240), (0, 255, 0), 2)
            cv2.rectangle(frame, (0, 480), (150, 240), (255, 0, 0), 2)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fists = fistCascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=8,
                minSize=(40, 40),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            for (x, y, w, h) in fists:
                if len(fists) == 1:
                    frame = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    x += int(w/2)
                    y += int(h/2)
                    frame = cv2.circle(frame, (x, y), 5, (0, 0, 255), 2)
                    self.xPos.append(np.size(frame, 1) - x)
                    self.yPos.append(np.size(frame, 0) - y)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, 'Process', (500, 20), font, 0.8, (0, 0, 0))
        cv2.putText(frame, 'Rectangle', (500, 40), font, 0.8, (0, 0, 0))
        cv2.putText(frame, 'Clear', (500, 260), font, 0.8, (0, 0, 0))
        cv2.putText(frame, 'Rectangle', (500, 280), font, 0.8, (0, 0, 0))
        img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)
        self.video_frame.setScaledContents(True)

    def start(self):
        self.timer.timeout.connect(self.next_frame_slot)
        self.timer.start(1000./self.fps)

    def stop(self):
        self.timer.stop()


class PlotThread(QtCore.QThread):
    update_trigger = QtCore.pyqtSignal(list, list, bool, bool) #fist position and clear and string

    def __init__(self, new_x, new_y):
        QtCore.QThread.__init__(self)
        self.new_x = new_x
        self.new_y = new_y

    def run(self):
        while True:
            if self.new_x and self.new_y:
                if self.new_x[-1] > 490 and self.new_y[-1] < 240: #inside blue rectangle
                    self.new_x.clear()
                    self.new_y.clear()
                    self.emit(1, 0)
                elif self.new_x[-1] > 490 and self.new_y[-1] > 240: #inside green rectangle
                    self.emit(0, 1)
                    #self.new_x.clear()
                    #self.new_y.clear()
                else:
                    self.emit(0, 0)
            else:
                self.emit(0, 0)
            sleep(0.1)

    def emit(self, clear, string):
        self.update_trigger.emit(self.new_x, self.new_y, clear, string)

app = QApplication(sys.argv)
app.setStyle("Plastic")
window = ControlWindow()
window.show()
sys.exit(app.exec_())
