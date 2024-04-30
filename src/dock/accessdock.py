#!/usr/bin/python3
import os,sys,io,psutil,shutil,signal,time
from PySide2.QtWidgets import QApplication,QGridLayout,QWidget,QPushButton,QHeaderView
from PySide2.QtCore import Qt,QSignalMapper,QSize,QThread
from PySide2.QtGui import QIcon,QPixmap,QCursor,QColor
from QtExtraWidgets import QTableTouchWidget
import subprocess
import lib.libdock as libdock

class threadLauncher(QThread):
	def __init__(self,cmd,parent=None):
		super().__init__()
		self.cmd=cmd

	def run(self):
		subprocess.run(self.cmd.split())
		return(True)
#class launch(QThread):

class accessdock(QWidget):
	def __init__(self,parent=None):
		super().__init__()
		self.dbg=True
		self.launchers=libdock.libdock()
		#self.setWindowModality(Qt.WindowModal)
		self.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint)
	#	self.setWindowFlags(Qt.X11BypassWindowManagerHint)
		layout=QGridLayout()
		self.setLayout(layout)
		self.grid=QTableTouchWidget(1,0)
		self.grid.verticalHeader().hide()
		self.grid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.grid.horizontalHeader().hide()
		self.grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		layout.addWidget(self.grid,0,0)#,Qt.AlignCenter|Qt.AlignCenter)
		self.threadLaunchers=[]
		self.updateScreen()
		colWidth=self.grid.horizontalHeader().sectionSize(0)
		width=(self.grid.columnCount()*colWidth)+(colWidth/3)
		rowHeight=self.grid.verticalHeader().sectionSize(0)
		height=(self.grid.rowCount()*rowHeight)
		self.grid.resize(QSize(width,height))
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

	def updateScreen(self):
		self.grid.clear()
		self.grid.setColumnCount(0)
		launchers=self.launchers.getLaunchers()
		for launcher in launchers:
			btn=QPushButton()
			btn=self._setUpBtn(btn,launcher[1])
			btn.setProperty("file",launcher[0])
			self.grid.setColumnCount(self.grid.columnCount()+1)
			self.grid.setCellWidget(0,self.grid.columnCount()-1,btn)
	#def updateScreen

	def _setUpBtn(self,btn,launcher):
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
		btn.clicked.connect(lambda: self._beginLaunch(launcher.get("Exec")))
		return(btn)
	#def _setUpBtn

	def _beginLaunch(self,*args):
		l=threadLauncher(args[0])
		l.start()
		l.finished.connect(self._endLaunch)
		self.threadLaunchers.append(l)
	#def _beginLaunch

	def _endLaunch(self,*args):
		print(args)
	#def _endLaunch
		
if __name__=="__main__":
	app=QApplication(["AccessDock"])
	dock=accessdock()
	dock.show()
	app.exec_()
