#!/usr/bin/python3
from llxaccessibility import llxaccessibility
from PySide2.QtWidgets import QWidget,QGridLayout,QScrollArea,QSpinBox,QLabel,QPushButton
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem,QScrollLabel
from extras.i18n import *
from wdg.btnBar import btnBar

class fontConfig(QStackedWindowItem):
	def __init_stack__(self,*args):
		self.setProps(shortDesc="",
			description="",
			longDesc="",
			icon="preferences-desktop-accessibility",
			tooltip="",
			index=1)
		self.hideControlButtons()
	#def __init_stack__

	def keyPressEvent(self,*args):
		print(args[0].key())

	def _defFontSize(self):
		lbl=QLabel()
		txt="<strong>{}</strong>".format(i18n["FONT_SIZE_MSG"])
		lbl.setText(txt)
		return(lbl)
	#def _defFontSize

	def _changeFontSize(self,*args):
		font=self.lblTestSize.font()
		font.setPointSize(args[0])
		self.lblTestSize.setFont(font)
	#def _changeFontSize

	def _defFontSizeControls(self):
		wdg=QSpinBox()
		wdg.setValue(self.font().pointSize())
		wdg.valueChanged.connect(self._changeFontSize)
		return(wdg)
	#def _defFontSizeControls

	def _defTestArea(self):
		lbl=QScrollLabel(styled=False)
		lbl.setText("{2}<p>{0}</p><p>{1}</p>".format(i18n["FONT_SIZE_TEST_1"],i18n["FONT_SIZE_TEST_2"],i18n["FONT_SIZE_TEST_0"]))
		return(lbl)
	#def _defTestArea(self):

	def _defScreenControlButtons(self):
		wdg=btnBar(self.parent)
		return(wdg)
	#def _defScreenControlButtons

	def __initScreen__(self,*args):
		box=QGridLayout(self)
		scr=QScrollArea()
		scr.setWidgetResizable(True)
		wdg=QWidget()
		wbox=QGridLayout(wdg)
		lblFontSize=self._defFontSize()
		wbox.addWidget(lblFontSize,0,0,1,1,Qt.AlignTop|Qt.AlignCenter)
		self.spnFontSize=self._defFontSizeControls()
		wbox.addWidget(self.spnFontSize,1,0,1,1,Qt.AlignCenter)
		self.lblTestSize=self._defTestArea()
		wbox.addWidget(self.lblTestSize,2,0,1,1)
		btns=self._defScreenControlButtons()
		wbox.addWidget(btns,3,0,1,1,Qt.AlignBottom)
		scr.setWidget(wdg)
		box.addWidget(scr)
	#def __initScreen__

	def updateScreen(self,*args):
		self.spnFontSize.setValue(self.font().pointSize())
		self.setCursor(Qt.ArrowCursor)
