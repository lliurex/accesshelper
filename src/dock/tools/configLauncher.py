#!/usr/bin/python3

import os,subprocess
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QGridLayout,QTableWidget,QScrollArea,QLabel,QGroupBox,QRadioButton
from PySide2.QtCore import QFile, QIODevice
from PySide2.QtGui import QColor
from QtExtraWidgets import QKdeConfigWidget

if __name__ == "__main__":
	app = QApplication(["Configuration"])
	UiFile=sys.argv[1]
	window=QKdeConfigWidget.QKdeConfigWidget(UiFile)
	layout=window.layout()
	btnBox=QWidget()
	hlay=QHBoxLayout()
	btnOk=QPushButton("Ok")
	btnOk.clicked.connect(window.saveChanges)
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
