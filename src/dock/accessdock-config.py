#!/usr/bin/python3
import dbus
import os,sys,shutil,time
import notify2
from PySide6.QtWidgets import QApplication,QGridLayout,QWidget,QPushButton,QHeaderView,QLabel,QSpinBox,QWidgetItem,QTableWidgetItem,QAbstractItemView,QCheckBox,QFrame,QHBoxLayout,QVBoxLayout,QMessageBox
from PySide6.QtCore import Qt,Signal,QSize,QObject
from PySide6.QtGui import QIcon,QCursor,QGuiApplication
from QtExtraWidgets import QTableTouchWidget,QHotkeyButton
import lib.libdock as libdock
import lib.launchers as launchers
import accessdock
import gettext
import resources
gettext.textdomain('accesswizard')
_ = gettext.gettext

i18n={"ADD":_("Add"),
	"BTNDEF":_("Default apps"),
	"DCK":_("Rearrange or modify buttons for the dock"),
	"DEF":_("This will delete all contents"),
	"DEL":_("Delete"),
	"DOWN":_("Down"),
	"EDI":_("Edit"),
	"HKEY":_("Keyboard shortcut"),
	"HKEYBTN":_("Push to assign"),
	"HKEYERR":_("already assigned"),
	"MAX":_("Items per row"),
	"STRT":_("Launch at session start"),
	"TOOLTIPBIG":_("Displays launcher name at fullscreen on mouse over"),
	"UP":_("Up")
	}

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
		self._fakeDock()
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
		self.layout().addWidget(self.fakeTable,0,0,1,1)
		self._cloneDock()
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("dock: {}".format(msg))
	
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

	def _fakeDock(self):
		self.realTable=self.layout().itemAt(0).widget()
		self.realTable.setVisible(False)
	#def _fakeDock

	def _cloneDock(self):
		self.fakeTable.setIconSize(QSize(48,48))	
		self.fakeTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.fakeTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.fakeTable.setRowCount(0)
		self.fakeTable.setRowCount(1)
		self.fakeTable.setColumnCount(0)
		self.fakeTable.setColumnCount(self.realTable.count())
		for i in range(0,self.realTable.count()):
			item=self.realTable.itemAt(i)
			wdg=None
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
		self.libdock=libdock.libdock()
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
		self._renderGui()
	#def _initScreen

	def _defLaunchersList(self):
		wdg=QTableTouchWidget(0,1)
		wdg.setEditTriggers(QAbstractItemView.NoEditTriggers) 
		wdg.itemSelectionChanged.connect(self._syncDockIdx)
		wdg.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		wdg.horizontalHeader().hide()
		wdg.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		#self.list.setSelectionBehavior(self.list.SelectRows)
		#self.list.setSelectionMode(self.list.SingleSelection)
		wdg.itemChanged.connect(self._change)
		return(wdg)
	#def _defLaunchersList

	def _defScrlList(self):
		wdg=QWidget()
		lay=QVBoxLayout(wdg)
		self.btnIup=QPushButton()
		self.btnIup.setAccessibleName(i18n["UP"])
		self.btnIup.setIcon(QIcon.fromTheme("arrow-up"))
		self.btnIup.setEnabled(False)
		self.btnIup.clicked.connect(self._itemUp)
		lay.addWidget(self.btnIup,Qt.AlignTop)
		self.btnIdo=QPushButton()
		self.btnIdo.setAccessibleName(i18n["UP"])
		self.btnIdo.setIcon(QIcon.fromTheme("arrow-down"))
		self.btnIdo.setEnabled(False)
		self.btnIdo.clicked.connect(self._itemDown)
		lay.addWidget(self.btnIdo,Qt.AlignBottom)
		return(wdg)
	#def _defScrlList

	def _defButtonsEdit(self):
		wdg=QWidget()
		lay=QVBoxLayout(wdg)
		btnDef=QPushButton(i18n.get("BTNDEF"))
		btnDef.clicked.connect(self._defAction)
		lay.addWidget(btnDef)
		btnAdd=QPushButton(i18n.get("ADD"))
		btnAdd.clicked.connect(self._addAction)
		lay.addWidget(btnAdd)
		self.btnDel=QPushButton(i18n.get("DEL"))
		self.btnDel.clicked.connect(self._delAction)
		self.btnDel.setEnabled(False)
		lay.addWidget(self.btnDel)
		self.btnEdi=QPushButton(i18n.get("EDI"))
		self.btnEdi.clicked.connect(self._ediAction)
		self.btnEdi.setEnabled(False)
		lay.addWidget(self.btnEdi)
		return(wdg)
	#def _defButtonsEdit

	def _defOptions(self):
		frm=QFrame()
		frm.setFrameShape(QFrame.HLine)
		frm.setLayout(QGridLayout())
		tlayout=frm.layout()
		self.chkStart=QCheckBox(i18n["STRT"])
		self.chkStart.setChecked(self._chkStartStatus())
		self.chkStart.stateChanged.connect(self._toggleStart)
		tlayout.addWidget(self.chkStart,0,0,1,2)
		self.chkToolT=QCheckBox(i18n["TOOLTIPBIG"])
		self.chkToolT.stateChanged.connect(self._toggleToolT)
		tlayout.addWidget(self.chkToolT,1,0,1,1)
		wdg=QWidget()
		hlay=QHBoxLayout()
		wdg.setLayout(hlay)
		hlay.addWidget(QLabel(i18n["HKEY"]),Qt.AlignLeft)
		btnHkeyText=self.libdock.getShortcut()
		if len(btnHkeyText.strip())>0:
			btnHkeyText=btnHkeyText.split(",")[0]
			self.btnHkey=QHotkeyButton(btnHkeyText)
		else:
			self.btnHkey=QHotkeyButton(i18n["HKEYBTN"])
		self.btnHkey.hotkeyAssigned.connect(self._assignHotkey)
		hlay.addWidget(self.btnHkey,Qt.AlignLeft)
		tlayout.addWidget(wdg,2,0,1,1,Qt.AlignLeft)
		return(frm)
	#def _defOptions

	def _renderGui(self):
		layout=self.layout()
		frm=QFrame()
		frm.setFrameShape(QFrame.Box)
		frm.setLayout(QGridLayout())
		layout.addWidget(frm,0,0,1,2)
		tlayout=frm.layout()
		self.dock=dock()
		self.dock.signals.changed.connect(self._saveChanges)
		self.dock.signals.itemSelectionChanged.connect(self._syncListIdx)
		lbl=QLabel(i18n.get("MAX"))
		lbl.setVisible(False)
		self.max=QSpinBox()
		self.max.setVisible(False)
		self.list=self._defLaunchersList()
		scrList=self._defScrlList()
		btnsEdit=self._defButtonsEdit()
		tlayout.addWidget(QLabel(i18n["DCK"]),0,0,1,3)
		tlayout.addWidget(self.dock,1,0,1,3)
		tlayout.addWidget(self.list,2,0,1,1)
		tlayout.addWidget(scrList,2,1,1,1)
		tlayout.addWidget(btnsEdit,2,2,1,1)
		options=self._defOptions()
		layout.addWidget(options,1,0,1,1)
	#def _renderGui

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

	def _assignHotkey(self,hkAction):
		hkey=hkAction.get("hotkey","")
		hkey=hkey.replace("Any","Space")
		haction=hkAction.get("action","")
		reserved=["ctrl+x","ctrl+z","ctrl+c","ctrl+p","ctrl+b","ctrl+a","ctrl+e","ctrl+u","ctrl+y","ctrl+d","ctrl+v","return"]
		if haction!="" or hkey.lower() in reserved:
			notify2.init("AccessDock")
			notification=notify2.Notification("{}".format(hkey),i18n["HKEYERR"].capitalize())
			notification.show()
			self.btnHkey.revertHotkey()
		else:
			self.libdock.setShortcut(hkey)
			self.btnHkey.seq=[]
		self.list.setFocus()
		time.sleep(0.1)
	#def _assignHotkey

	def updateScreen(self):
		self.dock.updateScreen()
		self.dock._cloneDock()
		self.list.clear()
		self.list.setRowCount(0)
		launchers=self.libdock.getLaunchers()
		for launcher in launchers:
			item=QTableWidgetItem()
			name=launcher[1].get("Name",launcher[0])
			desc=launcher[1].get("Comment","")
			if len(desc)>0:
				item.setToolTip(desc)
			item.setText(name)
			self.list.setRowCount(self.list.rowCount()+1)
			self.list.setItem(self.list.rowCount()-1,self.list.columnCount()-1,item)
		self.chkStart.setChecked(self._chkStartStatus())
		self.chkToolT.setChecked(self._chkToolTStatus())
	#def updateScreen

	def _toggleToolT(self):
		self.libdock.writeKValue("kwinrc","accessibledock","tooltipbig",str(self.chkToolT.isChecked()).lower())
	#def _toggleToolT

	def _chkToolTStatus(self):
		if self.libdock.readKValue("kwinrc","accessibledock","tooltipbig")=="true":
			return True
		return False
	#def _chkToolTStatus

	def _toggleStart(self):
		return (self.libdock.setDockEnabled(self.chkStart.isChecked()))
	#def _toggleStart

	def _chkStartStatus(self):
		return (self.libdock.getDockEnabled())
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
		launcher.destPath=self.libdock.launchersPath
		launcher.show()
	#def _addAction(self,*args):

	def _defAction(self,*args):
		dlg=QMessageBox()
		dlg.addButton(QMessageBox.Ok)
		dlg.addButton(QMessageBox.Cancel)
		dlg.setText(i18n.get("DEF"))
		if dlg.exec()==QMessageBox.Ok:
			self.list.clear()
			self.libdock.initLaunchers()
			self.updateScreen()
	#def _defAction(self,*args):

	def _ediAction(self,*args):
		idx=self.list.currentRow()
		data=self.dock.data
		launcher=launchers.launchers()
		launcher.accepted.connect(self.updateScreen)
		launcher.destPath=self.libdock.launchersPath
		launcher.setParms(data[idx])
		launcher.show()
	#def _ediAction(self,*args):

	def _delAction(self,*args):
		idx=self.list.currentRow()
		data=self.dock.data
		fpath=os.path.join(self.libdock.launchersPath,data[idx])
		if os.path.exists(fpath):
			os.remove(fpath)
		self.updateScreen()
	#def _delAction(self,*args):

	def _saveChanges(self,*args):
		lpath=self.libdock.launchersPath
		launchers=self.libdock.getLaunchers()
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

	def closeEvent(self,*args):
		bus=dbus.SessionBus()
		try:
			objbus=bus.get_object("net.lliurex.accessibledock","/net/lliurex/accessibledock")
			objint=dbus.Interface(bus,"net.lliurex.accessibledock")
			objbus.toggle()
			objbus.toggle()
		except:
			print("e")
			pass
		finally:
			sys.exit(0)
	#def closeEvent
		
app=QApplication(["AccessDock Configuration"])
dock=accessconf()

icon=QIcon(":/icons/accessdock.png")
dock.setWindowIcon(icon)
dock.setMinimumWidth(1000)
dock.setMinimumHeight(600)
QGuiApplication.setDesktopFileName("accessdock")
dock.show()
app.exec()
