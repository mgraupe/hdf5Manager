#! python
import os
import sys
from os.path import join, dirname, isdir
import glob
import h5py
import pdb
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.ticker import MultipleLocator
import re
import pickle

from PyQt4.QtCore import *
from PyQt4.QtGui import *

#from shapely.geometry import MultiPolygon, Polygon
#from shapely.topology import TopologicalError
#from skimage import transform as tf
#import itertools as it
#from random import shuffle
#import warnings as wa

# files
from hdf5_manager import Ui_MainWindow
from internal_ipkernel import InternalIPKernel

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
	"""Instance of the hdf5 Data Manager Qt interface."""
	def __init__(self):
		"""
		Initialize the application
		"""
		# initialize the UI and parent class
		QMainWindow.__init__(self)
		self.setupUi(self)
		self.setWindowTitle('HDF5 Data Manager')
		#
		self.create_status_bar()
		# 
		self.connectSignals()
		
		#self.ipk = InternalIPKernel()
		self.init_ipkernel('qt')
		
		# read settings file if it exists
		try :
			h5Settings = pickle.load(open('.h5Settings.p','rb'))
		except IOError:
			print 'No settings fils found.'
			setExits = False
		else:
			setExits = True
		
		#self.ipk = InternalIPKernel.init_ipkernel('qt')
		#window = create_window(MyQtWindow)
		#curDir = os.getcwd()
		
		self.experimentTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.experimentTree.setColumnWidth(0, 360)
		self.experimentTree.setColumnWidth(1, 90)
		self.experimentTree.setColumnWidth(2, 70)
		self.experimentTree.sortByColumn(0, Qt.AscendingOrder)
		
		self.experimentAttributes.setColumnWidth(0, 140)
		self.experimentAttributes.setColumnWidth(1, 215)
		self.experimentAttributes.setColumnWidth(2, 60)
		
		self.groupAttributes.setColumnWidth(0, 140)
		self.groupAttributes.setColumnWidth(1, 215)
		self.groupAttributes.setColumnWidth(2, 60)
		
		self.dataSetAttributes.setColumnWidth(0, 140)
		self.dataSetAttributes.setColumnWidth(1, 215)
		self.dataSetAttributes.setColumnWidth(2, 60)
		
		#self.experimentTree.headerView().resizeSection(0, 100)
		#self.experimentTree.headerView().resizeSection(1, 40)
		#self.experimentTree.headerView().resizeSection(2, 40)
		
		if setExits:
			DDir = h5Settings['dataDirectory']
			if os.path.isdir(DDir):
				self.dataDirectory = DDir
				self.fillOutFileList()
		
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
		
		self.workingDirectory.editingFinished.connect(self.read_edited_directory)
		
		# data section changed
		self.experimentTree.currentItemChanged.connect(self.toggle_data_selection)
		
		# plot currently active data
		self.plotDataBtn.clicked.connect(self.plot_data)
		self.addToPlotBtn.clicked.connect(self.add_to_plot)
		
		# Attributes
		self.experimentAttributes.itemChanged.connect(self.attributeChanges) 
		self.groupAttributes.itemChanged.connect(self.attributeChanges) 
		self.dataSetAttributes.itemChanged.connect(self.attributeChanges) 
		
		self.addExpRowBtn.clicked.connect(self.addExperimentRow)
		self.addGroupRowBtn.clicked.connect(self.addGroupRow)
		self.addDatasetRowBtn.clicked.connect(self.addDatasetRow)
		
		self.removeExpAttributeBtn.clicked.connect(self.removeExperimentAttribute)
		self.removeGroupAttributeBtn.clicked.connect(self.removeGroupAttribute)
		self.removeDatasetAttributeBtn.clicked.connect(self.removeDatasetAttribute)
		
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
		
		try:
			DDir = self.dataDirectory
		except NameError:
			dataDirNew = str(QFileDialog.getExistingDirectory(self, "Select Data Directory","/home/mgraupe/Documents/BTsync/brandon_data"))
		else:
			dataDirNew = str(QFileDialog.getExistingDirectory(self, "Select Data Directory", DDir))
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
        # manuel edit of directory field
        def read_edited_directory(self):
		
		self.dataDirectory = str(self.workingDirectory.text())
		# add / if not existing
		if self.dataDirectory and self.dataDirectory[-1] != '/':
			self.dataDirectory += '/'
		if self.dataDirectory:
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
				dt = float(curItemList[0].attrs['dt'])
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
				dt = float(curItemList[0].attrs['dt'])
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
				if type(data) == h5py._hl.group.Group:
					tree_node.setData(1, Qt.DisplayRole, str(len(data.keys())))
					try:
						lab = data.attrs['type']
					except KeyError:
						pass
					else:
						tree_node.setData(2, Qt.DisplayRole, str(lab))
						f.setBold(True)
						tree_node.setFont(2,f)
						tree_node.setFont(0,f)
					tree_node.setBackground( 0 , QColor(240, 255, 244) )
					tree_node.setBackground( 1 , QColor(240, 255, 244) )
					tree_node.setBackground( 2 , QColor(240, 255, 244) )
				elif type(data) == h5py._hl.dataset.Dataset:
					tree_node.setData(1, Qt.DisplayRole, str(data.shape))
					tree_node.setData(2, Qt.DisplayRole, str(data.dtype))
				tree_node.setTextAlignment (1, Qt.AlignRight)
				tree_node.setTextAlignment (2, Qt.AlignLeft)
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
			topnode.setData(1, Qt.DisplayRole, str(os.path.getsize(self.dataDirectory+root.file.filename)))
			try:
				lab = root.file.attrs['type']
			except KeyError:
				pass
			else:
				topnode.setData(2, Qt.DisplayRole, str(lab))
			topnode.setTextAlignment (1, Qt.AlignRight)
			topnode.setTextAlignment (1, Qt.AlignLeft)
			topnode.setBackground( 0 , QColor(231, 234, 255) )
			topnode.setBackground( 1 , QColor(231, 234, 255) )
			topnode.setBackground( 2 , QColor(231, 234, 255) )
			self.experimentTree.addTopLevelItem(topnode)
			#self.experimentTree.addTopLevelItem(1,'1')
			for item in root.itervalues():
				recursivePopulateTree(topnode, item)
		#self.experimentTree.setHeaderLabel(0,self.dataDirectory)
		self.workingDirectory.setText(self.dataDirectory)
		os.chdir(curDir)
		#self.saveAttributeChangeBtn.setEnabled(False)
	####################################################
	def fillOutAttributeTable(self,table,it,rowN):
		newitemC0 = QTableWidgetItem(str(it[0]))
		newitemC1 = QTableWidgetItem(str(it[1]))
		newitemC2 = QTableWidgetItem(type(it[1]).__name__)
		if type(it[1]).__name__ == 'ndarray':
			newitemC2 = QTableWidgetItem('arr,'+type(it[1][0]).__name__)
		table.setItem(rowN, 0, newitemC0)
		table.setItem(rowN, 1, newitemC1)
		table.setItem(rowN, 2, newitemC2)
	####################################################
	def toggle_data_selection(self):
		
		treeItem = self.experimentTree.currentItem()
		
		try:
			item = treeItem.data(0, Qt.UserRole).toPyObject()
		except AttributeError:
			pass
		else:
			self.experimentAttributes.clear()
			self.experimentAttributes.setRowCount(8)
			self.groupAttributes.clear()
			self.groupAttributes.setRowCount(5)
			self.dataSetAttributes.clear()
			self.dataSetAttributes.setRowCount(3)
			
			self.experimentNotesValue.clear()
			self.groupNotesValue.clear()
			
			# experiment  data always applies
			nE=0
			rowExperimentN = self.experimentAttributes.rowCount()
			for eee in item.file.attrs.iteritems():
				if str(eee[0]) == 'notes':
					self.experimentNotesValue.setPlainText(str(item.file.attrs['notes']))
				else:
					if nE >= (rowExperimentN-2):
						self.experimentAttributes.insertRow(rowExperimentN)
						rowExperimentN+=1
					self.fillOutAttributeTable(self.experimentAttributes,eee,nE)
					nE+=1
					
			
			# in case a dataset is selected
			if type(item) == h5py._hl.dataset.Dataset:
				# attributes of data-set
				nDS=0
				rowDataSetN = self.dataSetAttributes.rowCount()
				for aaa in item.attrs.iteritems():
					if nDS >= (rowDataSetN-2):
						self.dataSetAttributes.insertRow(rowDataSetN)
						rowDataSetN+=1
					self.fillOutAttributeTable(self.dataSetAttributes,aaa,nDS)
					nDS+=1
				# group attributes
				nG=0
				rowGroupN = self.groupAttributes.rowCount()
				for ppp in item.parent.attrs.iteritems():
					if str(ppp[0]) == 'groupNotes':
						self.groupNotesValue.setPlainText(str(item.parent.attrs['groupNotes']))
					else:
						if nG >= (rowGroupN-2):
							self.groupAttributes.insertRow(rowGroupN)
							rowGroupN+=1
						self.fillOutAttributeTable(self.groupAttributes,ppp,nG)
						nG+=1
				self.plotDataBtn.setEnabled(True)
			# in case group is selected
			elif type(item) == h5py._hl.group.Group and not item.name == '/':
				nG=0
				rowGroupN = self.groupAttributes.rowCount()
				for ppp in item.attrs.iteritems():
					if str(ppp[0]) == 'groupNotes':
						self.groupNotesValue.setPlainText(str(item.attrs['groupNotes']))
					else:
						if nG >= (rowGroupN-2):
							self.groupAttributes.insertRow(rowGroupN)
							rowGroupN+=1
						self.fillOutAttributeTable(self.groupAttributes,ppp,nG)
						nG+=1
				self.plotDataBtn.setEnabled(False)
			#
			self.saveAttributeChangeBtn.setEnabled(False)
			self.restoreAttributesBtn.setEnabled(False)
			self.saveNotesBtn.setEnabled(False)
			self.restoreNotesBtn.setEnabled(False)
		
	#############################################################################
	def attributeChanges(self):
		self.saveAttributeChangeBtn.setEnabled(True)
		self.restoreAttributesBtn.setEnabled(True)
        #############################################################################
	def saveAttributeFields(self,obj,i0,i1,i2):
		if i0 and len(i0.text())>0 :
			#try:
			if i2.text()[:5] == 'float':
				obj.attrs.create(str(i0.text()), float(i1.text()))
			elif i2.text()[:3] == 'int':
				obj.attrs.create(str(i0.text()), int(i1.text()))
			elif i2.text()[:3] == 'str':
				obj.attrs.create(str(i0.text()), str(i1.text()))
			elif i2.text()[:4] == 'arr,':
				if i2.text()[4:7] == 'int':
					temp = map(int,re.findall(r'\d+', str((i1.text()))))
					obj.attrs.create(str(i0.text()), np.array(temp))
				elif i2.text()[4:9] == 'float':
					temp = map(float,re.findall(r'\d+', str((i1.text()))))
					obj.attrs.create(str(i0.text()), np.array(temp))
			else:
				QMessageBox.warning(self, "Warning","Attribute type has to be float, int or str.")
					#
			#except ValueError, AttributeError:
			#	pass
	#############################################################################
	def saveAttributes(self):
		# get selected item
		treeItem = self.experimentTree.currentItem()
		selItem = treeItem.data(0, Qt.UserRole).toPyObject()
		# save experiment attributes
		self.delExperimentAttributes(selItem)
		for row in xrange(self.experimentAttributes.rowCount()):
			itemC0 = self.experimentAttributes.item(row, 0)
			itemC1 = self.experimentAttributes.item(row, 1)
			itemC2 = self.experimentAttributes.item(row, 2)
			self.saveAttributeFields(selItem.file,itemC0,itemC1,itemC2)
		
		# save group attributes
		if (type(selItem) == h5py._hl.group.Group and not selItem.name == '/'):
			# group attributes
			self.delAttributes(selItem)
			for row in xrange(self.groupAttributes.rowCount()):
				itemC0 = self.groupAttributes.item(row, 0)
				itemC1 = self.groupAttributes.item(row, 1)
				itemC2 = self.groupAttributes.item(row, 2)
				self.saveAttributeFields(selItem,itemC0,itemC1,itemC2)
		# in case dataset was selected
		elif type(selItem) == h5py._hl.dataset.Dataset:
			# data-set attributes
			self.delAttributes(selItem)
			for row in xrange(self.dataSetAttributes.rowCount()):
				itemC0 = self.dataSetAttributes.item(row, 0)
				itemC1 = self.dataSetAttributes.item(row, 1)
				itemC2 = self.dataSetAttributes.item(row, 2)
				self.saveAttributeFields(selItem,itemC0,itemC1,itemC2)
			# group attributes
			self.delAttributes(selItem.parent)
			for row in xrange(self.groupAttributes.rowCount()):
				itemC0 = self.groupAttributes.item(row, 0)
				itemC1 = self.groupAttributes.item(row, 1)
				itemC2 = self.groupAttributes.item(row, 2)
				self.saveAttributeFields(selItem.parent,itemC0,itemC1,itemC2)
		#print 'saved'
		self.saveAttributeChangeBtn.setEnabled(False)
		self.restoreAttributesBtn.setEnabled(False)
	#############################################################################
	def delExperimentAttributes(self,sItem):
		for eee in sItem.file.attrs.iterkeys():
			if not eee=='notes':
				sItem.file.attrs.__delitem__(eee)
	#############################################################################
	def delAttributes(self,sItem):
		for eee in sItem.attrs.iterkeys():
			if not eee=='groupNotes':
				sItem.attrs.__delitem__(eee)
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
	def addExperimentRow(self):
		rowExperimentN = self.experimentAttributes.rowCount()
		self.experimentAttributes.insertRow(rowExperimentN)
	#############################################################################
	def removeExperimentAttribute(self):
		treeItem = self.experimentTree.currentItem()
		selItem = treeItem.data(0, Qt.UserRole).toPyObject()
		
		row = self.experimentAttributes.currentItem().row()
		attName = str(self.experimentAttributes.item(row,0).text())
		selItem.file.attrs.__delitem__(attName)
		
		self.toggle_data_selection()
	#############################################################################
	def addGroupRow(self):
		rowGroupN = self.groupAttributes.rowCount()
		self.groupAttributes.insertRow(rowGroupN)
	#############################################################################
	def removeGroupAttribute(self):
		treeItem = self.experimentTree.currentItem()
		selItem = treeItem.data(0, Qt.UserRole).toPyObject()
		
		row = self.groupAttributes.currentItem().row()
		attName = str(self.groupAttributes.item(row,0).text())
		
		if (type(selItem) == h5py._hl.group.Group and not selItem.name == '/'):
			selItem.attrs.__delitem__(attName)
		elif type(selItem) == h5py._hl.dataset.Dataset:
			selItem.parent.attrs.__delitem__(attName)
			
		self.toggle_data_selection()
	#############################################################################
	def addDatasetRow(self):
		rowDatasetN = self.dataSetAttributes.rowCount()
		self.dataSetAttributes.insertRow(rowDatasetN)
	#############################################################################
	def removeDatasetAttribute(self):
		treeItem = self.experimentTree.currentItem()
		selItem = treeItem.data(0, Qt.UserRole).toPyObject()
		
		row = self.dataSetAttributes.currentItem().row()
		attName = str(self.dataSetAttributes.item(row,0).text())
		
		selItem.attrs.__delitem__(attName)
			
		self.toggle_data_selection()
	#############################################################################
	def closeEvent(self, event):
		# save current settings
		h5Settings = {}
		h5Settings['dataDirectory'] = self.dataDirectory
		pickle.dump(h5Settings,open('.h5Settings.p','wb'))
		
		print 'bye'
		self.cleanup_consoles()
		quit()
		event.accept()
		#reply = QMessageBox.question(self, 'Message',
		#"Are you sure to quit?", QMessageBox.Yes | 
		#QMessageBox.No, QMessageBox.No)

		#if reply == QMessageBox.Yes:
		#	self.cleanup_consoles()
		#	quit()
		#	event.accept()
		#	print 'bye'
		#else:
		#	event.ignore()        
		
			
##########################################################
if __name__ == "__main__":
	app = QApplication(sys.argv)
	form = hdf5Viewer()
	form.show()
	form.ipkernel.start()
	app.exec_()
	