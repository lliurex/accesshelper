#!/usr/bin/python3
from llxaccessibility import llxaccessibility
from PySide2.QtWidgets import QWidget,QGridLayout,QScrollArea,QSpinBox,QLabel,QPushButton
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem,QScrollLabel
from extras.i18n import *
from wdg.btnBar import btnBar

class scaleConfig(QStackedWindowItem):
	def __init_stack__(self,*args):
		self.setProps(shortDesc="",
			description="",
			longDesc="",
			icon="preferences-desktop-accessibility",
			tooltip="",
			index=2)
		self.hideControlButtons()
	#def __init_stack__

	def keyPressEvent(self,*args):
		print(args[0].key())

	def _defScaleSize(self):
		lbl=QLabel()
		txt="<strong>{}</strong>".format(i18n["SCALE_SIZE_MSG"])
		lbl.setText(txt)
		return(lbl)
	#def _defScaleSize

	def _defScaleDisclaimer(self):
		lbl=QLabel()
		lbl.setWordWrap(True)
		txt="<p>{0}. {1}</p>".format(i18n["SCALE_SIZE_MSG_1"],i18n["SCALE_SIZE_MSG_2"])
		lbl.setText(txt)
		return(lbl)
	#def _defScaleDisclaimer

	def _changeScaleSize(self,*args):
		font=self.lblTestSize.font()
		font.setPointSize(args[0])
		self.lblTestSize.setFont(font)
	#def _changeScaleSize

	def _defScaleSizeControls(self):
		wdg=QSpinBox()
		#wdg.setValue()
		#wdg.valueChanged.connect(self._changeFontSize)
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
		lblScaleSize=self._defScaleSize()
		wbox.addWidget(lblScaleSize,0,0,1,1,Qt.AlignTop|Qt.AlignCenter)
		lblDisclaimer=self._defScaleDisclaimer()
		wbox.addWidget(lblDisclaimer,1,0,1,1)
		self.spnScaleSize=self._defScaleSizeControls()
		wbox.addWidget(self.spnScaleSize,2,0,1,1,Qt.AlignCenter)
		self.lblTestSize=self._defTestArea()
		wbox.addWidget(self.lblTestSize,3,0,1,1)
		btns=self._defScreenControlButtons()
		wbox.addWidget(btns,4,0,1,1,Qt.AlignBottom)
		scr.setWidget(wdg)
		box.addWidget(scr)
	#def __initScreen__

	def updateScreen(self,*args):
		#self.spnFontSize.setValue(self.font().pointSize())
		pass
