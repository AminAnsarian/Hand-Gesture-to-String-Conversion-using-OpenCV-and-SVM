
import os
import sys
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from calc import calc_sum
from time import perf_counter
from calCython import calc_sum_cython


Form = uic.loadUiType(os.path.join(os.getcwd(), "mainwindow.ui"))[0]



class IntroWindow(QMainWindow, Form):
    def __init__(self):
        Form.__init__(self)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.start_pushButton.clicked.connect(self.start)
        self.thread2 = CalcThread(1, 1)

    def start(self):
        x = self.maxN_lineEdit.text()
        if self.python_radioButton.isChecked():
            self.thread2 = CalcThread(1, int(x), 1)
        elif self.cython_radioButton.isChecked():
            self.thread2 = CalcThread(1, int(x), 2)

        self.thread2.update_trigger.connect(self.update_label)
        self.thread2.time_trigger.connect(self.update_slider)
        self.thread2.start()


    def update_label(self, x, program):
        if program == 1:
            self.pythonTime_label.setText(str(x))
        elif program == 2:
            self.cythonTime_label.setText(str(x))

    def update_slider(self, time, program):
        if program == 1:
            self.horizontalSlider.setMaximum(time)
            self.horizontalSlider.setValue(time)
        elif program == 2:
            self.horizontalSlider.setValue(time)

class CalcThread(QtCore.QThread):
    update_trigger = QtCore.pyqtSignal(float, int)
    time_trigger = QtCore.pyqtSignal(float, int)

    def __init__(self, first, last, program=0):
        QtCore.QThread.__init__(self)
        self.first = first
        self.last = last
        self.program = program

    def run(self):
        proTime = 0
        temp = int(self.last/10000)
        for i in range(temp):
            t = perf_counter()
            if self.program == 1:
                output = calc_sum(self.first, 10000 * (i + 1))
            elif self.program == 2:
                output = calc_sum_cython(self.first, 10000 * (i + 1))
            proTime += (perf_counter() - t) * 1000
            self.update_trigger.emit(output, self.program)
        self.time_trigger.emit(proTime, self.program)
        app.processEvents()


app = QApplication(sys.argv)
app.setStyle("Plastique")
window = IntroWindow()
window.show()
sys.exit(app.exec_())

