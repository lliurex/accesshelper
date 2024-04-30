#!/usr/bin/python3

import os,subprocess
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication,QDialog,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QGridLayout,QLabel,QPushButton,QLineEdit,\
	QRadioButton,QCheckBox,QComboBox,QTableWidget,QSlider,QScrollArea,QMessageBox,QCalendarWidget
from PySide2.QtCore import QFile, QIODevice
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
	if isinstance(widget,QScrollArea):
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
			configWidgets.append(_recursiveExploreWidgets(widget))
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
		if hasattr(wdg,"text"):
			key=name.replace("kcfg_","")
			cmd=["kreadconfig5","--file","kwinrc","--group","{0}-{1}".format(plugType,uiId),"--key",key]
			print(" ".join(cmd))
			out=subprocess.check_output(cmd,universal_newlines=True,encoding="utf8")
			value=out.strip()
			if len(value)>0:
				print(wdg)
				if hasattr(wdg,"setText"):
					wdg.setText(value)
				elif hasattr(wdg,"setValue"):
					wdg.setValue(int(value))
#def readConfig

def saveChanges(configWidgets,uiId):
	if "effect" in uiId:
		plugType="Effect"
	else:
		plugType="Script"
	for name,wdg in configWidgets:
		if len(name)==0:
			continue
		key=name.replace("kcfg_","")
		if hasattr(wdg,"text"):
			cmd=["kwriteconfig5","--file","kwinrc","--group","{0}-{1}".format(plugType,uiId),"--key",key,"--value",wdg.text()]
			print(cmd)

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
	btnBox=QWidget()
	hlay=QHBoxLayout()
	btnOk=QPushButton("Ok")
	btnOk.clicked.connect(lambda: saveChanges(configWidgets,UiId))
	btnKo=QPushButton("Cancel")
	btnKo.clicked.connect(app.exit)
	hlay.addWidget(btnOk)
	hlay.addWidget(btnKo)
	btnBox.setLayout(hlay)
	layout.addWidget(btnBox)
	window.show()
	readConfig(configWidgets,UiId)
	sys.exit(app.exec_())
