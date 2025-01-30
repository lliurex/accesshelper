#!/usr/bin/python3
import sys,os,signal
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QGridLayout,QTableWidget,QScrollArea,QLabel,QGroupBox
from PySide2.QtCore import QFile, QIODevice
from llxaccessibility import llxaccessibility

accessibility=llxaccessibility.client()
uiFile="{}/main.qml".format(os.path.dirname(os.path.realpath(sys.argv[0])))
print(uiFile)

def _print(self,*args):
	print(args)

def _loadGui():
	window=None
	QUiFile = QFile(uiFile)
	if not QUiFile.open(QIODevice.ReadOnly):
		print(f"Cannot open {uiFile}: {QUiFile.errorString()}")
	else:
		loader = QUiLoader()
		window = loader.load(QUiFile)
		QUiFile.close()
	return(window)
#def _loadGui

## MAIN ##
if __name__ == "__main__":
	name="FocusFrame"
	#app = QApplication([name])
	window=_loadGui()
#try:
#	accessibility.trackFocus(_print)
#except Exception as e:
#	print(e)
#	pass

