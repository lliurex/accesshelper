import os,json
from llxaccessibility import llxaccessibility
from PySide2.QtWidgets import QWidget,QGridLayout,QListWidget,QListWidgetItem,QLabel
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize
from QtExtraWidgets import QStackedWindowItem, QPushInfoButton,QTableTouchWidget
from lib.threadLib import thLauncher
from rebost import store
from extras.i18n import *

class QConfigPane(QWidget):
	def __init__(self,apps,parent=None):
		super().__init__(parent)
		self.accesshelper=llxaccessibility.client()
		self._renderGui(apps)
		self.rebost=store.client()
		self.thLauncher=thLauncher(self.rebost)
	#def __init__

	def _launch(self,*args):
		if args[0].startswith("kcm"):
			self.accesshelper.launchKcmModule(args[0])
		else:
			self.thLauncher.setParms(args[0])
			self.thLauncher.start()
	#def _launch

	def _renderBtn(self,app):
		btn=QPushInfoButton()
		btn.defaultSize=72
		btn.label.setAlignment(Qt.AlignLeft)
		f=btn.font()
		if f.pointSize()<20:
			f.setPointSize(18)
		btn.setFont(f)
		for appName,data in app.items():
			btn.setText(i18n.get(appName))
			btn.setDescription(i18n.get(data[0]))
			if data[1]=="":
				appId=None
				if app=="ORCA":
					appId="orca"
				elif app=="EVIA":
					appId="eviacam"
				elif app=="ANTI":
					appId="antimicrox"
				if appId!=None:
					app=json.loads(self.rebost.showApp(appId))
					data[1]=app[0].get("icon")
			btn.clicked.connect(lambda x:self._launch(appName))
			btn.loadImgSync(data[1])
		return(btn)
	#def _renderBtn

	def _renderGui(self,apps):
		lay=QGridLayout(self)
		wdg=QTableTouchWidget(0,1)
		wdg.horizontalHeader().hide()
		wdg.verticalHeader().hide()
		rsrcDir=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","rsrc")
		for app in apps:
			wdg.setRowCount(wdg.rowCount()+1)
			btn=self._renderBtn(app)
			btn.setMinimumWidth(wdg.size().width())
			btn.setFixedHeight(84)
			wdg.setCellWidget(wdg.rowCount()-1,0,btn)
			wdg.setRowHeight(wdg.rowCount()-1,btn.height()+20)
			btn.show()
		wdg.setColumnWidth(0,btn.width())
		lay.addWidget(wdg,0,0,1,1)
	#def _renderGui

