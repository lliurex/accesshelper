#!/usr/bin/python3
import dbus
import accessdock
from PySide2.QtWidgets import QAbstractItemView,QHeaderView,QGridLayout,QWidget,QTableWidgetItem,QWidgetItem
from PySide2.QtCore import Qt,Signal,QSize,QObject
from PySide2.QtGui import QIcon,QCursor
from QtExtraWidgets import QTableTouchWidget,QHotkeyButton,QFlowTouchWidget

class dockSignals(QObject):
	changed=Signal()
	itemSelectionChanged=Signal()
#class dockSignals

class dock(accessdock.accessdock):
	def __init__(self):
		super().__init__()
		self.dbg=True
		self.signals=dockSignals()
		self.realTable=None
		self.updateLabel=False
		self.fakeTable=QTableTouchWidget()
		self.fakeTable.setEditTriggers(QAbstractItemView.NoEditTriggers) 
		self.fakeTable.verticalHeader().hide()
		self.fakeTable.setDragEnabled(True)
		self.fakeTable.setAcceptDrops(True)
		self.fakeTable.viewport().setAcceptDrops(True)
		self.fakeTable.setDragDropOverwriteMode(True)
		self.fakeTable.setDropIndicatorShown(True)
		self.fakeTable.setDragDropMode(QAbstractItemView.InternalMove)   
		self.fakeTable.cellPressed.connect(self._beginDrag)
		self.fakeTable.itemSelectionChanged.connect(self._itemSelectionChanged)
		self.fakeTable.dropEvent=self._drop
		self.data={}
		wdg=QWidget()
		self.setCentralWidget(wdg)
		lay=QGridLayout(wdg)
		lay.addWidget(self.fakeTable)
		lay.addWidget(self.fakeTable,0,0,1,1)
		self._fakeDock()
		self._cloneDock()
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("dock: {}".format(msg))
	#def _debug

	def _fakeDock(self):
		self.realTable=self.flow
		self.realTable.blockSignals(True)
		self.realTable.setVisible(False)
	#def _fakeDock
	
	def _indexToCell(self,idx):
		self._debug("Getting coords for IDX {}".format(idx))
		cc=self.fakeTable.columnCount()
		self._debug("Columns: {}".format(cc))
		row,col=divmod(idx,cc)
		return(row,col)
	#def _indexToCell

	def _itemSelectionChanged(self):
		self.signals.itemSelectionChanged.emit()
	#def _itemSelectionChanged

	def _beginDrag(self,*args):
		self.sourceCol=self.fakeTable.currentColumn()
		self.sourceRow=self.fakeTable.currentRow()
		self._debug("Begint at {} {}".format(self.sourceRow,self.sourceCol))
	#def _beginDrag

	def _drop(self,*args,**kwargs):
		block=False
		self._debug("Drop Kwargs: {}".format(kwargs))
		if "idx" in kwargs.keys():
			row,col=self._indexToCell(kwargs.get("idx"))
			sourceCol=col
			sourceRow=row
			self._debug("SOURCE C: {}".format(sourceCol))
			self._debug("SOURCE R: {}".format(sourceRow))
			destRow,destCol=self._indexToCell(kwargs.get("toIdx"))
			self._debug("DEST C: {}".format(destCol))
			self._debug("DEST R: {}".format(destRow))
			block=True
		else:
			ev=args[0]
			pos=self.fakeTable.mapFromGlobal(QCursor.pos())
			colW=self.fakeTable.columnWidth(1)
			destCol=int((pos.x()-self.fakeTable.verticalHeader().width())/colW)
			if destCol==self.fakeTable.columnCount():
				destCol-=1
			destRow=int(pos.y()/self.fakeTable.verticalHeader().height())
			sourceCol=self.sourceCol
			sourceRow=self.sourceRow
		self._rearrangeDock(sourceRow,sourceCol,destRow,destCol,block)
	#def _drop

	def _rearrangeDock(self,sourceRow,sourceCol,destRow,destCol,block=False):
		sourceIdx=sourceCol+((self.fakeTable.columnCount())*sourceRow)
		self._debug("SOURCE IDX: {}".format(sourceIdx))
		cc=self.fakeTable.columnCount()
		destIdx=destCol+(cc*destRow)
		self._debug("DEST IDX: {}".format(destIdx))
		inc=1
		if destIdx<sourceIdx:
			inc=-1
		self._debug("MOVE FROM {} TO {} INC {}".format(sourceIdx,destIdx,inc))
		for currentIdx in range(sourceIdx+inc,destIdx+inc,inc):
			crow,ccol=self._indexToCell(currentIdx)
			orow,ocol=self._indexToCell(sourceIdx)
			source=self.fakeTable.takeItem(orow,ocol)
			self._debug("From Coords {} {}".format(orow,ocol))
			if source==None:
				continue
			self._debug("To Coords {} {}".format(crow,ccol))
			dest=self.fakeTable.takeItem(crow,ccol)
			if dest==None:
				continue
			self.fakeTable.setItem(crow,ccol,source)
			self.data[currentIdx]=source.data(Qt.UserRole)
			self._debug("{},{} -> {}".format(crow,ccol,source.data(Qt.UserRole)))
			self.fakeTable.setItem(orow,ocol,dest)
			self.data[sourceIdx]=dest.data(Qt.UserRole)
			self._debug("{},{} -> {}".format(orow,ocol,dest.data(Qt.UserRole)))
			sourceIdx=currentIdx
		destRow,destCol=self._indexToCell(destIdx)
		if block==False:
			self.signals.changed.emit()
	#def _rearrangeDock

	def _cloneDock(self):
		self.fakeTable.setIconSize(QSize(48,48))	
		self.fakeTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.fakeTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.fakeTable.setRowCount(0)
		self.fakeTable.setRowCount(1)
		self.fakeTable.setColumnCount(0)
		self.fakeTable.setColumnCount(self.realTable.count())
		print("O")
		for i in range(0,self.realTable.count()):
			item=self.realTable.itemAt(i)
			print(item)
			if isinstance(item,QWidgetItem):
				wdg=item.widget()
				if isinstance(wdg,accessdock.QPushButtonDock):
					icon=wdg.icon()
					item=QTableWidgetItem()
					item.setIcon(icon)
					#item.setData(Qt.UserRole,wdg.property("file"))
					item.setData(Qt.UserRole,wdg.property("fpath"))
					self.fakeTable.setItem(0,i,item)
					#self.data[idx]=wdg.property("file")
					self.data[i]=wdg.property("fpath")
					self._debug("Item for {}".format(i))
		print("O")
	#def _cloneDock

	def getLaunchers(self):
		return(self.data)
	#def getLaunchers

	def currentIndex(self):
		return(self.fakeTable.currentColumn()+(self.fakeTable.currentRow()*self.fakeTable.columnCount()))
	#def currentIndex

	def setCurrentIndex(self,idx):
		cc=self.fakeTable.columnCount()
		destRow,destCol=divmod(idx,cc)
		self.fakeTable.setCurrentCell(destRow,destCol)
	#def setCurrentIndex
		
#class dock

