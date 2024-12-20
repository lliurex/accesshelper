#!/usr/bin/python3
### This library implements atspi communications
import os,shutil,sys
from PySide2.QtWidgets import QApplication
from llxaccessibility import llxaccessibility

app=QApplication(["TTS"])
if len(sys.argv)!=6:
	sys.exit(-1)
accessibility=llxaccessibility.client()
accessibility.readScreen(onlyScreen=True)
#txt=accessibility.getClipboardText()
#if not txt:
#	txt=accessibility.getImageOcr()
#if len(txt)>0:
#	accessibility.ttsSay(txt)
##spk.setParms(stretch=sys.argv[1],pitch=sys.argv[2],rate=sys.argv[3],voice=sys.argv[4],engine=sys.argv[5])
