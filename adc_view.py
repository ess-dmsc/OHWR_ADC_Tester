# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'adc_view.ui'
#
# Created by: PyQt4 UI code generator 4.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(900, 569)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.dataLayout = QtGui.QVBoxLayout()
        self.dataLayout.setObjectName(_fromUtf8("dataLayout"))
        self.ts_layout = QtGui.QHBoxLayout()
        self.ts_layout.setObjectName(_fromUtf8("ts_layout"))
        self.timeStampLabel = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeStampLabel.sizePolicy().hasHeightForWidth())
        self.timeStampLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.timeStampLabel.setFont(font)
        self.timeStampLabel.setObjectName(_fromUtf8("timeStampLabel"))
        self.ts_layout.addWidget(self.timeStampLabel)
        self.timeStamp = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeStamp.sizePolicy().hasHeightForWidth())
        self.timeStamp.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.timeStamp.setFont(font)
        self.timeStamp.setObjectName(_fromUtf8("timeStamp"))
        self.ts_layout.addWidget(self.timeStamp)
        self.dataLayout.addLayout(self.ts_layout)
        self.divider = QtGui.QFrame(self.centralwidget)
        self.divider.setFrameShape(QtGui.QFrame.HLine)
        self.divider.setFrameShadow(QtGui.QFrame.Sunken)
        self.divider.setObjectName(_fromUtf8("divider"))
        self.dataLayout.addWidget(self.divider)
        self.plotFrame = QtGui.QFrame(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotFrame.sizePolicy().hasHeightForWidth())
        self.plotFrame.setSizePolicy(sizePolicy)
        self.plotFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.plotFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.plotFrame.setObjectName(_fromUtf8("plotFrame"))
        self.dataLayout.addWidget(self.plotFrame)
        self.horizontalLayout.addLayout(self.dataLayout)
        self.line = QtGui.QFrame(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(34)
        self.line.setFont(font)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.statsLayout = QtGui.QVBoxLayout()
        self.statsLayout.setObjectName(_fromUtf8("statsLayout"))
        self.statsLabel = QtGui.QLabel(self.centralwidget)
        self.statsLabel.setMaximumSize(QtCore.QSize(300, 16777215))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.statsLabel.setFont(font)
        self.statsLabel.setObjectName(_fromUtf8("statsLabel"))
        self.statsLayout.addWidget(self.statsLabel)
        self.tableView = QtGui.QTableView(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setMinimumSize(QtCore.QSize(300, 0))
        self.tableView.setMaximumSize(QtCore.QSize(300, 16777215))
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.statsLayout.addWidget(self.tableView)
        self.horizontalLayout.addLayout(self.statsLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "ADC Viewer", None))
        self.timeStampLabel.setText(_translate("MainWindow", "Time stamp:", None))
        self.timeStamp.setText(_translate("MainWindow", "XXXXXXXXXXXX", None))
        self.statsLabel.setText(_translate("MainWindow", "Packet information", None))

