#!/usr/bin/python3
import os,sys,subprocess,json
from PySide2.QtWidgets import QApplication,QGridLayout,QWidget,QPushButton,QHeaderView,QMenu,QAction,QToolTip,QLabel,QDesktopWidget
from PySide2.QtCore import Qt,QSignalMapper,QSize,QThread,QPoint,QEvent,Signal,QObject,QRect
from PySide2.QtGui import QIcon,QPixmap,QCursor,QColor,QPalette,QGuiApplication
import dbus
import dbus.service
import dbus.mainloop.glib
from QtExtraWidgets import QTableTouchWidget,QScrollLabel
import subprocess
import lib.libdock as libdock
import gettext
import resources
gettext.textdomain('accesswizard')
_ = gettext.gettext

i18n={"CONFBTN":_("Configure launcher"),
	"CONFDOCK":_("Configure dock"),
	"CONFIGURE":_("Configure"),
	"TOGGLE":_("Toggle visibility")
	}

class dbusMethods(dbus.service.Object):
	"""DBus service that fires \"toggleVisible\" signal on demand"""
	def __init__(self,bus_name,*args,**kwargs):
		super().__init__(bus_name,"/net/lliurex/accessibledock")
		self.widget=args[0]
	#def __init__(self,bus_name,*args,**kwargs):

	@dbus.service.signal("net.lliurex.accessibledock")
	def toggleVisible(self):
		pass
	#def toggleVisible(self)

	@dbus.service.method("net.lliurex.accessibledock")
	def toggle(self):
		"""Calling this method fires up the signal."""
		self.toggleVisible()
	#def toggle

	@dbus.service.method("net.lliurex.accessibledock", in_signature='', out_signature='as')
	def getLaunchers(self):
		dock=libdock.libdock()
		dbusList = dbus.Array()
		for launcher in dock.getLaunchers():
			name,data=launcher
			dbusList.append(json.dumps(launcher))
		return(dbusList)
		"""Calling this method fires up the signal."""
	#def toggle

	@dbus.service.method("net.lliurex.accessibledock", in_signature='', out_signature='b')
	def isVisible(self):
		return(self.widget.isVisible())
	#def toggle
#class dbusMethods

class threadLauncher(QThread):
	"""QThread based subprocess launcher
		...
		Parameters:
			cmd: str
				Command to launch"""
	def __init__(self,cmd,parent=None):
		super().__init__()
		self.cmd=cmd
	#def __init__

	def run(self):
		try:
			subprocess.run(self.cmd.split())
		except Exception as e:
			print("Err launching {0}:\nFailed cmd: {1}".format(e,self.cmd))
		return(True)
	#def run
#class threadLauncher

class QToolTipDock(QLabel):
	"""Custom tooltip for dock buttons

		Parameters
		----------
			text: str
				tooltip text

		Methods
		-------
			toggle: Calling this shows/hide the tooltip

			Parameters
			----------
				coords: QPoint whith x/y coordenates
	"""
	def __init__(self,text="",bigTip=False,parent=None):
		super().__init__()
		self.setWindowFlags(Qt.X11BypassWindowManagerHint|Qt.BypassWindowManagerHint|Qt.FramelessWindowHint|Qt.WindowTransparentForInput|Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint)
		self.setText(text)
		self.setAccessibleName(text)
		self.setAccessibleDescription("")
		self.setAlignment(Qt.AlignCenter)
		f=self.font()
		f.setWeight(f.Bold)
		f.setPointSize(f.pointSize()+2)
		self.setFont(f)
		scr=QApplication.screens()[0]
		newSize=scr.size().width()/(len(self.text()))
		f.setPointSize(newSize-10)
		self.fontFull=f
		self.bigTip=bigTip
		self.setStyleSheet("border: 1px solid black;")
	#def __init__

	def _getCoordsForFull(self,oldCoords):
		scr=QApplication.screens()[0]
		h=scr.size().height()
		portion=int(h/6)-1
		zone=int(oldCoords.y()/portion)
		if self.bigTip==True:
			f=self.font()
			newSize=portion-10
			f.setPointSize(newSize)
			self.setFont(f)
			zoneInc=2
			zoneBorder=3
		else:
			zoneInc=1
			zoneBorder=5
		coordX=int(scr.size().width()/2)-int(len(self.text())*self.font().pointSize()/2)
		if zone<zoneBorder:
			coordY=portion*(zone+zoneInc)
		else:
			coordY=portion*(zone-zoneInc)
		return(QPoint(coordX,coordY))
	#def _getCoordsForFull

	def toggle(self,coords):
		if self.isVisible():
			self.setVisible(False)
		else:
			if self.bigTip==True:
				self.setFont(self.fontFull)
				coords=self._getCoordsForFull(coords)
			else:
				cursor=self.cursor()
				coords=cursor.pos()
			self.setMinimumWidth(len(self.text())*self.font().pointSize())
			(x,y)=(coords.x(),coords.y())
			scr=QApplication.screens()[0]
			if coords.x()+(len(self.text())*self.font().pointSize())>scr.size().width():
				w=scr.size().width()
				x=w-(len(self.text())*self.font().pointSize())
			if (coords.y()+self.height())>scr.size().height():
				h=scr.size().height()
				y=h-self.height()
			self.move(x,y)
			self.setVisible(True)
	#def toggle
#class QToolTipDock
	
class QPushButtonDock(QPushButton):
	"""A dock button
		
		Parameters
		----------
			launcher: Data
				Desktop info associated with this button as returned by libdock

		Attributes
		----------
			name: str
				Launcher name
			data: dict
				Launcher data
			file: str
				Path to the file on disk
			path: str
				Relative path to the file
			fpath: str
				Path to the file processed with app2menu
			initialSize: QSize
				Initial button size
			mnu: QMenu
				Contextual menu
			lbl: QToolTipDock
				Custom fake tooltip 
			threadLaunchers: List
				List with launched threads

		Signals
		-------
			configure: -> QObject (self)
				Configure option clicked
			configureLauncher: -> QObject (self)
				ConfigureLauncher option clicked
			configureMain:
				ConfigureMain option clicked
			focusIn: -> QObject (self)
				Focus entered
	"""
	configure=Signal(QObject)
	configureLauncher=Signal(QObject)
	focusIn=Signal(QObject)
	toggle=Signal()
	configureMain=Signal()
	def __init__(self,launcher,bigTip=False,parent=None):
		super().__init__()
		layout=QGridLayout()
		self.setLayout(layout)
		self.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint)
		#self.setWindowFlags(Qt.BypassWindowManagerHint)
		self.name,self.data=launcher
		self.setProperty("file",self.data.get("File",""))
		self.setProperty("path",self.data.get("Path",""))
		self.setProperty("fpath",self.data.get("fpath",""))
		self.installEventFilter(self)
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.initialSize=QSize(72,72)
		self.mnu=self._addContextMenu()
		self.customContextMenuRequested.connect(self._popup)
		self.lbl=QToolTipDock(self.data.get("Name"),bigTip)
		self.lbl.setAccessibleName(self.data.get("Name"))
		self.lbl.setVisible(False)
		#layout.addWidget(self.lbl,0,0)
		self.threadLaunchers=[]
		self.popupShow=False
		self.dock=parent
		self._renderBtn()
		self.clicked.connect(self._beginLaunch)
	#def __init__(self,text="",parent=None):

	def _renderBtn(self):
		self.setFixedSize(self.initialSize)
		icn=QIcon()
		iconName=self.data.get("Icon","")
		if len(iconName)==0:
			iconName="accessibledock"
		if os.path.exists(iconName):
			pxm=QPixmap(iconName)
			icn=QIcon(pxm)
		else:
			icn=QIcon.fromTheme(iconName)
		self.setAccessibleName(self.data["Name"])
		self.setIcon(icn)
		self.setIconSize(QSize(64,64))
		self.setFixedSize(QSize(72,72))
	#def _renderBtn

	def _beginLaunch(self,*args):
		cmd=self.data.get("Exec","")
		if len(cmd)>0:
			self.setEnabled(False)
			self.dock.setVisible(False)
			l=threadLauncher(cmd)
			l.start()
			l.finished.connect(self._endLaunch)
			self.threadLaunchers.append(l)
	#def _beginLaunch

	def _endLaunch(self,*args):
		self.dock.setVisible(True)
		if self.isEnabled()==False:
			self.setEnabled(True)
		else:
			self.configure.emit(self)
	#def _endLaunch

	def _toggle(self,*Args,**kwargs):
		self.toggle.emit()
	#def _toggle

	def _launchConfigBtn(self,*args,**kwargs):
		path=self.property("fpath")
		if len(path)>0:
			self.configureLauncher.emit(self)
			if path.endswith(".desktop"):
				path=self.property("fpath")
				cmd="python3 {0} {1}".format(os.path.join(os.path.dirname(os.path.abspath(__file__)),"lib/launchers.py"),path)
				l=threadLauncher(cmd)
				self.threadLaunchers.append(l)
				l.start()
				l.finished.connect(self._endLaunch)
			#	subprocess.run(cmd)
	#def _launchConfigBtn

	def _launchConfig(self,*args,**kwargs):
		path=self.property("path")
		fpath=self.property("fpath")
		if len(path)>0:
			self.configure.emit(self)
			if not path.endswith(".desktop") or "applications" not in path:
				pathdir=os.path.dirname(path)
				pathconfig=os.path.join(pathdir,"contents","ui","config.ui")
				if os.path.exists(pathconfig):
					cmd="python3 {0} {1}".format(os.path.join(os.path.dirname(os.path.abspath(__file__)),"tools/configLauncher.py"),pathconfig)
					try:
						l=threadLauncher(cmd)
						self.threadLaunchers.append(l)
						l.start()
						l.finished.connect(self._endLaunch)
					except Exception as e:
						print("Error launching config {}".format(pathconfig))
						print(e)
		elif len(fpath)>0:
			if "kwin4_effect" in fpath:
				self.configure.emit(self)
				cmd="systemsettings kcm_kwin_effects"
				try:
					l=threadLauncher(cmd)
					self.threadLaunchers.append(l)
					l.start()
					l.finished.connect(self._endLaunch)
				except Exception as e:
					print("Error launching config {}".format(pathconfig))
					print(e)
	#def _launchConfig

	def _popup(self):
		if self.mnu:
			y=self.y()+self.height()
			scr=QApplication.screens()[0]
			screenheight=scr.size().height()
			if y+self.mnu.height()>screenheight:
				y=self.y()-(screenheight-y-self.mnu.height())
			x=0
			self.mnu.popup(self.mapToGlobal(QPoint(x,y)))
			path=self.property("path")
			if path.endswith("metadata.json"):
				dirn=os.path.dirname(path)
				path=os.path.join(dirn,"contents","ui","config.ui")
				if os.path.exists(path)==False:
					path=""
			elif "kwin4_effect" in self.property("fpath"):
					path=self.property("fpath")
			else:
				path=""
			if len(path)==0:
				act=self.mnu.defaultAction()
				act.setEnabled(False)
	#def _popup

	def _addContextMenu(self):
		mnu=QMenu(self.name)
		#toggle=mnu.addAction(i18n["TOGGLE"])
		confapp=mnu.addAction(i18n["CONFIGURE"])
		#confbtn=mnu.addAction(i18n["CONFBTN"])
		confdock=mnu.addAction(i18n["CONFDOCK"])
		#toggle.triggered.connect(self._toggle)
		confapp.triggered.connect(self._launchConfig)
		#confbtn.triggered.connect(self._launchConfigBtn)
		confdock.triggered.connect(self.configureMain.emit)
		mnu.setDefaultAction(confapp)
		return(mnu)
	#def _addContextMenu

	def eventFilter(self,*args):
		wdg=args[0]
		ev=args[1]
		if ev.type()==QEvent.Type.ContextMenu:
			self.popupShow=True
		if ev.type()==QEvent.Type.Resize and self.popupShow==True:
			self.popupShow=False
		if self.popupShow==False and (ev.type()==QEvent.Type.Enter or ev.type()==QEvent.Type.FocusIn):
			if self.hasFocus()==False:
				self.setFocus()
				size=self.size()
				origSize=72
				newsize=QSize(size.width(),origSize*1.5)
				self.setIconSize(newsize)
				self.setFixedSize(newsize)
				self.lbl.toggle(self.mapToGlobal(QPoint(0,self.y()+self.height())))
				self.focusIn.emit(self)
		elif self.popupShow==True or (ev.type()==QEvent.Type.Leave or ev.type()==QEvent.Type.FocusOut):
			size=self.size()
			if self.lbl.isVisible():
				self.lbl.setVisible(False)
		#		self.lbl.toggle(self.mapToGlobal(QPoint(self.x(),self.y())))
			newsize=QSize(size.width(),self.initialSize.height()/1.1)
			self.setFixedSize(newsize)
			self.setIconSize(newsize)
		ev.ignore()
		return(False)
	#def eventFilter
#class QPushButtonDock

class accessdock(QWidget):
	"""Accessible dock main class.
		Draws the dock in screen at position x,y (borrowed from kwinrc)

		Attributes
		----------
			grid: QTableTouchWidget
				Grid for buttons
			libdock: Module
				Module with extra functionality
	"""
	def __init__(self,parent=None):
		super().__init__()
		self.dbg=True
		self.libdock=libdock.libdock()

		self.setWindowIcon(QIcon.fromTheme("accessibledock"))
		QGuiApplication.setDesktopFileName("accessibledock")
		self.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)
		#This hides decoration and bypass window 
		#also skips app registering in at-spi so is unexistent for ORCA 
		#self.setWindowFlags(Qt.BypassWindowManagerHint)
		#self.setStyleSheet("margin:0px")
		layout=QGridLayout()
		layout.setContentsMargins(2,2,2,2)
		self.setLayout(layout)
		self.grid=QTableTouchWidget(1,0)
		self.grid.setObjectName("Table")
		self.grid.setShowGrid(False)
		self.grid.verticalHeader().hide()
		self.grid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.grid.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.grid.horizontalHeader().hide()
		self.grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.grid.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		#redirect event easy way
		self.grid.mouseMoveEvent=self.mouseMoveEvent
		layout.addWidget(self.grid,0,0)
		self.threadLaunchers=[]
		self.updateScreen()
		#self.setStyleSheet('QPushButton{border:3px solid rgba(%s);}'%color)
		self._resize()
		coords=self.libdock.readKValue("kwinrc","accessibledock","coords").split(",")
		if len(coords)>1:
			self.move(int(coords[0]),int(coords[1]))
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("accessdock: {}".format(msg))
	#def _debug

	def closeEvent(self,*args):
		if args[0].spontaneous():
			args[0].accept()
		else:
			args[0].ignore()
			self._toggle()
	#def closeEvent

	def _setColorForBorder(self):
		qplt=QPalette()
		if hasattr(qplt,"accent"):
			qbrs=qplt.accent()
			(r,g,b,a)=qbrs.color().getRgbF()
		else:
			qbrs=qplt.dark()
			(r,g,b,a)=qbrs.color().getRgbF()
			(r,g,b,a)=(a-r,a-g,a-b,a)
		#Dark is the new bright in the world of nonsense
		color="{},{},{},{}".format(255*r,255*g,255*b,a)
		self.setStyleSheet('#Table{border:3px solid rgba(%s);}'%color)
	#def _setColorForBorder

	def _launchDockConfig(self,*args,**kwargs):
		self.setVisible(False)
		try:
			cmd=os.path.join(os.path.dirname(os.path.abspath(__file__)),"accessdock-config.py")
			l=threadLauncher(cmd)
			self.threadLaunchers.append(l)
			l.start()
			l.finished.connect(self._endLaunch)
		except:
			print("Error launching config")
	#def _launchDockConfig

	def _endLaunch(self,*args):
		self.updateScreen()
		self.setVisible(True)
	#def _endLaunch

	def mousePressEvent(self, ev):
		ev.accept()
	#def mousePressEvent

	def mouseMoveEvent(self, ev):
		x = ev.globalX()-(self.width()/2)
		y = ev.globalY()
		self.move(x, y)
	#def mouseMoveEvent

	def mouseReleaseEvent(self,*args):
		ncoords="{},{}".format(self.x(),self.y())
		coords=self.libdock.readKValue("kwinrc","accessibledock","coords").split(",")
		if ncoords!=coords:
			self.libdock.writeKValue("kwinrc","accessibledock","coords",ncoords)
	#def mouseReleaseEvent

	def leaveEvent(self,*args):
		#steal focus so buttons get resized
		self.setFocus()
	#def leaveEvent

	def updateScreen(self):
		self._setColorForBorder()
		oldcount=self.grid.columnCount()
		w=0
		if oldcount>0:
			w=self.width()/oldcount
		self.grid.clear()
		self.grid.setColumnCount(0)
		self.btnMnu={}
		launchers=self.libdock.getLaunchers()
		bigTip=False
		if self.libdock.readKValue("kwinrc","accessibledock","tooltipbig")=="true":
			bigTip=True
		if len(launchers)<=0:
			wrkF="/usr/share/accesswizard/dock/accessdock-config.py"
			launchers.append(("accessdock-config.py",{"File":wrkF,"Path":wrkF,"fpath":wrkF,"Name":"Configure","Icon":"accessdock","Exec":wrkF}))
		for launcher in launchers:
			btn=QPushButtonDock(launcher,bigTip,parent=self)
			btn.configureMain.connect(self._launchDockConfig)
			btn.configure.connect(self._toggle)
			btn.configureLauncher.connect(self._toggle)
			btn.toggle.connect(self._toggle)
			self.grid.setColumnCount(self.grid.columnCount()+1)
			self.grid.setCellWidget(0,self.grid.columnCount()-1,btn)
		hh=self.grid.horizontalHeader()
		hh.setSectionResizeMode(hh.ResizeToContents)
		vh=self.grid.verticalHeader()
		vh.setSectionResizeMode(vh.ResizeToContents)
		if oldcount>0:
			self._resize()
	#def updateScreen
	
	def _resize(self):
		colWidth=self.grid.horizontalHeader().sectionSize(0)
		width=(self.grid.columnCount()*colWidth)+(colWidth/3)
		rowHeight=self.grid.verticalHeader().sectionSize(0)
		height=(self.grid.rowCount()*rowHeight)
		self.grid.resize(QSize(width,height))
		width+=colWidth/30
		height+=rowHeight/3
		self.setFixedSize(width,height)
	#def _resize

	def _toggle(self,*args,**kwargs):
		if self.isVisible()==False:
			self.updateScreen()
		self.setVisible(not(self.isVisible()))
	#def _toggle
#class accessdock
		
if __name__=="__main__":
	app=QApplication(["AccessDock"])
	dock=accessdock()
	#Check if is already running
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	try:
		bus=dbus.SessionBus()
	except Exception as e:
		print("Could not get session bus: %s\nAborting"%e)
		sys.exit(1)
	try:
		objbus=bus.get_object("net.lliurex.accessibledock","/net/lliurex/accessibledock")
		objint=dbus.Interface(bus,"net.lliurex.accessibledock")
		objbus.toggle()
		print("Already launched!")
		sys.exit(2)
	except Exception as e:
		print(e)
		pass
	name=dbus.service.BusName("net.lliurex.accessibledock",bus)
	bus.add_signal_receiver(dock._toggle,
                        bus_name='net.lliurex.accessibledock',
                        interface_keyword='',
                        member_keyword='',
                        path_keyword='',
                        message_keyword='')
	objbus=bus.get_object("net.lliurex.accessibledock","/net/lliurex/accessibledock")
	objbus.connect_to_signal("Toggled",dock._toggle,dbus_interface="net.lliurex.accessibledock")
	dclient=dbusMethods(bus,dock)
	dock.show()
	app.exec_()
