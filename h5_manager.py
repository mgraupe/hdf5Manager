#! python
import os
import sys
from os.path import join, dirname, isdir
import glob
import h5py
import pdb
import time
import numpy as np
import platform
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import Slider, RadioButtons
import re
import pickle
from functools import partial

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
        
        # determine directory separator depending on OS
        if platform.system()=='Windows':
            self.separator = '\\'
        else:
            self.separator = '/'  
        #self.ipk = InternalIPKernel.init_ipkernel('qt')
        #window = create_window(MyQtWindow)
        #curDir = os.getcwd()

        self.dataSetTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.dataSetTree.setColumnWidth(0, 330)
        self.dataSetTree.setColumnWidth(1, 90)
        self.dataSetTree.setColumnWidth(2, 100)
        self.dataSetTree.sortByColumn(0, Qt.AscendingOrder)
        
        self.dataSetTree.header().setResizeMode(0, QHeaderView.Stretch)
        
        self.attributesTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.attributesTree.setColumnWidth(0, 260)
        self.attributesTree.setColumnWidth(1, 160)
        self.attributesTree.setColumnWidth(2, 70)
        self.attributesTree.sortByColumn(0, Qt.DescendingOrder)
        
        self.attributesTree.header().setResizeMode(1, QHeaderView.Stretch)
        
        
        #self.experimentAttributes.setColumnWidth(0, 140)
        #self.experimentAttributes.setColumnWidth(1, 215)
        #self.experimentAttributes.setColumnWidth(2, 60)
        
        #self.groupAttributes.setColumnWidth(0, 140)
        #self.groupAttributes.setColumnWidth(1, 215)
        #self.groupAttributes.setColumnWidth(2, 60)
        
        #self.dataSetAttributes.setColumnWidth(0, 140)
        #self.dataSetAttributes.setColumnWidth(1, 215)
        #self.dataSetAttributes.setColumnWidth(2, 60)
        
        #self.dataSetTree.headerView().resizeSection(0, 100)
        #self.dataSetTree.headerView().resizeSection(1, 40)
        #self.dataSetTree.headerView().resizeSection(2, 40)
        
        if setExits:
            DDir = h5Settings['dataDirectory']
            if os.path.isdir(DDir):
                self.dataDirectory = DDir
                self.fillOutFileList()
        
        #self.saveAttributeChangeBtn.setEnabled(False)
        #self.restoreAttributesBtn.setEnabled(False)
        
        #self.saveNotesBtn.setEnabled(False)
        #self.restoreNotesBtn.setEnabled(False)
        
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
        self.dataSetTree.currentItemChanged.connect(self.toggle_data_selection)
        
        aa = np.arange(2)
        # plot currently active data
        self.plotDataBtn.clicked.connect(partial(self.plot_data,'new'))
        self.addToPlotBtn.clicked.connect(partial(self.plot_data,'add'))
        
        # Attributes
        #self.experimentAttributes.itemChanged.connect(self.attributeChanges) 
        #self.groupAttributes.itemChanged.connect(self.attributeChanges) 
        #self.dataSetAttributes.itemChanged.connect(self.attributeChanges) 
        
        #self.addExpRowBtn.clicked.connect(self.addExperimentRow)
        #self.addGroupRowBtn.clicked.connect(self.addGroupRow)
        #self.addDatasetRowBtn.clicked.connect(self.addDatasetRow)
        
        #self.removeExpAttributeBtn.clicked.connect(self.removeExperimentAttribute)
        #self.removeGroupAttributeBtn.clicked.connect(self.removeGroupAttribute)
        #self.removeDatasetAttributeBtn.clicked.connect(self.removeDatasetAttribute)
        
        #self.saveAttributeChangeBtn.clicked.connect(self.saveAttributes)
        #self.restoreAttributesBtn.clicked.connect(self.toggle_data_selection)
        
        # Notes
        #self.experimentNotesValue.textChanged.connect(self.notesChanges)
        #self.groupNotesValue.textChanged.connect(self.notesChanges)
        
        #self.saveNotesBtn.clicked.connect(self.saveNotes)
        #self.restoreNotesBtn.clicked.connect(self.toggle_data_selection)

        # iPython
        self.launchiPythonBtn.clicked.connect(self.new_qt_console)
        self.sendToConsoleBtn.clicked.connect(self.add_selection_to_console)
        self.plotNameSpaceBtn.clicked.connect(self.print_namespace)

        
    ####################################################
    # load directory with data files
    def load_directory(self):
        
        try:
            DDir = self.dataDirectory
        except (AttributeError, NameError):
            dataDirNew = str(QFileDialog.getExistingDirectory(self, "Select Data Directory","/home/mgraupe/Documents/BTsync/brandon_data/"))
        else:
            dataDirNew = str(QFileDialog.getExistingDirectory(self, "Select Data Directory", DDir))
        #fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        
        if len(dataDirNew)>0:
            #self.dataDirEdit.setText(dataDirNew)
            print dataDirNew
            self.dataDirectory = dataDirNew + self.separator
            self.fillOutFileList() 
        
    ####################################################
    # reload directory with data files
    def reload_directory(self):
        #curDir = os.getcwd()
        #os.chdir(self.dataDirectory)
        #dataFileList = glob.glob("*.hdf5")
        #print 'Data file list'
        #print dataFileList
        
        #for n in range(len(dataFileList)):
        #	ff = h5py.File(dataFileList[n], 'r')
        #	ff.close()
        #self.workingDirectory.setText(self.dataDirectory)
        #os.chdir(curDir)
        
        self.fillOutFileList()
    ####################################################
    # manuel edit of directory field
    def read_edited_directory(self):
        
        self.dataDirectory = str(self.workingDirectory.text())
        # add / if not existing
        if self.dataDirectory and self.dataDirectory[-1] != self.separator:
            self.dataDirectory += self.separator
        if self.dataDirectory:
            self.fillOutFileList()
        
    ####################################################
    #  plot data
    def plot_data(self, howToPlot):
        # obtain currently selected item
        multipleTempItems = self.dataSetTree.selectedItems()
        curItemList = []
        for i in range(len(multipleTempItems)):
            curItemList.append(multipleTempItems[i].data(0, Qt.UserRole).toPyObject()) 
        nSelection = len(multipleTempItems)
        #tempItem = self.dataSetTree.currentItem()
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
        
        
        
        if howToPlot == 'new':
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
            # determine time vector
            if curItemList[0].attrs.__contains__('dt'):
                dt = float(curItemList[0].attrs['dt'])
                tt = np.linspace(0.,(curItemList[0].shape[0]-1)*dt,curItemList[0].shape[0])
            elif curItemList[0].attrs.__contains__('start-end-dt'):
                #[ -1.50000000e+02   2.00000000e+02   1.00000000e-01]
                tstart = float(curItemList[0].attrs['start-end-dt'][0])
                tend = float(curItemList[0].attrs['start-end-dt'][0])
                dt = float(curItemList[0].attrs['start-end-dt'][2])
                tt = np.linspace(tstart,tstart+(curItemList[0].shape[0]-1)*dt,curItemList[0].shape[0])
            else:
                QMessageBox.warning(self, "Warning","Attribute for TimeSeries must have the name 'dt' or 'start-end-dt'!")
                return
                #
            # plot
            if selection  :
                a1i = self.ax1.plot(tt,curItemList[0].value[:,dsSelection],label=dsSelection)
                plt.legend(iter(a1i),dsSelection,loc=1,frameon=False)
            else:
                a1i = self.ax1.plot(tt,curItemList[0].value)
                if (len(curItemList[0].shape)==1):
                    plt.legend(iter(a1i),range(1),loc=1,frameon=False)
                else:
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
            a1i = self.ax1.imshow(curItemList[0].value,cmap='gray',origin='lower',interpolation='none')
            plt.colorbar(a1i)
        # 3D plot
        elif self.ImageStackRadioBtn.isChecked():

            plt.subplots_adjust(left=0.2, bottom=0.25)
            frame = 0
            a1i = self.ax1.imshow(curItemList[0].value[frame,:,:],origin='lower',cmap='gray')
            #a1i = self.ax1.imshow(curItemList[0].value,origin='lower',interpolation='none')
            axcolor = 'lightgoldenrodyellow'
            axframe = plt.axes([0.25, 0.1, 0.65, 0.03], axisbg=axcolor)
            self.sframe = Slider(axframe, 'Frame #', 0, len(curItemList[0].value)-1, valinit=0,valfmt=u'%0.0f')
            # update function for the slider
            def update(val):
                print val
                frame = np.around(self.sframe.val)
                a1i.set_data(curItemList[0].value[frame,:,:])
                #plt.show()
            self.sframe.on_changed(update)
            #
            self.ax1.set_xlabel('pixel')
            self.ax1.set_ylabel('pixel')
                # generic plot
        else:
            if selection:
                a1i = self.ax1.plot(curItemList[0].value[:,dsSelection])
                plt.legend(iter(a1i),dsSelection,loc=1,frameon=False)
            else:
                a1i = self.ax1.plot(curItemList[0].value)
                if nSelection>1:
                    plt.legend(iter(a1i),list(range(curItemList[0].shape[1])),loc=1,frameon=False)
                else:
                    plt.legend(iter(a1i),list(curItemList[0]),loc=1,frameon=False)
                
        if howToPlot == 'new':
            self.ax1.spines['top'].set_visible(False)
            self.ax1.spines['right'].set_visible(False)
            self.ax1.spines['bottom'].set_position(('outward', 10))
            self.ax1.spines['left'].set_position(('outward', 10))
            self.ax1.yaxis.set_ticks_position('left')
            self.ax1.xaxis.set_ticks_position('bottom')
                
        try:
            plt.show()
        except AttributeError:
            pass
    ####################################################
    def fillOutFileList(self):
        # clear current list
        self.dataSetTree.clear()
        
        curDir = os.getcwd()
        os.chdir(self.dataDirectory)
        dataFileList = glob.glob('*.hdf5')
        dataFileList += glob.glob('*.h5')
        dataFileList += glob.glob('*.ma')
        #print self.dataDirectory
        #print 'Data file list'
        #print dataFileList
        
        for n in range(len(dataFileList)):
            #print dataFileList[n]
            ff = h5py.File(dataFileList[n], 'r')
            topnode = QTreeWidgetItem([ff.filename])
            f = QFont()
            f.setBold(True)
            topnode.setFont(0,f)
            root = ff["/"]
            topnode.setData(0, Qt.UserRole, root)
            topnode.setData(1, Qt.DisplayRole, str(os.path.getsize(self.dataDirectory+root.file.filename)))
            topnode.setTextAlignment (1, Qt.AlignRight)
            topnode.setTextAlignment (2, Qt.AlignLeft)
            for i in range(3):
                topnode.setBackground( i , QColor(208, 230, 255) )
            
            #
            try:
                groupN = 0
                def recursivePopulateTree(parent_node, data,groupN):
                    tree_node = QTreeWidgetItem([data.name])
                    tree_node.setData(0, Qt.UserRole, data)
                    if type(data) == h5py._hl.group.Group:
                        #tree_node.setData(1, Qt.DisplayRole, str(len(data.keys())))
                        try:
                            lab = data.attrs['type']
                        except KeyError:
                            pass
                        else:
                            tree_node.setData(2, Qt.DisplayRole, str(lab))
                            #f.setBold(True)
                            tree_node.setFont(2,f)
                        tree_node.setFont(0,f)
                        col = ((180+groupN*20), 255, (184+groupN*20))
                        for i in range(3):
                            tree_node.setBackground( i , QColor(col[0], col[1], col[2]) )
                        groupN+=1
                    elif type(data) == h5py._hl.dataset.Dataset:
                        tree_node.setData(1, Qt.DisplayRole, str(data.shape))
                        tree_node.setData(2, Qt.DisplayRole, str(data.dtype))
                    tree_node.setTextAlignment (1, Qt.AlignRight)
                    tree_node.setTextAlignment (2, Qt.AlignLeft)
                    parent_node.addChild(tree_node)
                    if type(data) == h5py._hl.group.Group:
                        for item in data.itervalues():
                            recursivePopulateTree(tree_node, item, groupN)
                # add root
                try:
                    lab = root.file.attrs['type']
                except KeyError:
                    pass
                else:
                    topnode.setData(2, Qt.DisplayRole, str(lab))
                #
                self.dataSetTree.addTopLevelItem(topnode)
                for item in root.itervalues():
                    recursivePopulateTree(topnode, item, groupN)
            # show file name in red in case error occurs during hdf5 file parsing
            except (AttributeError, RuntimeError):
                textcolor = QColor("red")
                topnode.setTextColor(0,textcolor)
                topnode.setTextColor(1,textcolor)
                topnode.setTextColor(2,textcolor)
                topnode.setData(2, Qt.DisplayRole, str("Problem in HDF5 format"))
                self.dataSetTree.addTopLevelItem(topnode)
                
        #self.dataSetTree.setHeaderLabel(0,self.dataDirectory)
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
        
        treeItem = self.dataSetTree.currentItem()
        
        try:
            item = treeItem.data(0, Qt.UserRole).toPyObject()
        except AttributeError:
            pass
        else:
            self.currentSelectionValue.setText(item.file.filename+str(item.name))
            self.attributesTree.clear()
            def recursivePopulateAttributeTree(parent_node, att, col):
                tree_node = QTreeWidgetItem([att[0]])
                #tree_node.setFlags(Qt.ItemIsEnabled)
                #tree_node.setFlags(Qt.ItemIsEditable)
                tree_node.setData(0, Qt.UserRole, att[0])
                tree_node.setData(1, Qt.DisplayRole, str(att[1]))
                tree_node.setData(2, Qt.DisplayRole, (str(att[1].dtype) if type(att[1])!= str else str('str') ) )
                for i in range(3):
                    tree_node.setBackground( i , QColor(col[0], col[1], col[2]) )
                parent_node.addChild(tree_node)
            # add root
            topnode = QTreeWidgetItem([item.file.filename])
            f = QFont()
            f.setBold(True)
            topnode.setFont(0,f)
            if type(item) ==  h5py._hl.dataset.Dataset:
                root = item.parent["/"]
            else:
                root = item["/"]
            topnode.setData(0, Qt.UserRole, root)
                        #
            for i in range(3):
                topnode.setBackground( i , QColor(208, 230, 255) )
            self.attributesTree.addTopLevelItem(topnode)
            #self.dataSetTree.addTopLevelItem(1,'1')
            for att in root.attrs.iteritems():
                #print att[0], att[1]
                recursivePopulateAttributeTree(topnode,att,(208, 230,255))
                # determine dept of selected item in terms of subdirectories
                selItem = {}
                levelN = 0
                selItem[levelN] = item
                while ((type(selItem[levelN]) == h5py._hl.dataset.Dataset or type(selItem[levelN]) == h5py._hl.group.Group) and not selItem[levelN].name == '/'):
                    selItem[levelN+1] = selItem[levelN].parent
                    levelN+=1
                # fill out 
                parent_node = topnode
                for i in range(1,levelN+1):
                    tree_node = QTreeWidgetItem([selItem[levelN-i].name])
                    tree_node.setData(0, Qt.UserRole, selItem[levelN-i])
                    tree_node.setFont(0,f)
                    #stree_node.setData(1, Qt.DisplayRole, str(selItem[levelN-i].dtype))
                    if type(selItem[levelN-i]) == h5py._hl.dataset.Dataset :
                            col = (255,255,255)
                    elif type(selItem[levelN-i]) == h5py._hl.group.Group :
                            col = ((180+(i-1)*20), 255, (184+(i-1)*20))   
                    for n in range(3):
                            tree_node.setBackground( n , QColor(col[0], col[1], col[2]) )
                    parent_node.addChild(tree_node)
                    #tree_node.setData(1, Qt.DisplayRole, str(selItem[levelN-i].dtype))
                    for att in selItem[levelN-i].attrs.iteritems():
                            recursivePopulateAttributeTree(tree_node,att,col)
                    #
                    #tree_node = QTreeWidgetItem([selItem[levelN-i].name])
                    #tree_node.setData(0, Qt.UserRole, selItem[topnode-i])
                    #tree_node.setData(1, Qt.DisplayRole, str(data.shape))
                    parent_node = tree_node
                
                self.attributesTree.expandAll()
                #item.parent
            #for item in root.itervalues():
            #	recursivePopulateTree(topnode, item,groupN)
                        
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
        treeItem = self.dataSetTree.currentItem()
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
        treeItem = self.dataSetTree.currentItem()
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
        treeItem = self.dataSetTree.currentItem()
        item = treeItem.data(0, Qt.UserRole).toPyObject()
        self.addData(item.value)
    #############################################################################
    def addExperimentRow(self):
        rowExperimentN = self.experimentAttributes.rowCount()
        self.experimentAttributes.insertRow(rowExperimentN)
    #############################################################################
    def removeExperimentAttribute(self):
        treeItem = self.dataSetTree.currentItem()
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
        treeItem = self.dataSetTree.currentItem()
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
        treeItem = self.dataSetTree.currentItem()
        selItem = treeItem.data(0, Qt.UserRole).toPyObject()
        
        row = self.dataSetAttributes.currentItem().row()
        attName = str(self.dataSetAttributes.item(row,0).text())
        
        selItem.attrs.__delitem__(attName)
            
        self.toggle_data_selection()
    #############################################################################
    def closeEvent(self, event):
        # save current settings
        try:
            self.dataDirectory
        except AttributeError:
            pass
        else:
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
