# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'timer.ui'
#
# Created: Mon Oct 12 21:40:38 2009
#      by: PyQt4 UI code generator 4.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(330,125)
        MainWindow.setWindowTitle("pyvoctr")
        self.centralwidget = QtGui.QWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.vbox_work_area = QtGui.QVBoxLayout()
        self.vbox_work_area.setSpacing(3)
        self.vbox_work_area.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.vbox_work_area.setObjectName("vbox_work_area")
        self.lb_source = QtGui.QLabel(self.centralwidget)
        self.lb_source.setTextFormat(QtCore.Qt.RichText)
        self.lb_source.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_source.setObjectName("lb_source")
        self.vbox_work_area.addWidget(self.lb_source)
        self.lb_target = QtGui.QLabel(self.centralwidget)
        self.lb_target.setTextFormat(QtCore.Qt.RichText)
        self.lb_target.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_target.setObjectName("lb_target")
        self.vbox_work_area.addWidget(self.lb_target)
        self.gridLayout.addLayout(self.vbox_work_area,7,0,1,1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,330,23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        pass

