#!/usr/bin/python3
from PySide2.QtWidgets import QApplication,QMessageBox,QGridLayout,QLabel,QPushButton,QWidget
from PySide2.QtCore import Qt,QSignalMapper
from stacks import libaccesshelper
import gettext
import time
_ = gettext.gettext
QString=type("")
QInt=type(0)

class accessdock(QWidget):
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.dbg=True
		self.fastSettings={"color":"color","font_size":"","pointer_size":"","read":"","config":"","hide":""}
		self.widgets={}
		self._renderGui()
		self.x=0
		self.y=0
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("dock: {}".format(msg))
	#def _debug

	def _renderGui(self):
		#self.setWindowFlags(Qt.X11BypassWindowManagerHint)
		self.setWindowModality(Qt.WindowModal)
		self.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
		layout=QGridLayout()
		col=0
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self.execute)
		for setting,value in self.fastSettings.items():
			lbl=QLabel(setting.replace("_"," ").capitalize())
			layout.addWidget(lbl,0,col,1,1)
			btn=QPushButton()
			sigmap_run.setMapping(btn,setting)
			btn.clicked.connect(sigmap_run.map)
			layout.addWidget(btn,1,col,1,1)
			self.widgets[setting]=btn
			col+=1

		self.setLayout(layout)
	#def _renderGui

	def execute(self,*args,**kwargs):
		if isinstance(args,tuple):
			if args[0].lower()=="hide":
				self.hide()

	def mousePressEvent(self, event):
		_lastpos = event.pos()

	def mouseMoveEvent(self, e):

		x = e.globalX()-(self.width()/2)
		y = e.globalY()
		print(e.globalPos())
		print("{} {}".format(x,y))
		self.move(x, y)
		

app=QApplication(["AccessDock"])
dock=accessdock()
dock.show()
app.exec_()
