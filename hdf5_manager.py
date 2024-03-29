# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hdf5_manager.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1091, 866)
        MainWindow.setMinimumSize(QtCore.QSize(500, 700))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        MainWindow.setStyleSheet("background-color: rgb(226, 226, 226);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridFrame = QtWidgets.QFrame(self.centralwidget)
        self.gridFrame.setMinimumSize(QtCore.QSize(0, 10))
        self.gridFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.gridFrame.setObjectName("gridFrame")
        self.gridLayout = QtWidgets.QGridLayout(self.gridFrame)
        self.gridLayout.setContentsMargins(6, 6, 6, 6)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalWidget = QtWidgets.QWidget(self.gridFrame)
        self.horizontalWidget.setObjectName("horizontalWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.loadDirectoryBtn = QtWidgets.QPushButton(self.horizontalWidget)
        self.loadDirectoryBtn.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.loadDirectoryBtn.setObjectName("loadDirectoryBtn")
        self.horizontalLayout_2.addWidget(self.loadDirectoryBtn)
        self.reloadDirectoryBtn = QtWidgets.QPushButton(self.horizontalWidget)
        self.reloadDirectoryBtn.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.reloadDirectoryBtn.setObjectName("reloadDirectoryBtn")
        self.horizontalLayout_2.addWidget(self.reloadDirectoryBtn)
        self.workingDirectory = QtWidgets.QLineEdit(self.horizontalWidget)
        self.workingDirectory.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.workingDirectory.setObjectName("workingDirectory")
        self.horizontalLayout_2.addWidget(self.workingDirectory)
        self.gridLayout.addWidget(self.horizontalWidget, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.gridFrame, 0, 0, 1, 1)
        self.gridFrame1 = QtWidgets.QFrame(self.centralwidget)
        self.gridFrame1.setMinimumSize(QtCore.QSize(0, 20))
        self.gridFrame1.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.gridFrame1.setObjectName("gridFrame1")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.gridFrame1)
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.horizontalWidget1 = QtWidgets.QWidget(self.gridFrame1)
        self.horizontalWidget1.setObjectName("horizontalWidget1")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.horizontalWidget1)
        self.horizontalLayout_10.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.gridFrame2 = QtWidgets.QFrame(self.horizontalWidget1)
        self.gridFrame2.setBaseSize(QtCore.QSize(0, 0))
        self.gridFrame2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.gridFrame2.setLineWidth(1)
        self.gridFrame2.setObjectName("gridFrame2")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.gridFrame2)
        self.gridLayout_6.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_6.setSpacing(2)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_5 = QtWidgets.QLabel(self.gridFrame2)
        self.label_5.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout_6.addWidget(self.label_5, 0, 0, 1, 1)
        self.horizontalWidget2 = QtWidgets.QWidget(self.gridFrame2)
        self.horizontalWidget2.setObjectName("horizontalWidget2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.horizontalWidget2)
        self.horizontalLayout_5.setContentsMargins(5, 3, 5, 3)
        self.horizontalLayout_5.setSpacing(5)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.genericRadioBtn = QtWidgets.QRadioButton(self.horizontalWidget2)
        self.genericRadioBtn.setObjectName("genericRadioBtn")
        self.plottingChoice = QtWidgets.QButtonGroup(MainWindow)
        self.plottingChoice.setObjectName("plottingChoice")
        self.plottingChoice.addButton(self.genericRadioBtn)
        self.horizontalLayout_5.addWidget(self.genericRadioBtn)
        self.timeSeriesRadioBtn = QtWidgets.QRadioButton(self.horizontalWidget2)
        self.timeSeriesRadioBtn.setObjectName("timeSeriesRadioBtn")
        self.plottingChoice.addButton(self.timeSeriesRadioBtn)
        self.horizontalLayout_5.addWidget(self.timeSeriesRadioBtn)
        self.spikesRadioBtn = QtWidgets.QRadioButton(self.horizontalWidget2)
        self.spikesRadioBtn.setObjectName("spikesRadioBtn")
        self.plottingChoice.addButton(self.spikesRadioBtn)
        self.horizontalLayout_5.addWidget(self.spikesRadioBtn)
        self.threeDRadioBtn = QtWidgets.QRadioButton(self.horizontalWidget2)
        self.threeDRadioBtn.setObjectName("threeDRadioBtn")
        self.plottingChoice.addButton(self.threeDRadioBtn)
        self.horizontalLayout_5.addWidget(self.threeDRadioBtn)
        self.ImageStackRadioBtn = QtWidgets.QRadioButton(self.horizontalWidget2)
        self.ImageStackRadioBtn.setObjectName("ImageStackRadioBtn")
        self.plottingChoice.addButton(self.ImageStackRadioBtn)
        self.horizontalLayout_5.addWidget(self.ImageStackRadioBtn)
        self.gridLayout_6.addWidget(self.horizontalWidget2, 1, 0, 1, 1)
        self.horizontalWidget3 = QtWidgets.QWidget(self.gridFrame2)
        self.horizontalWidget3.setObjectName("horizontalWidget3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalWidget3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.dataSetSelection = QtWidgets.QLineEdit(self.horizontalWidget3)
        self.dataSetSelection.setMaximumSize(QtCore.QSize(200, 16777215))
        self.dataSetSelection.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.dataSetSelection.setObjectName("dataSetSelection")
        self.horizontalLayout_3.addWidget(self.dataSetSelection)
        self.plotDataBtn = QtWidgets.QPushButton(self.horizontalWidget3)
        self.plotDataBtn.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.plotDataBtn.setObjectName("plotDataBtn")
        self.horizontalLayout_3.addWidget(self.plotDataBtn)
        self.addToPlotBtn = QtWidgets.QPushButton(self.horizontalWidget3)
        self.addToPlotBtn.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.addToPlotBtn.setObjectName("addToPlotBtn")
        self.horizontalLayout_3.addWidget(self.addToPlotBtn)
        self.gridLayout_6.addWidget(self.horizontalWidget3, 3, 0, 1, 1)
        self.horizontalLayout_10.addWidget(self.gridFrame2)
        self.gridFrame3 = QtWidgets.QFrame(self.horizontalWidget1)
        self.gridFrame3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.gridFrame3.setObjectName("gridFrame3")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.gridFrame3)
        self.gridLayout_5.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.horizontalWidget4 = QtWidgets.QWidget(self.gridFrame3)
        self.horizontalWidget4.setObjectName("horizontalWidget4")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.horizontalWidget4)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.launchiPythonBtn = QtWidgets.QPushButton(self.horizontalWidget4)
        self.launchiPythonBtn.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.launchiPythonBtn.setObjectName("launchiPythonBtn")
        self.horizontalLayout_6.addWidget(self.launchiPythonBtn)
        self.sendToConsoleBtn = QtWidgets.QPushButton(self.horizontalWidget4)
        self.sendToConsoleBtn.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.sendToConsoleBtn.setObjectName("sendToConsoleBtn")
        self.horizontalLayout_6.addWidget(self.sendToConsoleBtn)
        self.plotNameSpaceBtn = QtWidgets.QPushButton(self.horizontalWidget4)
        self.plotNameSpaceBtn.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.plotNameSpaceBtn.setObjectName("plotNameSpaceBtn")
        self.horizontalLayout_6.addWidget(self.plotNameSpaceBtn)
        self.gridLayout_5.addWidget(self.horizontalWidget4, 2, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.gridFrame3)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.gridLayout_5.addWidget(self.label_6, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem, 1, 0, 1, 1)
        self.horizontalLayout_10.addWidget(self.gridFrame3)
        self.gridLayout_7.addWidget(self.horizontalWidget1, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.gridFrame1, 3, 0, 1, 2)
        self.gridFrame4 = QtWidgets.QFrame(self.centralwidget)
        self.gridFrame4.setMinimumSize(QtCore.QSize(0, 10))
        self.gridFrame4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.gridFrame4.setObjectName("gridFrame4")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.gridFrame4)
        self.gridLayout_8.setContentsMargins(9, 6, 6, 6)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.horizontalWidget5 = QtWidgets.QWidget(self.gridFrame4)
        self.horizontalWidget5.setObjectName("horizontalWidget5")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalWidget5)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.dataSetTree = QtWidgets.QTreeWidget(self.horizontalWidget5)
        self.dataSetTree.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.dataSetTree.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.dataSetTree.setMidLineWidth(0)
        self.dataSetTree.setAnimated(True)
        self.dataSetTree.setObjectName("dataSetTree")
        self.dataSetTree.headerItem().setTextAlignment(1, QtCore.Qt.AlignCenter)
        self.dataSetTree.headerItem().setTextAlignment(2, QtCore.Qt.AlignCenter)
        self.dataSetTree.header().setVisible(True)
        self.dataSetTree.header().setCascadingSectionResizes(False)
        self.dataSetTree.header().setDefaultSectionSize(200)
        self.dataSetTree.header().setMinimumSectionSize(20)
        self.dataSetTree.header().setStretchLastSection(False)
        self.horizontalLayout.addWidget(self.dataSetTree)
        self.attributesTree = QtWidgets.QTreeWidget(self.horizontalWidget5)
        self.attributesTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.attributesTree.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.attributesTree.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.attributesTree.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.attributesTree.setProperty("showDropIndicator", True)
        self.attributesTree.setDragEnabled(False)
        self.attributesTree.setDragDropOverwriteMode(False)
        self.attributesTree.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.attributesTree.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.attributesTree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.attributesTree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.attributesTree.setAutoExpandDelay(-1)
        self.attributesTree.setIndentation(20)
        self.attributesTree.setItemsExpandable(True)
        self.attributesTree.setAnimated(True)
        self.attributesTree.setColumnCount(3)
        self.attributesTree.setObjectName("attributesTree")
        self.attributesTree.headerItem().setTextAlignment(1, QtCore.Qt.AlignCenter)
        self.attributesTree.headerItem().setTextAlignment(2, QtCore.Qt.AlignCenter)
        self.attributesTree.header().setDefaultSectionSize(200)
        self.attributesTree.header().setMinimumSectionSize(20)
        self.attributesTree.header().setSortIndicatorShown(True)
        self.attributesTree.header().setStretchLastSection(False)
        self.horizontalLayout.addWidget(self.attributesTree)
        self.gridLayout_8.addWidget(self.horizontalWidget5, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.gridFrame4, 1, 0, 1, 2)
        self.gridFrame5 = QtWidgets.QFrame(self.centralwidget)
        self.gridFrame5.setMinimumSize(QtCore.QSize(30, 0))
        self.gridFrame5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.gridFrame5.setObjectName("gridFrame5")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridFrame5)
        self.gridLayout_2.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalWidget6 = QtWidgets.QWidget(self.gridFrame5)
        self.horizontalWidget6.setObjectName("horizontalWidget6")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.horizontalWidget6)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label = QtWidgets.QLabel(self.horizontalWidget6)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.label)
        self.currentSelectionValue = QtWidgets.QLineEdit(self.horizontalWidget6)
        self.currentSelectionValue.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.currentSelectionValue.setObjectName("currentSelectionValue")
        self.horizontalLayout_4.addWidget(self.currentSelectionValue)
        self.gridLayout_2.addWidget(self.horizontalWidget6, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.gridFrame5, 2, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1091, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.loadDirectoryBtn.setText(_translate("MainWindow", "Load directory"))
        self.reloadDirectoryBtn.setText(_translate("MainWindow", "Reload"))
        self.workingDirectory.setPlaceholderText(_translate("MainWindow", "Directory of hdf5 files"))
        self.label_5.setText(_translate("MainWindow", "Plotting"))
        self.genericRadioBtn.setText(_translate("MainWindow", "Generic"))
        self.timeSeriesRadioBtn.setText(_translate("MainWindow", "TimeSeries"))
        self.spikesRadioBtn.setText(_translate("MainWindow", "Spikes"))
        self.threeDRadioBtn.setText(_translate("MainWindow", "3D"))
        self.ImageStackRadioBtn.setText(_translate("MainWindow", "ImageStack"))
        self.dataSetSelection.setPlaceholderText(_translate("MainWindow", "Subselection e.g. 0,2,4-6"))
        self.plotDataBtn.setText(_translate("MainWindow", "Plot data"))
        self.addToPlotBtn.setText(_translate("MainWindow", "Add to plot"))
        self.launchiPythonBtn.setText(_translate("MainWindow", "Launch iPython"))
        self.sendToConsoleBtn.setText(_translate("MainWindow", "Send to concole"))
        self.plotNameSpaceBtn.setText(_translate("MainWindow", "Print NameSpace"))
        self.label_6.setText(_translate("MainWindow", "Analysis"))
        self.dataSetTree.setSortingEnabled(True)
        self.dataSetTree.headerItem().setText(0, _translate("MainWindow", "DataSets"))
        self.dataSetTree.headerItem().setText(1, _translate("MainWindow", "Size"))
        self.dataSetTree.headerItem().setText(2, _translate("MainWindow", "Type"))
        self.attributesTree.setSortingEnabled(True)
        self.attributesTree.headerItem().setText(0, _translate("MainWindow", "Attributes"))
        self.attributesTree.headerItem().setText(1, _translate("MainWindow", "Value"))
        self.attributesTree.headerItem().setText(2, _translate("MainWindow", "Type"))
        self.label.setText(_translate("MainWindow", "Selection"))
