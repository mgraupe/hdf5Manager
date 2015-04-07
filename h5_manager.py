#! python
import os
import sys
from os.path import join, dirname, isdir
import glob
import h5py
import pdb
import time
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.ticker import MultipleLocator

import numpy as np
from datetime import datetime
from scipy.spatial import ConvexHull
from scipy.cluster.hierarchy import average, fcluster
from scipy.stats import mode
from shapely.geometry import MultiPolygon, Polygon
from shapely.topology import TopologicalError
from skimage import transform as tf
import itertools as it
from random import shuffle
import warnings as wa

from hdf5_manager import Ui_MainWindow
#from importROIsWidget import Ui_importROIsWidget

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from guidata import qthelpers

import guiqwt.baseplot
#import guiqwt_patch
#guiqwt.baseplot.BasePlot.add_item_with_z_offset = guiqwt_patch.add_item_with_z_offset
from guiqwt.plot import ImageDialog
from guiqwt.tools import FreeFormTool, InteractiveTool, \
    RectangleTool, RectangularShapeTool, SelectTool
from guiqwt.builder import make
from guiqwt.shapes import PolygonShape, EllipseShape
from guiqwt.events import setup_standard_tool_filter, PanHandler
from guiqwt.image import ImageItem

from internal_ipkernel import InternalIPKernel
#def create_window(window_class):
	#"""Create a Qt window in Python, or interactively in IPython with Qt GUI
	#event loop integration.
	#"""
	#app_created = False
	#app = QtCore.QCoreApplication.instance()
	#if app is None:
		#app = QtGui.QApplication(sys.argv)
		#app_created = True
	#app.references = set()
	#window = window_class()
	#app.references.add(window)
	#window.show()
	#if app_created:
		#app.exec_()
	#return window

def hyphen_range(s):
	#print s, s.split(',')
	""" yield each integer from a complex range string like "1-9,12, 15-20,23"

	>>> list(hyphen_range('1-9,12, 15-20,23'))
	[1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 15, 16, 17, 18, 19, 20, 23]

	>>> list(hyphen_range('1-9,12, 15-20,2-3-4'))
	Traceback (most recent call last):
		...
	ValueError: format error in 2-3-4
	"""
	for x in s.split(','):
		elem = x.split('-')
		if len(elem) == 1: # a number
			yield int(elem[0])
		elif len(elem) == 2: # a range inclusive
			start, end = map(int, elem)
			for i in xrange(start, end+1):
				yield i
		else: # more than one hyphen
			raise ValueError('format error in %s' % x)

class hdf5Viewer(QMainWindow, Ui_MainWindow,InternalIPKernel):
	"""Instance of the ROI Buddy Qt interface."""
	def __init__(self):
		"""
		Initialize the application
		"""
		# initialize the UI and parent class
		QMainWindow.__init__(self)
		self.setupUi(self)
		self.setWindowTitle('HDF5 file viewer')
		#
		self.create_status_bar()
		# 
		self.connectSignals()
		
		#self.ipk = InternalIPKernel()
		self.init_ipkernel('qt')
		
		#self.ipk = InternalIPKernel.init_ipkernel('qt')
		#window = create_window(MyQtWindow)
		#curDir = os.getcwd()
		
		self.experimentTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
		
		self.saveAttributeChangeBtn.setEnabled(False)
		self.restoreAttributesBtn.setEnabled(False)
		
		self.saveNotesBtn.setEnabled(False)
		self.restoreNotesBtn.setEnabled(False)
		
	####################################################
        # set status bar
	def create_status_bar(self):
		self.statusBar().addWidget(QLabel("Ready"), 1)
		
	####################################################
        # connect signals to actions
	def connectSignals(self):

		# chose directory containing data files
		self.loadDirectoryBtn.clicked.connect(self.load_directory)
		self.reloadDirectoryBtn.clicked.connect(self.reload_directory)
		
		# data section changed
		self.experimentTree.currentItemChanged.connect(self.toggle_data_selection)
		
		# plot currently active data
		self.plotDataBtn.clicked.connect(self.plot_data)
		self.addToPlotBtn.clicked.connect(self.add_to_plot)
		
		# Attributes
		self.experimentAttributes.itemChanged.connect(self.attributeChanges) 
		self.groupAttributes.itemChanged.connect(self.attributeChanges) 
		self.dataSetAttributes.itemChanged.connect(self.attributeChanges) 
		
		self.saveAttributeChangeBtn.clicked.connect(self.saveAttributes)
		self.restoreAttributesBtn.clicked.connect(self.toggle_data_selection)
		
		# Notes
		self.experimentNotesValue.textChanged.connect(self.notesChanges)
		self.groupNotesValue.textChanged.connect(self.notesChanges)
		
		self.saveNotesBtn.clicked.connect(self.saveNotes)
		self.restoreNotesBtn.clicked.connect(self.toggle_data_selection)
		
		# iPython
		self.launchiPythonBtn.clicked.connect(self.new_qt_console)
		self.sendToConsoleBtn.clicked.connect(self.add_selection_to_console)
		self.plotNameSpaceBtn.clicked.connect(self.print_namespace)

        
        ####################################################
        # load directory with data files
        def load_directory(self):
		
		dataDirNew = str(QFileDialog.getExistingDirectory(self, "Select Data Directory","/home/mgraupe/Documents/BTsync/brandon_data"))
		#fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')
		
		if len(dataDirNew)>0:
			#self.dataDirEdit.setText(dataDirNew)
			print dataDirNew
			self.dataDirectory = dataDirNew + '/'
			self.fillOutFileList() 
		
	####################################################
        # reload directory with data files
        def reload_directory(self):
		self.fillOutFileList()
		
	####################################################
        #  plot data
	def plot_data(self):
		# obtain currently selected item
		multipleTempItems = self.experimentTree.selectedItems()
		curItemList = []
		for i in range(len(multipleTempItems)):
			curItemList.append(multipleTempItems[i].data(0, Qt.UserRole).toPyObject()) 
		nSelection = len(multipleTempItems)
		#tempItem = self.experimentTree.currentItem()
		#print len(tempItem), tempItem
		#curItem = tempItem.data(0, Qt.UserRole).toPyObject()
		
		# subselection of data to plot specified in GUI
		if self.dataSetSelection.text():
			#print self.dataSetSelection.text(), type(self.dataSetSelection.text())
			dsSelection = list(hyphen_range(str(self.dataSetSelection.text())))
			# reduce by one since index starts with 0
			#dsSelection = [i-1 for i in dsSelection]
			selection = True
		else:
			selection = False
		
		# create figure
		fig_width = 9 # width in inches
                fig_height = 6  # height in inches
                fig_size =  [fig_width,fig_height]
                params = {'axes.labelsize': 12,
                        'axes.titlesize': 12,
                        'font.size': 12,
                        'xtick.labelsize': 12,
                        'ytick.labelsize': 12,
                        'figure.figsize': fig_size,
                        'savefig.dpi' : 600,
                        'axes.linewidth' : 1.3,
                        'ytick.major.size' : 4,      # major tick size in points
                        'xtick.major.size' : 4      # major tick size in points
                        #'edgecolor' : None
                        #'xtick.major.size' : 2,
                        #'ytick.major.size' : 2,
                        }
                rcParams.update(params)
                
                self.fig = plt.figure()
                
                self.ax1 = self.fig.add_subplot(111)
                # set title
                #if nSelection == 1:
		#ax1.set_title(curItem.file.filename + ' : ' + curItem.name, fontsize=14)
		#else:
		self.ax1.set_title(curItemList[0].file.filename + ' : ' + curItemList[0].name, fontsize=14)
                
		# time-series plot
		if self.timeSeriesRadioBtn.isChecked():
			try:
				dt = curItemList[0].attrs['dt']
			except KeyError:
				if selection:
					a1i = self.ax1.plot(curItemList[0].value[:,dsSelection])
					plt.legend(iter(a1i),dsSelection,loc=1,frameon=False)
				else:
					a1i = self.ax1.plot(curItemList[0].value)
					plt.legend(iter(a1i),list(range(curItemList[0].shape[1])),loc=1,frameon=False)
			else:
				tt = np.linspace(0.,(curItemList[0].shape[0]-1)*dt,curItemList[0].shape[0])
				if selection:
					a1i = self.ax1.plot(tt,curItemList[0].value[:,dsSelection],label=dsSelection)
					plt.legend(iter(a1i),dsSelection,loc=1,frameon=False)
				else:
					a1i = self.ax1.plot(tt,curItemList[0].value)
					plt.legend(iter(a1i),list(range(curItemList[0].shape[1])),loc=1,frameon=False)
				#ax1.plot(tt,curItem.value[:,dsSelection])
				self.ax1.set_xlabel('time (sec)')
				#plt.legend(loc=1,frameon=False)
		# plot spikes plot
                elif self.spikesRadioBtn.isChecked():
			for ith, trial in enumerate(curItemList):
				self.ax1.vlines(trial.value,  ith + .6, ith + 1.4)
			self.ax1.set_ylim(.5, len(curItemList) + .5)
			self.ax1.yaxis.set_major_locator(MultipleLocator(1))
		# 3D plot
		elif self.threeDRadioBtn.isChecked():
			a1i = self.ax1.imshow(curItemList[0].value,origin='lower',interpolation='none')
			plt.colorbar(a1i)
		# generic plot
		else:
			if selection:
				a1i = self.ax1.plot(curItemList[0].value[:,dsSelection])
				plt.legend(iter(a1i),dsSelection,loc=1,frameon=False)
			else:
				a1i = self.ax1.plot(curItemList[0].value)
				plt.legend(iter(a1i),list(range(curItemList[0].shape[1])),loc=1,frameon=False)
                
                self.ax1.spines['top'].set_visible(False)
		self.ax1.spines['right'].set_visible(False)
		self.ax1.spines['bottom'].set_position(('outward', 10))
		self.ax1.spines['left'].set_position(('outward', 10))
		self.ax1.yaxis.set_ticks_position('left')
		self.ax1.xaxis.set_ticks_position('bottom')
		
                #plt.colorbar(a1i)
                
                #ax2 = self.fig.add_subplot(212)
                #ax2.set_title('Histogram (note max. value is 65532)')
                #ax2.hist(Sima.flatten()[13:],bins=100)
                
                try:
                        plt.show()
                except AttributeError:
                        pass
	####################################################
        #  plot data
	def add_to_plot(self):
		# obtain currently selected item
		multipleTempItems = self.experimentTree.selectedItems()
		curItemList = []
		for i in range(len(multipleTempItems)):
			curItemList.append(multipleTempItems[i].data(0, Qt.UserRole).toPyObject()) 
		nSelection = len(multipleTempItems)
		#tempItem = self.experimentTree.currentItem()
		#print len(tempItem), tempItem
		#curItem = tempItem.data(0, Qt.UserRole).toPyObject()
		
		# subselection of data to plot specified in GUI
		if self.dataSetSelection.text():
			#print self.dataSetSelection.text(), type(self.dataSetSelection.text())
			dsSelection = list(hyphen_range(str(self.dataSetSelection.text())))
			# reduce by one since index starts with 0
			#dsSelection = [i-1 for i in dsSelection]
			selection = True
		else:
			selection = False
		
		# time-series plot
		if self.timeSeriesRadioBtn.isChecked():
			try:
				dt = curItemList[0].attrs['dt']
			except KeyError:
				if selection:
					a1i = self.ax1.plot(curItemList[0].value[:,dsSelection])
					plt.legend(iter(a1i),dsSelection,loc=1,frameon=False)
				else:
					a1i = self.ax1.plot(curItemList[0].value)
					plt.legend(iter(a1i),list(range(curItemList[0].shape[1])),loc=1,frameon=False)
			else:
				tt = np.linspace(0.,(curItemList[0].shape[0]-1)*dt,curItemList[0].shape[0])
				if selection:
					a1i = self.ax1.plot(tt,curItemList[0].value[:,dsSelection],label=dsSelection)
					plt.legend(iter(a1i),dsSelection,loc=1,frameon=False)
				else:
					a1i = self.ax1.plot(tt,curItemList[0].value)
					plt.legend(iter(a1i),list(range(curItemList[0].shape[1])),loc=1,frameon=False)
				#self.ax1.plot(tt,curItem.value[:,dsSelection])
				self.ax1.set_xlabel('time (sec)')
				#plt.legend(loc=1,frameon=False)
		# plot spikes plot
                elif self.spikesRadioBtn.isChecked():
			for ith, trial in enumerate(curItemList):
				self.ax1.vlines(trial.value,  ith + .6, ith + 1.4)
			self.ax1.set_ylim(.5, len(curItemList) + .5)
			self.ax1.yaxis.set_major_locator(MultipleLocator(1))
		# 3D plot
		elif self.threeDRadioBtn.isChecked():
			a1i = self.ax1.imshow(curItemList[0].value,origin='lower',interpolation='none')
			plt.colorbar(a1i)
		# generic plot
		else:
			if selection:
				a1i = self.ax1.plot(curItemList[0].value[:,dsSelection])
				plt.legend(iter(a1i),dsSelection,loc=1,frameon=False)
			else:
				a1i = self.ax1.plot(curItemList[0].value)
				plt.legend(iter(a1i),list(range(curItemList[0].shape[1])),loc=1,frameon=False)
                
                try:
                        plt.draw()
                except AttributeError:
                        pass
		
	####################################################
	def fillOutFileList(self):
		# clear current list
		self.experimentTree.clear()
		
		curDir = os.getcwd()
		os.chdir(self.dataDirectory)
		dataFileList = glob.glob("*.hdf5")
		#print 'Data file list'
		#print dataFileList
		
		for n in range(len(dataFileList)):
			ff = h5py.File(dataFileList[n], 'r+')
			
			def recursivePopulateTree(parent_node, data):
				tree_node = QTreeWidgetItem([data.name])
				tree_node.setData(0, Qt.UserRole, data)
				parent_node.addChild(tree_node)
				if type(data) == h5py._hl.group.Group:
					for item in data.itervalues():
						recursivePopulateTree(tree_node, item)
			# add root
			topnode = QTreeWidgetItem([ff.filename])
			f = QFont()
			f.setBold(True)
			f.setPointSize(11)
			topnode.setFont(0,f)
			root = ff["/"]
			topnode.setData(0, Qt.UserRole, root)
			self.experimentTree.addTopLevelItem(topnode)
			for item in root.itervalues():
				recursivePopulateTree(topnode, item)
		self.experimentTree.setHeaderLabel(self.dataDirectory)
		os.chdir(curDir)
		#self.saveAttributeChangeBtn.setEnabled(False)
	####################################################
	def toggle_data_selection(self):
		
		treeItem = self.experimentTree.currentItem()
		
		item = treeItem.data(0, Qt.UserRole).toPyObject()
		
		self.experimentAttributes.clear()
		self.experimentAttributesFixed.clear()
		self.groupAttributes.clear()
		self.groupAttributesFixed.clear()
		self.dataSetAttributes.clear()
		self.dataSetAttributesFixed.clear()
		self.experimentNotesValue.clear()
		self.groupNotesValue.clear()
		
		#self.groupAttributes.insertRow(6)
		
		
		#if type(item) == h5py._hl.group.Group:
		#elif type(item) == h5py._hl.files.File:
		
		# experiment  data always applies
		n=0
		for eee in item.file.attrs.iteritems():
			if str(eee[0]) == 'notes':
				self.experimentNotesValue.setPlainText(str(item.file.attrs['notes']))
			else:
				newitemC0 = QTableWidgetItem(str(eee[0]))
				newitemC1 = QTableWidgetItem(str(eee[1]))
				self.experimentAttributes.setItem(n, 0, newitemC0)
				self.experimentAttributes.setItem(n, 1, newitemC1)
				n+=1
				
			#self.expValue.setText(str(item.file.attrs['experiment']))
			#self.experimentDateValue.setText(str(item.file.attrs['expDate']))
			#self.recordingIDValue.setText(str(item.file.attrs['expID']))
			#self.analysisFileValue.setText(str(item.file.attrs['analysisFile']))
			#self.analysisFileLocationValue.setText(str(item.file.attrs['analysisFileLocation']))
			#self.lastAnalyzedValue.setText(time.ctime(os.path.getmtime(self.dataDirectory+item.file.filename)))
		nMembers = len(item.file.keys())
		
		newItemC0 = QTableWidgetItem(str('number of members'))
		#newItemC0.setFlags(Qt.ItemIsEnabled)
		self.experimentAttributesFixed.setItem(0, 0, newItemC0)
		#self.experimentAttributes.item(n, 0).setBackground(QColor(230,230,230))
		newItemC1 = QTableWidgetItem(str(nMembers))
		#newItemC1.setFlags(Qt.ItemIsEnabled)
		self.experimentAttributesFixed.setItem(0, 1, newItemC1)
		
		newItemC0 = QTableWidgetItem(str('last analyzed'))
		#newItemC0.setFlags(Qt.ItemIsEnabled)
		self.experimentAttributesFixed.setItem(1, 0, newItemC0)
		#self.experimentAttributes.item(n, 0).setBackground(QColor(230,230,230))
		newItemC1 = QTableWidgetItem(time.ctime(os.path.getmtime(self.dataDirectory+item.file.filename)))
		#newItemC1.setFlags(Qt.ItemIsEnabled)
		self.experimentAttributesFixed.setItem(1, 1, newItemC1)
		#self.experimentAttributes.item(n, 1).setBackground(QColor(230,230,230))
		
		newItemC0 = QTableWidgetItem(str('file size'))
		#newItemC0.setFlags(Qt.ItemIsEnabled)
		self.experimentAttributesFixed.setItem(2, 0, newItemC0)
		#self.experimentAttributes.item(n+1, 0).setBackground(QColor(230,230,230))
		newItemC1 = QTableWidgetItem(str(os.path.getsize(self.dataDirectory+item.file.filename)))
		#newItemC1.setFlags(Qt.ItemIsEnabled)
		self.experimentAttributesFixed.setItem(2, 1, newItemC1)
		#self.experimentAttributes.item(n+1, 1).setBackground(QColor(230,230,230))
			
			
		# in case a dataset is selected
		if type(item) == h5py._hl.dataset.Dataset:
			#print 'ds', item.name
			# data-set properties
			newItemC0 = QTableWidgetItem(str('shape'))
			#newItemC0.setFlags(Qt.ItemIsEnabled)
			self.dataSetAttributesFixed.setItem(0, 0, newItemC0)
			#self.dataSetAttributes.item(0, 0).setBackground(QColor(230,230,230))
			newItemC1 = QTableWidgetItem(str(item.shape))
			#newItemC1.setFlags(Qt.ItemIsEnabled)
			self.dataSetAttributesFixed.setItem(0, 1, newItemC1)
			#self.dataSetAttributes.item(0, 1).setBackground(QColor(230,230,230))
			newItemC0 = QTableWidgetItem(str('data type'))
			#newItemC0.setFlags(Qt.ItemIsEnabled)
			self.dataSetAttributesFixed.setItem(1, 0, newItemC0)
			#self.dataSetAttributes.item(1, 0).setBackground(QColor(230,230,230))
			newItemC1 = QTableWidgetItem(str(item.dtype))
			#newItemC1.setFlags(Qt.ItemIsEnabled)
			self.dataSetAttributesFixed.setItem(1, 1, newItemC1)
			#self.dataSetAttributes.item(1, 1).setBackground(QColor(230,230,230))
			#self.shapeValue.setText(str(item.shape))
			#self.typeValue.setText(str(item.dtype))
			# attributes of data-set
			n=0
			for aaa in item.attrs.iteritems():
				newitemC0 = QTableWidgetItem(str(aaa[0]))
				newitemC1 = QTableWidgetItem(str(aaa[1]))
				self.dataSetAttributes.setItem(n, 0, newitemC0)
				self.dataSetAttributes.setItem(n, 1, newitemC1)
				n+=1
				#print n
			# attributes of parent directory
			nMembers = len(item.parent.keys())
			#self.memberNumberValue.setText(str(nMembers))
			newItemC0 = QTableWidgetItem(str('number of members'))
			#newItemC0.setFlags(Qt.ItemIsEnabled)
			self.groupAttributesFixed.setItem(0, 0, newItemC0)
			#self.groupAttributes.item(0, 0).setBackground(QColor(230,230,230))
			newItemC1 = QTableWidgetItem(str(nMembers))
			#newItemC1.setFlags(Qt.ItemIsEnabled)
			self.groupAttributesFixed.setItem(0, 1, newItemC1)
			#self.groupAttributes.item(0, 1).setBackground(QColor(230,230,230))
			n=0
			for ppp in item.parent.attrs.iteritems():
				if str(ppp[0]) == 'groupNotes':
					self.groupNotesValue.setPlainText(str(item.parent.attrs['groupNotes']))
				else:
					newitemC0 = QTableWidgetItem(str(ppp[0]))
					newitemC1 = QTableWidgetItem(str(ppp[1]))
					self.groupAttributes.setItem(n, 0, newitemC0)
					self.groupAttributes.setItem(n, 1, newitemC1)
					n+=1
			self.plotDataBtn.setEnabled(True)
		# in case group is selected
		elif type(item) == h5py._hl.group.Group and not item.name == '/':
			#print 'group', item.name
			# attributes of group
			nMembers = len(item.keys())
			#self.memberNumberValue.setText(str(nMembers))
			newItemC0 = QTableWidgetItem(str('number of members'))
			#newItemC0.setFlags(Qt.ItemIsEnabled)
			self.groupAttributesFixed.setItem(0, 0, newItemC0)
			#self.groupAttributes.item(0, 0).setBackground(QColor(230,230,230))
			newItemC1 = QTableWidgetItem(str(nMembers))
			#newItemC1.setFlags(Qt.ItemIsEnabled)
			self.groupAttributesFixed.setItem(0, 1, newItemC1)
			#self.groupAttributes.item(0, 1).setBackground(QColor(230,230,230))
			n=0
			for ppp in item.attrs.iteritems():
				if str(ppp[0]) == 'groupNotes':
					self.groupNotesValue.setPlainText(str(item.attrs['groupNotes']))
				else:
					newitemC0 = QTableWidgetItem(str(ppp[0]))
					newitemC1 = QTableWidgetItem(str(ppp[1]))
					self.groupAttributes.setItem(n, 0, newitemC0)
					self.groupAttributes.setItem(n, 1, newitemC1)
					n+=1
			self.plotDataBtn.setEnabled(False)
		
		
		
		#pdb.set_trace()
		#activeExp = self.experimentTree.currentItem()
		#print activeExp
		#print dataset.filename
		self.saveAttributeChangeBtn.setEnabled(False)
		self.restoreAttributesBtn.setEnabled(False)
		self.saveNotesBtn.setEnabled(False)
		self.restoreNotesBtn.setEnabled(False)
		
	#############################################################################
	def attributeChanges(self):
		self.saveAttributeChangeBtn.setEnabled(True)
		self.restoreAttributesBtn.setEnabled(True)
		
	#############################################################################
	def saveAttributes(self):
		# get selected item
		treeItem = self.experimentTree.currentItem()
		item = treeItem.data(0, Qt.UserRole).toPyObject()
		for row in xrange(self.experimentAttributes.rowCount()):
			itemC0 = self.experimentAttributes.item(row, 0)
			itemC1 = self.experimentAttributes.item(row, 1)
			print row, type(itemC0)
			if itemC0:
				#print itemC0.text(), itemC1.text()
				#text = str(item.text())
				#for i in arange(5):
				#print itemC0.text(), type(itemC0.text())
				item.file.attrs.__setitem__(str(itemC0.text()), str(itemC1.text()))
		
		# is group was selected
		if type(item) == h5py._hl.dataset.Dataset or (type(item) == h5py._hl.group.Group and not item.name == '/'):
			# group attributes
			for row in xrange(self.groupAttributes.rowCount()):
				itemC0 = self.groupAttributes.item(row, 0)
				itemC1 = self.groupAttributes.item(row, 1)
				#print row, type(itemC0)
				if itemC0:
					#print itemC0.text(), itemC1.text()
					#text = str(item.text())
					#for i in arange(5):
					#print itemC0.text(), type(itemC0.text())
					item.parent.attrs.__setitem__(str(itemC0.text()), str(itemC1.text()))
		if type(item) == h5py._hl.dataset.Dataset:
			# data-set attributes
			for row in xrange(self.dataSetAttributes.rowCount()):
				itemC0 = self.dataSetAttributes.item(row, 0)
				itemC1 = self.dataSetAttributes.item(row, 1)
				print row, type(itemC0)
				if itemC0:
					#print itemC0.text(), itemC1.text()
					#text = str(item.text())
					#for i in arange(5):
					#print itemC0.text(), type(itemC0.text())
					item.attrs.__setitem__(str(itemC0.text()), str(itemC1.text()))
			
		#print 'saved'
		self.saveAttributeChangeBtn.setEnabled(False)
		self.restoreAttributesBtn.setEnabled(False)
	#############################################################################
	def notesChanges(self):
		self.saveNotesBtn.setEnabled(True)
		self.restoreNotesBtn.setEnabled(True)
	#############################################################################
	def saveNotes(self):
		# get selected item
		treeItem = self.experimentTree.currentItem()
		item = treeItem.data(0, Qt.UserRole).toPyObject()
		
		#try:
		#	item.file.attrs['notes']
		#except KeyError:
		item.file.attrs.__setitem__(str('notes'), str(self.experimentNotesValue.toPlainText()))
		
		if type(item) == h5py._hl.dataset.Dataset:
			#print 'ds'
			item.parent.attrs.__setitem__(str('groupNotes'), str(self.groupNotesValue.toPlainText()))
		elif type(item) == h5py._hl.group.Group and not item.name == '/':
			#print 'group'
			item.attrs.__setitem__(str('groupNotes'), str(self.groupNotesValue.toPlainText()))
		#
		self.saveNotesBtn.setEnabled(False)
		self.restoreNotesBtn.setEnabled(False)
	#############################################################################
	def add_selection_to_console(self):
		# get selected item
		treeItem = self.experimentTree.currentItem()
		item = treeItem.data(0, Qt.UserRole).toPyObject()
		
		self.addData(item.value)
	#############################################################################
	def closeEvent(self, event):
		
		reply = QMessageBox.question(self, 'Message',
		"Are you sure to quit?", QMessageBox.Yes | 
		QMessageBox.No, QMessageBox.No)

		if reply == QMessageBox.Yes:
			self.cleanup_consoles()
			quit()
			event.accept()
			print 'bye'
		else:
			event.ignore()        
		
			
##########################################################
if __name__ == "__main__":
	app = QApplication(sys.argv)
	form = hdf5Viewer()
	form.show()
	form.ipkernel.start()
	app.exec_()
	