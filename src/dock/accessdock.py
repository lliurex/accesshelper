#!/usr/bin/python3
import os,sys,subprocess
from PySide2.QtWidgets import QApplication,QGridLayout,QWidget,QPushButton,QHeaderView,QMenu,QAction
from PySide2.QtCore import Qt,QSignalMapper,QSize,QThread,QPoint,QEvent,Signal
from PySide2.QtGui import QIcon,QPixmap,QCursor,QColor
import dbus
import dbus.service
import dbus.mainloop.glib
from QtExtraWidgets import QTableTouchWidget
import subprocess
import lib.libdock as libdock
import gettext
import resources
_ = gettext.gettext

i18n={"CONFIGURE":_("Configure"),
	"CONFDOCK":_("Configure dock")}

class dbusMethods(dbus.service.Object):
	def __init__(self,bus_name,*args,**kwargs):
		super().__init__(bus_name,"/net/lliurex/accessibledock")
		self.widget=args[0]

	@dbus.service.signal("net.lliurex.accessibledock")
	def toggleVisible(self):
		pass
	#def toggleVisible(self)

	@dbus.service.method("net.lliurex.accessibledock")
	def toggle(self,*args):
		self.toggleVisible()
		pass
	#def toggle
#class dbusMethods

class threadLauncher(QThread):
	def __init__(self,cmd,parent=None):
		super().__init__()
		self.cmd=cmd
	#def __init__

	def run(self):
		subprocess.run(self.cmd.split())
		return(True)
	#def run
#class threadLauncher

class accessdock(QWidget):
	def __init__(self,parent=None):
		super().__init__()
		self.dbg=True
		self.libdock=libdock.libdock()
		self.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint)
		self.setWindowFlags(Qt.BypassWindowManagerHint)
		layout=QGridLayout()
		self.setLayout(layout)
		self.grid=QTableTouchWidget(1,0)
		self.grid.verticalHeader().hide()
		self.grid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.grid.horizontalHeader().hide()
		self.grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		layout.addWidget(self.grid,0,0)
		self.threadLaunchers=[]
		self.updateScreen()
		colWidth=self.grid.horizontalHeader().sectionSize(0)
		width=(self.grid.columnCount()*colWidth)+(colWidth/3)
		rowHeight=self.grid.verticalHeader().sectionSize(0)
		height=(self.grid.rowCount()*rowHeight)
		self.grid.resize(QSize(width,height))
		self.activeWidget=None
		width+=colWidth/30
		height+=rowHeight/3
		self.setFixedSize(width,height)
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("accessdock: {}".format(msg))
	#def _debug

	def mousePressEvent(self, event):
		event.accept()
	#def mousePressEvent

	def mouseMoveEvent(self, e):
		x = e.globalX()-(self.width()/2)
		y = e.globalY()
		self.move(x, y)
	#def mouseMoveEvent

	def eventFilter(self,*args):
		wdg=args[0]
		ev=args[1]
		if ev.type()==QEvent.Type.ContextMenu:
			self._popup(wdg)
		else:
			ev.ignore()
		return(False)
	#def eventFilter

	def _popup(self,wdg):
		mnu=self.btnMnu.get(wdg)
		if mnu:
			self.activeWidget=wdg
			mnu.popup(self.mapToGlobal(QPoint(wdg.x(),wdg.y())))
			path=self.activeWidget.property("path")
			if len(path)==0:
				act=mnu.defaultAction()
				act.setEnabled(False)
	#def _popup

	def _launchDockConfig(self,*args,**kwargs):
		self.setVisible(False)
		try:
			subprocess.run(["./accessdock-config.py"])
		except:
			print("Error launching config")
		finally:
			self.updateScreen()
			self.setFixedSize(self.grid.size())
			self.setVisible(True)
	#def _launchDockConfig

	def _launchConfig(self,*args,**kwargs):
		path=self.activeWidget.property("path")
		if len(path)>0:
			if path.endswith(".desktop") and "applications" in path:
				path=self.activeWidget.property("fpath")
				subprocess.run(["python3","extras/launchers.py",path])
			else:
				pathdir=os.path.dirname(path)
				pathconfig=os.path.join(pathdir,"contents","ui","config.ui")
				if os.path.exists(pathconfig):
					self.setVisible(False)
					try:
						subprocess.run(["extras/configLauncher.py",pathconfig])
					except:
						print("Error launching config {}".format(pathconfig))
					finally:
						self.setVisible(True)
	#def _launchConfig

	def updateScreen(self):
		self.grid.clear()
		self.grid.setColumnCount(0)
		self.btnMnu={}
		launchers=self.libdock.getLaunchers()
		for launcher in launchers:
			mnu=QMenu(launcher[1]["Name"])
			#actConfig=QAction("Configure")
			confapp=mnu.addAction(i18n["CONFIGURE"])
			confdock=mnu.addAction(i18n["CONFDOCK"])
			confapp.triggered.connect(self._launchConfig)
			confdock.triggered.connect(self._launchDockConfig)
			mnu.setDefaultAction(confapp)
			btn=QPushButton()
			btn.installEventFilter(self)
			btn.setContextMenuPolicy(Qt.CustomContextMenu)
			btn.customContextMenuRequested.connect(self._popup)
			#btn.setMenu(mnu)
			self.btnMnu[btn]=mnu
			btn=self._setupBtn(btn,launcher[1])
			btn.setProperty("file",launcher[0])
			self.grid.setColumnCount(self.grid.columnCount()+1)
			self.grid.setCellWidget(0,self.grid.columnCount()-1,btn)
	#def updateScreen

	def _setupBtn(self,btn,launcher):
		#btn.setText(launcher.get("Name","Unknown"))
		icn=QIcon()
		iconName=launcher.get("Icon","")
		if len(iconName)==0:
			iconName="rebost"
		if os.path.exists(iconName):
			pxm=QPixmap(iconName)
			icn=QIcon(pxm)
		else:
			icn=QIcon.fromTheme(iconName)
		btn.setToolTip(launcher["Name"])
		btn.setAccessibleName(launcher["Name"])
		btn.setIcon(icn)
		btn.setIconSize(QSize(64,64))
		btn.setFixedSize(QSize(72,72))
		btn.setProperty("path",launcher.get("Path",""))
		btn.setProperty("fpath",launcher.get("fpath",""))
		btn.clicked.connect(lambda: self._beginLaunch(launcher.get("Exec")))
		return(btn)
	#def _setupBtn

	def _beginLaunch(self,*args):
		l=threadLauncher(args[0])
		l.start()
		l.finished.connect(self._endLaunch)
		self.threadLaunchers.append(l)
	#def _beginLaunch

	def _endLaunch(self,*args):
		print(args)
	#def _endLaunch

	def _toggle(self,*args,**kwargs):
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
