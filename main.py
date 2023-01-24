import sys
import threading
import time
from queue import Queue

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QLinearGradient
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
import driver

from math import log10, floor


def round_to_1(x):
  return round(x, -int(floor(log10(abs(x)))))


# ...
# ...
# Importing Libraries

try:
  _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
  def _fromUtf8(s):
      return s

try:
  _encoding = QtGui.QApplication.UnicodeUTF8


  def _translate(context, text, disambig):
      return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
  def _translate(context, text, disambig):
      return QtWidgets.QApplication.translate(context, text, disambig)

strata = driver.DVCUPDriver("COM" + str(2))
strata.set_manual_mode()
global txq


def ser_out(s):
  #        strata = driver.DVCUPDriver("COM" + str(3))
  #        strata.set_manual_mode()
  global txq
  txq = float(s)
  #        strata.set_setpoint_Dinamo(float(self.txq))
  if txq == 0:
      txq = 808
#    print(txq)


class CalibrationStationUI(object):
  def __init__(self):
      self.newSP = None
      self.button = None
      self.ForelinePressureValueLabel = None
      self.InletPressureValueLabel = None
      self.DigivacNamelabel = None
      self.centralwidget = None
      self.InletPressureLabel = None
      self.SPScreen = SetPointInputWindow()
      ser_out(5)

  #        self.calli.setsetpoint(500)

  def show_new_window(self):

      setpoint, ok = QtWidgets.QInputDialog.getInt(self,"input","Setpoint")

      ser_out(setpoint)
      print(txq)

  def setupUI(self, VacDisplay):
      VacDisplay.setObjectName(_fromUtf8("Blended Reading"))
      VacDisplay.resize(600, 400)
      sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(VacDisplay.sizePolicy().hasHeightForWidth())
      VacDisplay.setSizePolicy(sizePolicy)
      VacDisplay.setMouseTracking(False)
      VacDisplay.setStyleSheet(
          _fromUtf8("QMainWindow {background-color: blue;}")
      )
      radius = 15
      self.centralwidget = QtWidgets.QWidget(VacDisplay)
      sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)

      sizePolicy.setHeightForWidth(
          self.centralwidget.sizePolicy().hasHeightForWidth()
      )
      self.centralwidget.setSizePolicy(sizePolicy)
      self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
      # self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
      # self.graphicsView.setGeometry(QtCore.QRect(610, 30, 41, 41))
      # self.graphicsView.setStyleSheet(
      #     _fromUtf8(
      #         "background-color: yellow;"
      #     )
      # )
      # # self.graphicsView.setStyleSheet(
      # #     _fromUtf8(
      # #         "background-color: transparent;\n"
      # #         "background-image: url(:/gradient1/Images/logout.png);\n"
      # #         "background-repeat: no;"
      # #     )
      # # )
      # self.graphicsView.setFrameShape(QtWidgets.QFrame.NoFrame)
      # self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
      self.DigivacNamelabel = QtWidgets.QLabel(self.centralwidget)
      self.DigivacNamelabel.setGeometry(QtCore.QRect(270, 10, 131, 51))
      sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.DigivacNamelabel.sizePolicy().hasHeightForWidth())
      self.DigivacNamelabel.setSizePolicy(sizePolicy)

      font = QtGui.QFont()
      font.setPointSize(21)
      font.setBold(True)
      font.setWeight(75)
      self.DigivacNamelabel.setFont(font)
      self.DigivacNamelabel.setStyleSheet(
          _fromUtf8(
              "image : none;\n" "color: #000;\n" "background-color: transparent;"
          )
      )
      self.DigivacNamelabel.setObjectName(_fromUtf8("label"))


      font2 = QtGui.QFont()
      font2.setPointSize(80)
      font2.setBold(True)
      font2.setWeight(75)
      headerfont = QtGui.QFont()
      headerfont.setPointSize(20)
      headerfont.setBold(True)
      headerfont.setWeight(75)




      self.InletPressureValueLabel = QtWidgets.QLabel(self.centralwidget)
      self.InletPressureValueLabel.setAlignment(Qt.AlignCenter)
      self.InletPressureValueLabel.setGeometry(QtCore.QRect(560, 70, 800, 260))
      self.InletPressureValueLabel.setStyleSheet(
          _fromUtf8("image: none;\n" "color: #00f;\n" "background-color: #fff;")
      )
      self.InletPressureValueLabel.setStyleSheet(
          """
          background:rgb(255, 255, 255);
          border-top-left-radius:{0}px;
          border-bottom-left-radius:{0}px;
          border-top-right-radius:{0}px;
          border-bottom-right-radius:{0}px;
          """.format(radius)
      )
      self.InletPressureValueLabel.setFont(font2)
      self.InletPressureValueLabel.setObjectName(_fromUtf8("label_4"))
      self.CurrentSetpointValueLabel = QtWidgets.QLabel(self.centralwidget)
      self.CurrentSetpointValueLabel.setAlignment(Qt.AlignCenter)
      self.CurrentSetpointValueLabel.setGeometry(QtCore.QRect(139, 570, 801, 261))
      self.CurrentSetpointValueLabel.setStyleSheet(
          _fromUtf8("image: none;\n" "color: #00f;\n" "background-color: #fff;")
      )
      self.CurrentSetpointValueLabel.setStyleSheet(
          """
          background:rgb(255, 255, 255);
          border-top-left-radius:{0}px;
          border-bottom-left-radius:{0}px;
          border-top-right-radius:{0}px;
          border-bottom-right-radius:{0}px;
          """.format(radius)
      )

      self.CurrentSetpointValueLabel.setFont(font2)
      self.CurrentSetpointValueLabel.setObjectName(_fromUtf8("label_5"))

      self.InletPressureLabel = QtWidgets.QLabel(self.centralwidget)
      self.InletPressureLabel.setAlignment(Qt.AlignCenter)
      self.InletPressureLabel.setGeometry(QtCore.QRect(560, 5, 801, 191))
      self.InletPressureLabel.setStyleSheet(
          _fromUtf8("image: none;\n" "color: #00f;\n" "background-color: transparent;")
      )
      self.InletPressureLabel.setFont(headerfont)
      self.InletPressureLabel.setObjectName(_fromUtf8("label_2"))

      self.ForelinePressureValueLabel = QtWidgets.QLabel(self.centralwidget)
      self.ForelinePressureValueLabel.setAlignment(Qt.AlignCenter)
      self.ForelinePressureValueLabel.setGeometry(QtCore.QRect(980, 570, 801, 261))
      self.ForelinePressureValueLabel.setStyleSheet(
          _fromUtf8("image: none;\n" "color: #00f;\n" "background-color: #fff;")
      )
      self.ForelinePressureValueLabel.setStyleSheet(
          """
          background:rgb(255, 255, 255);
          border-top-left-radius:{0}px;
          border-bottom-left-radius:{0}px;
          border-top-right-radius:{0}px;
          border-bottom-right-radius:{0}px;
          """.format(radius)
      )
      self.ForelinePressureValueLabel.setFont(font2)
      self.ForelinePressureValueLabel.setObjectName(_fromUtf8("label_2"))
      self.CurrentSetpointLabel = QtWidgets.QLabel(self.centralwidget)
      self.CurrentSetpointLabel.setAlignment(Qt.AlignCenter)
      self.CurrentSetpointLabel.setGeometry(QtCore.QRect(139, 380, 801, 461))
      self.CurrentSetpointLabel.setStyleSheet(
          _fromUtf8("image: none;\n" "color: #00f;\n" "background-color: transparent;")
      )
      self.CurrentSetpointLabel.setFont(headerfont)
      self.CurrentSetpointLabel.setObjectName(_fromUtf8("label_3"))

      self.ForelineLabel = QtWidgets.QLabel(self.centralwidget)
      self.ForelineLabel.setAlignment(Qt.AlignCenter)
      self.ForelineLabel.setGeometry(QtCore.QRect(980, 380, 801, 461))
      self.ForelineLabel.setStyleSheet(
          _fromUtf8("image: none;\n" "color: #00f;\n" "background-color: transparent;")
      )
      self.ForelineLabel.setFont(headerfont)
      self.ForelineLabel.setObjectName(_fromUtf8("label_6"))

      self.button = QtWidgets.QPushButton(self.centralwidget)
      self.button.setFont(headerfont)
      self.button.setText("Adjust Set Point")
      self.button.clicked.connect(self.show_new_window)
      self.button.setGeometry(QtCore.QRect(710, 900, 500, 70))
      self.button.setStyleSheet(
          _fromUtf8("image: none;\n" "color: #00f;\n" "background-color: #00f;")
      )
      self.button.setStyleSheet(
          """
          background:rgb(255, 255, 255);
          border-top-left-radius:{0}px;
          border-bottom-left-radius:{0}px;
          border-top-right-radius:{0}px;
          border-bottom-right-radius:{0}px;
          """.format(radius)
      )

      VacDisplay.setCentralWidget(self.centralwidget)
      self.retranslateUi(VacDisplay)
      QtCore.QMetaObject.connectSlotsByName(VacDisplay)

  def retranslateUi(self, digivac):
      digivac.setWindowTitle(_translate("Calibration Station", "Digivac", None))
      self.DigivacNamelabel.setText(_translate("Calibration Station", "Digivac", None))
      self.InletPressureLabel.setText(_translate("Calibration Station", "Inlet Pressure \n Torr", None))
      self.CurrentSetpointLabel.setText(_translate("Calibration Station", "Current Set-point", None))
      self.ForelineLabel.setText(_translate("Calibration Station", "Fore-line Pressure", None))


#        if self.SPScreen.isVisible():
#            self.SPScreen.hide()
#        else:
#            self.SPScreen.show()


class SetPointInputWindow(QWidget):
  """
  This "window" is a QWidget. If it has no parent, it
  will appear as a free-floating window as we want.
  """

  def __init__(self, **kwds):
      super().__init__(**kwds)
      self.btn = None
      self.le = None
      self.desiredSP = 0.1
      self.label = QLabel("Enter Desired Setpoint")
      layout = QVBoxLayout()
      layout.addWidget(self.label)
      self.btn = QPushButton("Enter Setpoint")
      layout.addWidget(self.btn)
      self.le = QLineEdit()
      self.btn.clicked.connect(self.setSetpoint)
      layout.addWidget(self.le)
      self.setLayout(layout)

  def buttonClick(self):
      input(CalibrationStationUI.calli.setsetpoint)
      print(self.desiredSP)

  def setSetpoint(self):
      CalibrationStationUI.calli.setsetpoint(float(self.le.text()))


#         self.desiredSP, ok = QInputDialog.getInt(self, "integer input dualog", "enter a number")
#         print(self.desiredSP)
#         if ok:
#             self.le.setText(str(self.desiredSP))
# class Window(QWidget):
#     def __init__(self):
#         super().__init__(parent=None)
#         self.setWindowTitle("Calibration Station")
#         self.initUI()
#
#     #     self._createMenu()
#     #    self._createToolBar()
#     #   self._createStatusBar(3)
#
#     def initUI(self):
#         setpoint_title = QLabel('Enter a Setpoint:', self)
#         vacuum_title = QLabel('Blended Reading', self)
#         sps_edit = QLineEdit(self)
#         #       aeee_edit = QLineEdit(self)
#
#         grid = QHBoxLayout()
#         grid.setSpacing(10)
#         grid.addWidget(setpoint_title)
#         grid.addWidget(sps_edit)
#
#         self.setLayout(grid)
#         self.setGeometry(300, 300, 350, 300)
class VacDisplay3CM(QtWidgets.QMainWindow, CalibrationStationUI):
  def __init__(self, parent=None, currentsetpoint=None):
      super().__init__(parent)

      self.strata_worker = StrataSensor()
      self.setupUI(self)
      self.strata_worker.valueChanged.connect(self.on_value_changed)
#        self.CurrentSetpointValueLabel.setNum(txq)

      self.strata_worker.start()


  @QtCore.pyqtSlot(list)
  def on_value_changed(self, vac_level):
      self.InletPressureValueLabel.setNum(vac_level[0])
      self.ForelinePressureValueLabel.setNum(vac_level[1])
      self.CurrentSetpointValueLabel.setNum(vac_level[2])

#       print(vac_level[2])


class StrataSensor(QtCore.QObject):
  valueChanged = QtCore.pyqtSignal(list)
  newSP = QtCore.pyqtSignal()

  def __init__(self, parent=None):
      super().__init__(parent)

  def start(self):
      threading.Thread(target=self._read, daemon=True).start()

  def _read(self):
      global txq
      while True:
          vac_level = (strata.get_pressure_3CM())
          vac_level4 = float(strata.get_pressure(4))
          new_sp = txq
          if vac_level:
              self.valueChanged.emit([vac_level, vac_level4, new_sp])
              strata.set_setpoint_Dinamo(new_sp)
              print(new_sp)

  def getsetpoint(self):
      #     print(strata.get_pressure(3))
      #     print(strata.set_setpoint_Dinamo(60))
      return float(strata.get_setpoint_Dinamo())

  def setsetpoint(self, desired_setpoint):
      #     print(strata.get_pressure(3))
      # strata = driver.DVCUPDriver("COM" + str(3))
      # strata.set_manual_mode()
      strata.set_setpoint_Dinamo(desired_setpoint)


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)
  window = VacDisplay3CM()

  window.show()

  sys.exit(app.exec_())




