#!/usr/bin/python3
import os,sys,shutil
from PySide2.QtWidgets import QApplication,QGridLayout,QWidget,QPushButton,QHeaderView,QLabel,QSpinBox,QTableWidgetItem,QAbstractItemView,QCheckBox,QFrame
from PySide2.QtCore import Qt,Signal,QSize,QThread,QPoint,QObject
from PySide2.QtGui import QIcon,QPixmap,QCursor,QColor,QDrag
from QtExtraWidgets import QTableTouchWidget,QHotkeyButton
import lib.libdock as libdock
import extras.launchers as launchers
import accessdock
import gettext
import resources
_ = gettext.gettext

i18n={"ADD":_("Add"),
	"DCK":_("Rearrange or add new buttons"),
	"DEL":_("Delete"),
	"DOWN":_("Down"),
	"EDI":_("Edit"),
	"HKEY":_("Assign hotkey"),
	"HKEYBTN":_("Push"),
	"MAX":_("Items per row"),
	"STRT":_("Launch at session start"),
	"UP":_("Up")
	}

class dockSignals(QObject):
	changed=Signal()
	itemSelectionChanged=Signal()
#class dockSignals

class dock(accessdock.accessdock):
	def __init__(self):
		super().__init__()
		self.signals=dockSignals()
		self.realTable=None
		self._fakeDock()
		self.fakeTable=QTableTouchWidget()
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
		self.source=None
		self.dest=None
		self.data={}
		self.layout().addWidget(self.fakeTable,0,0,1,1)
		self._cloneDock()
	#def __init__
	
	def _indexToCell(self,idx):
		cc=self.fakeTable.columnCount()
		row,col=divmod(idx,cc)
		return(row,col)
	#def _indexToCell

	def _itemSelectionChanged(self):
		self.signals.itemSelectionChanged.emit()
	#def _itemSelectionChanged

	def _beginDrag(self,*args):
		self.sourceCol=self.fakeTable.currentColumn()
		self.sourceRow=self.fakeTable.currentRow()
	#def _beginDrag

	def _drop(self,*args,**kwargs):
		block=False
		if "idx" in kwargs.keys():
			row,col=self._indexToCell(kwargs.get("idx"))
			self.sourceCol=col
			self.sourceRow=row
			destRow,destCol=self._indexToCell(kwargs.get("toIdx"))
			block=True
		else:
			ev=args[0]
			pos=self.fakeTable.mapFromGlobal(QCursor.pos())
			colW=self.fakeTable.columnWidth(1)
			destCol=int((pos.x()-self.fakeTable.verticalHeader().width())/colW)
			if destCol==self.fakeTable.columnCount():
				destCol-=1
			destRow=int(pos.y()/self.fakeTable.verticalHeader().height())
		self.source=self.fakeTable.takeItem(self.sourceRow,self.sourceCol)
		self.fakeTable.setItem(self.sourceRow,self.sourceCol,None)
		self._rearrangeDock(destRow,destCol,block)
	#def _drop

	def _rearrangeDock(self,destRow,destCol,block=False):
		sourceIdx=self.sourceCol+(self.fakeTable.columnCount()*self.sourceRow)
		cc=self.fakeTable.columnCount()
		destIdx=destCol+(cc*destRow)
		tmpIdx=sourceIdx
		inc=1
		if destIdx<sourceIdx:
			inc=-1
		for i in range(sourceIdx+inc,destIdx+inc,inc):
			row,col=self._indexToCell(i)
			newRow,newCol=self._indexToCell(tmpIdx)
			dest=self.fakeTable.takeItem(row,col)
			self.data[tmpIdx]=dest.data(Qt.UserRole)
			self.fakeTable.setItem(newRow,newCol,None)
			self.fakeTable.setItem(row,col,None)
			self.fakeTable.setItem(newRow,newCol,dest)
			tmpIdx=i
		destRow,destCol=self._indexToCell(destIdx)
		self.fakeTable.setItem(destRow,destCol,self.source)
		self.data[destIdx]=self.source.data(Qt.UserRole)
		if block==False:
			self.signals.changed.emit()
	#def _rearrangeDock

	def _fakeDock(self):
		self.realTable=self.layout().itemAt(0).widget()
		self.realTable.setVisible(False)
	#def _fakeDock

	def _cloneDock(self):
		self.fakeTable.setIconSize(QSize(48,48))	
		self.fakeTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.fakeTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.fakeTable.setRowCount(0)
		self.fakeTable.setRowCount(self.realTable.rowCount())
		self.fakeTable.setColumnCount(0)
		self.fakeTable.setColumnCount(self.realTable.columnCount())
		for i in range(0,self.realTable.rowCount()):
			for j in range(0,self.realTable.columnCount()):
				wdg=self.realTable.cellWidget(i,j)
				if isinstance(wdg,QPushButton):
					icon=wdg.icon()
					item=QTableWidgetItem()
					item.setIcon(icon)
					item.setData(Qt.UserRole,wdg.property("file"))
					self.fakeTable.setItem(i,j,item)
					idx=j+(i*self.fakeTable.columnCount())
					self.data[idx]=wdg.property("file")
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

class accessconf(QWidget):
	def __init__(self,parent=None):
		super().__init__()
		self.dbg=True
		self.launchers=libdock.libdock()

		#self.setWindowModality(Qt.WindowModal)
		#self.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)
		self._initScreen()
		self.threadLaunchers=[]
		self.updateScreen()
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("accessdock: {}".format(msg))
	#def _debug

	def _initScreen(self):
		layout=QGridLayout()
		self.setLayout(layout)
		self._renderDockConfig()
		self._renderOptions()
	#def _initScreen

	def _renderDockConfig(self):
		layout=self.layout()
		frm=QFrame()
		frm.setFrameShape(frm.Box)
		frm.setLayout(QGridLayout())
		layout.addWidget(frm,0,0,1,2)
		layout=frm.layout()
		self.dock=dock()
		self.dock.signals.changed.connect(self._saveChanges)
		self.dock.signals.itemSelectionChanged.connect(self._syncListIdx)
		lbl=QLabel(i18n.get("MAX"))
		lbl.setVisible(False)
		self.max=QSpinBox()
		self.max.setVisible(False)
		self.list=QTableTouchWidget(0,1)
		self.list.itemSelectionChanged.connect(self._syncDockIdx)
		self.list.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.list.horizontalHeader().hide()
		self.list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.list.setSelectionBehavior(self.list.SelectRows)
		self.list.setSelectionMode(self.list.SingleSelection)
		self.list.itemChanged.connect(self._change)
		self.btnIup=QPushButton()
		self.btnIup.setAccessibleName(i18n["UP"])
		self.btnIup.setIcon(QIcon.fromTheme("arrow-up"))
		self.btnIup.setEnabled(False)
		self.btnIup.clicked.connect(self._itemUp)
		self.btnIdo=QPushButton()
		self.btnIdo.setAccessibleName(i18n["UP"])
		self.btnIdo.setIcon(QIcon.fromTheme("arrow-down"))
		self.btnIdo.setEnabled(False)
		self.btnIdo.clicked.connect(self._itemDown)
		self.btnAdd=QPushButton(i18n.get("ADD"))
		self.btnAdd.clicked.connect(self._addAction)
		self.btnDel=QPushButton(i18n.get("DEL"))
		self.btnDel.clicked.connect(self._delAction)
		self.btnDel.setEnabled(False)
		self.btnEdi=QPushButton(i18n.get("EDI"))
		self.btnEdi.clicked.connect(self._ediAction)
		self.btnEdi.setEnabled(False)
		layout.addWidget(QLabel(i18n["DCK"]),0,0,1,4)
		layout.addWidget(self.dock,1,0,1,4)
		layout.addWidget(self.list,2,0,3,2)
		layout.addWidget(self.btnIup,2,2,2,1,Qt.AlignTop|Qt.AlignLeft)
		layout.addWidget(self.btnIdo,4,2,1,1,Qt.AlignBottom|Qt.AlignLeft)
		layout.addWidget(self.btnAdd,2,3,1,1,Qt.AlignTop)
		layout.addWidget(self.btnEdi,3,3,1,1,Qt.AlignTop)
		layout.addWidget(self.btnDel,4,3,1,1,Qt.AlignTop)
	#def _renderDockConfig

	def _renderOptions(self):
		layout=self.layout()
		row=layout.rowCount()
		frm=QFrame()
		frm.setLayout(QGridLayout())
		frm.setFrameShape(frm.HLine)
		layout.addWidget(frm,row,0,1,2)
		self.chkStart=QCheckBox(i18n["STRT"])
		self.chkStart.setChecked(self._chkStartStatus())
		layout.addWidget(self.chkStart,row+1,0,1,2)
		layout.addWidget(QLabel(i18n["HKEY"]),row+2,0,Qt.AlignLeft)
		self.btnHkey=QHotkeyButton(i18n["HKEYBTN"])
		layout.addWidget(self.btnHkey,row+2,0,Qt.AlignRight)
	#def _renderOptions

	def _change(self,*args):
		if args[0].isSelected():
			if len(args[0].text())<3:
				return
			lpath=launchers.launchers().launchersPath
			idx=self.list.currentRow()
			data=self.dock.data
			fpath=os.path.join(lpath,data[idx])
			with open(fpath,"r") as f:
				fcontents=f.read()
			nfcontents=[]
			for l in fcontents.split("\n"):
				nl=l
				if l.replace(" ","").startswith("Name"):
					nl=l.split("=")
					nl[1]=args[0].text()
					nl="=".join(nl)
				nfcontents.append("{}\n".format(nl))
			with open(fpath,"w") as f:
				f.writelines(nfcontents)
	#def _change

	def updateScreen(self):
		self.dock.updateScreen()
		self.dock._cloneDock()
		self.list.clear()
		self.list.setRowCount(0)
		launchers=self.launchers.getLaunchers()
		for launcher in launchers:
			item=QTableWidgetItem()
			item.setText(launcher[1].get("Name",launcher[0]))
			self.list.setRowCount(self.list.rowCount()+1)
			self.list.setItem(self.list.rowCount()-1,self.list.columnCount()-1,item)
		self.chkStart.stateChanged.connect(self._toggleStart)
	#def updateScreen

	def _toggleStart(self):
		dskName="net.lliurex.accessibledock.desktop"
		dskPath=os.path.join(os.environ.get("HOME"),".config","autostart",dskName)
		srcPath=os.path.join("/usr","share","applications",dskName)
		if self._chkStartStatus()==True:
			self._debug("Disable autostart")
			os.unlink(dskPath)
		elif os.path.exists(srcPath):
			if os.path.exists(os.path.dirname(dskPath))==False:
				os.makedirs(os.path.dirname(dskPath))
			self._debug("Enable autostart")
			shutil.copy(srcPath,dskPath)
	#def _toggleStart

	def _chkStartStatus(self):
		status=False
		dskName="net.lliurex.accessibledock.desktop"
		if os.path.exists(os.path.join(os.environ.get("HOME"),".config","autostart",dskName)):
			status=True
		return status
	#def _chkStartStatus

	def _itemUp(self):
		idx=self.list.currentRow()
		newIdx=idx-1
		if newIdx<0:
			return
		i=self.list.takeItem(idx,0)
		ni=self.list.takeItem(newIdx,0)
		self.list.setCurrentItem(self.list.takeItem(newIdx,0))
		self.list.setItem(newIdx,0,i)
		self.list.setItem(idx,0,ni)
		self.list.setCurrentCell(newIdx,0)
		self.dock._drop(idx=idx,toIdx=newIdx)
		self._saveChanges()
		self.dock.setCurrentIndex(newIdx)
	#def _itemUp

	def _itemDown(self):
		idx=self.list.currentRow()
		newIdx=idx+1
		if newIdx>=self.list.rowCount():
			return
		i=self.list.takeItem(idx,0)
		ni=self.list.takeItem(newIdx,0)
		self.list.setCurrentItem(self.list.takeItem(newIdx,0))
		self.list.setItem(newIdx,0,i)
		self.list.setItem(idx,0,ni)
		self.list.setCurrentCell(newIdx,0)
		self.dock._drop(idx=idx,toIdx=newIdx)
		self._saveChanges()
		self.dock.setCurrentIndex(newIdx)
	#def _itemDown

	def _syncListIdx(self,*args):
		self.btnDel.setEnabled(True)
		self.btnEdi.setEnabled(True)
		idx=self.dock.currentIndex()
		self.list.setEnabled(False)
		self.list.setCurrentCell(idx,0)
		self.list.setEnabled(True)
	#def _syncListIdx

	def _syncDockIdx(self,*args):
		idx=self.list.currentRow()
		if self.btnIup.isEnabled()==False and idx>0:
			self.btnIup.setEnabled(True)
		elif idx==0:
			self.btnIup.setEnabled(False)
		if self.btnIdo.isEnabled()==False and idx<self.list.rowCount()-1:
			self.btnIdo.setEnabled(True)
		elif idx>=self.list.rowCount()-1:
			self.btnIdo.setEnabled(False)
		self.dock.setCurrentIndex(idx)
	#def _syncDockIdx

	def _addAction(self,*args):
		launcher=launchers.launchers()
		launcher.accepted.connect(self.updateScreen)
		launcher.destPath=self.launchers.launchersPath
		launcher.show()
	#def _addAction(self,*args):

	def _ediAction(self,*args):
		idx=self.list.currentRow()
		data=self.dock.data
		launcher=launchers.launchers()
		launcher.accepted.connect(self.updateScreen)
		launcher.destPath=self.launchers.launchersPath
		launcher.setParms(data[idx])
		launcher.show()
	#def _addAction(self,*args):

	def _delAction(self,*args):
		idx=self.list.currentRow()
		data=self.dock.data
		fpath=os.path.join(self.launchers.launchersPath,data[idx])
		if os.path.exists(fpath):
			os.remove(fpath)
		self.updateScreen()
	#def _delAction(self,*args):

	def _saveChanges(self,*args):
		lpath=self.launchers.launchersPath
		launchers=self.launchers.getLaunchers()
		new=[]
		for launcher in launchers:
			new.append(launcher[0])
		launchers=self.dock.getLaunchers().items()
		for idx,fname in launchers:
			name=fname.split("_",1)[-1]
			fpath=f"{idx:03d}_{name}"
			for f in new:
				if name in f and fpath!=f:
					sourcef=os.path.join(lpath,f)
					if os.path.exists(sourcef):
						destf=os.path.join(lpath,fpath.replace(" ","_"))
						shutil.move(sourcef,destf)
						self._debug("Move {} -> {}".format(os.path.join(lpath,f),os.path.join(lpath,fpath.replace(" ","_"))))
						break
		self.updateScreen()
	#def _saveChanges
		
app=QApplication(["AccessDock Configuration"])
dock=accessconf()

icon=QIcon(":/icons/accessdock.png")
dock.setWindowIcon(icon)
dock.show()
app.exec_()
