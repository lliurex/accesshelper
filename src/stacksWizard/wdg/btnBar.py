#!/usr/bin/python3
from PySide2.QtWidgets import QGridLayout,QPushButton,QWidget
from PySide2.QtCore import Qt
from extras.i18n import *

class btnBar(QWidget):
	def __init__(self,*args):
		super().__init__()
		self.parentStk=args[0]
		self._scrControls()
	#def __init__

	def _goNext(self):
		idx=self.parentStk.getCurrentStackIndex()+1
		self.parentStk.setCurrentStack(idx=idx)
		self.setCursor(Qt.ArrowCursor)
	#def _goNext

	def _goPrev(self):
		idx=self.parentStk.getCurrentStackIndex()-1
		if idx<0:
			idx=0
		if idx<self.parentStk.getCurrentStackIndex():
			self.parentStk.setCurrentStack(idx=idx)
		self.setCursor(Qt.ArrowCursor)
	#def _goPrev

	def _scrControls(self):
		box=QGridLayout(self)
		box.setSpacing(24)
		self.btnPrev=QPushButton(i18n["BTN_PREV"])
		self.btnPrev.clicked.connect(self._goPrev)
		self.btnNext=QPushButton(i18n["BTN_NEXT"])
		self.btnNext.clicked.connect(self._goNext)
		box.addWidget(self.btnPrev,0,0,1,1)
		box.addWidget(self.btnNext,0,1,1,1)
	#def _defScreenControlButtons

