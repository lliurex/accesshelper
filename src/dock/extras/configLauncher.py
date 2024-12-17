#!/usr/bin/python3

import os,subprocess
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QGridLayout,QTableWidget,QScrollArea,QLabel,QGroupBox,QRadioButton
from PySide2.QtCore import QFile, QIODevice
from PySide2.QtGui import QColor

plugtype="Effect"
def _getSignalForConnection(widget):
	name=widget.objectName()
	if name.startswith("kcfg_"):
		return(name)
	return("")
#def _getSignalForConnection

def _recursiveExploreWidgets(widget):
	if widget==None:
		return
	name=_getSignalForConnection(widget)
	if isinstance(widget,QTableWidget):
		for x in range (0,widget.rowCount()):
			for y in range (0,widget.columnCount()):
				tableWidget=widget.cellWidget(x,y)
				_recursiveExploreWidgets(tableWidget)
	elif isinstance(widget,QScrollArea):
		wdg=widget.widget()
		if wdg:
			_recursiveExploreWidgets(wdg)
		else:
			lay=widget.layout()
			if lay:
				_recursiveExploreWidgets(lay)
	else:
		if type(widget) in [QGridLayout,QVBoxLayout,QHBoxLayout]:
			_recursiveSetupEvents(widget)
		else:
			try:
				if widget.layout():
					_recursiveSetupEvents(widget.layout())
			except:
				_recursiveSetupEvents(widget)
	return(name,widget)
#def _recursiveExploreWidgets(widget):

def _recursiveSetupEvents(layout):
	if layout==None:
		return
	configWidgets=[]
	for idx in range(0,layout.count()):
		widget=layout.itemAt(idx).widget()
		if isinstance(widget,QWidget):
			if isinstance(widget,QGroupBox):
				for rad in widget.findChildren(QRadioButton):
					wdg=_recursiveExploreWidgets(rad)
					if wdg not in configWidgets:
						configWidgets.append(wdg)
			else:
				wdg=_recursiveExploreWidgets(widget)
			if wdg not in configWidgets:
				configWidgets.append(wdg)
		elif layout.itemAt(idx).layout():
			_recursiveSetupEvents(layout.itemAt(idx).layout(),block)
	return(configWidgets)
#def _recursiveSetupEvents

def readConfig(configWidgets,uiId):
	if "effect" in uiId:
		plugType="Effect"
	else:
		plugType="Script"
	for name,wdg in configWidgets:
		if len(name)==0:
			continue
		#if hasattr(wdg,"text"):
		key=name.replace("kcfg_","")
		cmd=["kreadconfig5","--file","kwinrc","--group","{0}-{1}".format(plugType,uiId),"--key",key]
		out=subprocess.check_output(cmd,universal_newlines=True,encoding="utf8")
		value=out.strip()
		if len(value)>0:
			if isinstance(wdg,QPushButton):
				hasKcolor=wdg.property("color")
				if hasKcolor!=None:
					kcolor=value.split(",")
					newcolor=QColor.fromRgb(int(kcolor[0]),int(kcolor[1]),int(kcolor[2]))
					wdg.setProperty("color",newcolor)
				wdg.setText(value)
			elif hasattr(wdg,"checkState"):
				state=True
				if value!="true":
					state=False
				wdg.setChecked(state)
			elif hasattr(wdg,"isChecked"):
				state=True
				if value!="true":
					state=False
				wdg.setChecked(state)
			elif hasattr(wdg,"setCurrentIndex"):
				wdg.setCurrentIndex(int(value))
			elif hasattr(wdg,"setValue"):
				wdg.setValue(int(value))
			elif hasattr(wdg,"setText"):
				wdg.setText(value)
#def readConfig

def _generateCommand(plugType,uiId,key,text):
	cmd=[]
	cmd=["kwriteconfig5","--file","kwinrc","--group","{0}-{1}".format(plugType,uiId),"--key",key,str(text)]
	return(cmd)
#def _generateCommand

def saveChanges(configWidgets,uiId):
	cmd=""
	if "effect" in uiId:
		plugType="Effect"
	else:
		plugType="Script"
	for name,wdg in configWidgets:
		if isinstance(wdg,QLabel):
			continue
		if len(name)==0:
			continue
		key=name.replace("kcfg_","")
		hasKcolor=wdg.property("color")
		if hasKcolor!=None:
			color="{0},{1},{2}".format(hasKcolor.red(),hasKcolor.green(),hasKcolor.blue())
			cmd=self._generateCommand(plugType,uiId,key,color)
			#cmd=["kwriteconfig5","--file","kwinrc","--group","{0}-{1}".format(plugType,uiId),"--key",key,str(color)]
		elif hasattr(wdg,"checkState") or hasattr(wdg,"group"):
			print(wdg)
			state=wdg.isChecked()
			cmd=_generateCommand(plugType,uiId,key,str(state).lower())
		elif hasattr(wdg,"value"):
			cmd=_generateCommand(plugType,uiId,key,str(wdg.value()))
		elif hasattr(wdg,"text"):
			cmd=_generateCommand(plugType,uiId,key,str(wdg.text()))
		if len(cmd)>0:
			subprocess.run(cmd)
	sys.exit(0)
#def saveChanges

def getId(UiFile):
	#search for a metadata file
	end=False
	path=UiFile
	uiId=""
	while end==False:
		path=os.path.dirname(path)
		for f in os.scandir(path):
			if f.name.startswith("metadata")==True:
				end=True
				path=f.path
		if path.count("/")<=2:
			end=True
	if path.endswith("json") or path.endswith("desktop"):
		with open(path,"r") as f:
			fcontent=f.readlines()
		for l in fcontent:
			if l.replace(" ","").startswith("\"Id\""):
				uiId=l.split(":")[-1]
				uiId=uiId.replace(" ","").replace("\"","").replace(",","").strip()
	return(uiId)
#def getId

if __name__ == "__main__":
	app = QApplication(["Configuration"])
	UiFile=sys.argv[1]
	QuiFile = QFile(UiFile)
	if not QuiFile.open(QIODevice.ReadOnly):
		print(f"Cannot open {UiFile}: {QuiFile.errorString()}")
		sys.exit(-1)
	loader = QUiLoader()
	window = loader.load(QuiFile)
	QuiFile.close()
	if not window:
		print(loader.errorString())
		sys.exit(-1)
	UiId=getId(UiFile)
	layout=window.layout()
	configWidgets=_recursiveSetupEvents(layout)
	readConfig(configWidgets,UiId)
	btnBox=QWidget()
	hlay=QHBoxLayout()
	btnOk=QPushButton("Ok")
	btnOk.clicked.connect(lambda: saveChanges(configWidgets,UiId))
	btnKo=QPushButton("Cancel")
	btnKo.clicked.connect(app.exit)
	btnOk.setFixedSize(btnKo.sizeHint().width(),btnOk.sizeHint().height())
	btnKo.setFixedSize(btnKo.sizeHint().width(),btnOk.sizeHint().height())
	hlay.addWidget(btnOk)
	hlay.addWidget(btnKo)
	btnBox.setLayout(hlay)
	if isinstance(layout,QGridLayout):
		layout.addWidget(btnBox,layout.rowCount(),0,1,layout.columnCount())
	else:
		layout.addWidget(btnBox)
	window.show()
	sys.exit(app.exec_())
