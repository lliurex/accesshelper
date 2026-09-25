#!/usr/bin/python3
import os,subprocess
from PySide2.QtCore import QThread,Signal

class thWorker(QThread):
	def __init__(self,proc,parent=None):
		QThread.__init__(self,parent)
		self.proc=proc
	#def __init__

	def run(self):
		self.proc.communicate()
	#def run
#class thWorker


class thProcess(QThread):
	def __init__(self,parent=None):
		QThread.__init__(self,parent)
	#def __init__

	def setCmd(self,cmd,parms=""):
		self.cmd=cmd
		self.parms=parms
		self.procs=[]
	#def setCmd

	def run(self):
		cmd=[self.cmd]
		if len(self.parms)>0:
			parms=self.parms.split(" ")
			cmd.extend(parms)
		proc=subprocess.Popen(cmd)
		self.procs.append(thWorker(proc))
	#def run
