#!/usr/bin/python3
import subprocess,os
import tarfile
import tempfile
import time
import shutil
from collections import OrderedDict
from PySide2.QtGui import QIcon,QPixmap,QColor
from multiprocessing import Process
import dbus
import json
import random

class xHelperClass():
	def __init__(self):
		self.dbg=False
		self.dictFileData={}
		self.tmpDir="/tmp/.accesstmp"

	def _debug(self,msg):
		if self.dbg:
			print("libhelper: {}".format(msg))
	#def _debug
	
	def _getMonitors(self,*args):
		monitors=[]
		cmd=subprocess.run(["xrandr","--listmonitors"],capture_output=True,encoding="utf8")
		for xrandmonitor in cmd.stdout.split("\n"):
			monitor=xrandmonitor.split(" ")[-1].strip()
			if not monitor or monitor.isdigit()==True:
				continue
			monitors.append(monitor)
		return(monitors)
	#def _getMonitors

	def setScaleFactor(self,scaleFactor,plasma=True,xrand=False):
		cmd=["xrandr","--listmonitors"]
		output=subprocess.run(cmd,capture_output=True,text=True)
		monitors=[]
		for line in output.stdout.split("\n"):
			if len(line.split(" "))>=4:
				monitors.append("{0}={1}".format(line.split(" ")[-1],scaleFactor))
		cmd=[]
		if xrand==True:
			for monitor in monitors:
				f=round(1-((float(scaleFactor)-1)/3),2)
				output=monitor.split("=")[0]
				#Sometimes xrand fails if scaling from!=1 so force it
				cmd=["xrandr","--output",output,"--scale","{}x{}".format(1,1)]
				subprocess.run(cmd)
				cmd=["xrandr","--output",output,"--scale","{}x{}".format(f,f)]
				try:
					subprocess.run(cmd)
				except Exception as e:
					print(" ".join(cmd))
					print(e)
		return(" ".join(cmd))
	#def setScaleFactor
	
	def getScaleFactor(self):
		cmd=["xrandr"]
		out=subprocess.run(cmd,capture_output=True,universal_newlines=True)
		pres=""
		fscale=100
		for line in out.stdout.split("\n"):
			if "connected primary" in line:
				pres=line.split()[3].split("+")[0]
			if pres:
				if "*" in line:
					cres=line.strip().split()[0]
					xpres=float(pres.split("x")[0])
					xcres=float(cres.split("x")[0])
					fscale=xpres/xcres
					fscale=round(100+((1-fscale)*300))+1
					break
		fscale=5*(int(fscale/5))
		return(fscale)
	#def getScaleFactor

	def removeRGBFilter(self):
		for monitor in self._getMonitors():
			xrand=["xrandr","--output",monitor,"--gamma","1:1:1","--brightness","1"]
		xgamma=["xgamma","-screen","0","-rgamma","1","-ggamma","1","-bgamma","1"]
		cmd=subprocess.run(xgamma,capture_output=True,encoding="utf8")
	#def resetRGBFilter

	def setRGBFilter(self,alpha,onlyset=False):
		def getRgbCompatValue(color):
			(top,color)=color
			c=round((color*top)/255,2)
			return c
		def adjustCompatValue(color):
			(multiplier,c,minValue)=color
			while (c*100)%multiplier!=0 and c!=0:
				c=round(c+0.01,2)
			if c<=minValue:
				c=minValue
			return c
		#xgamma uses 0.1-10 scale. Values>4 are too bright and values<0.5 too dark
		maxXgamma=3.5
		minXgamma=0.5
		#kgamma uses 0.40-3.5 scale. 
		maxKgamma=3.5
		minKgamma=0.4
		(xred,xblue,xgreen)=map(getRgbCompatValue,[(maxXgamma,alpha.red()),(maxXgamma,alpha.blue()),(maxXgamma,alpha.green())])
		(red,blue,green)=map(getRgbCompatValue,[(maxKgamma,alpha.red()),(maxKgamma,alpha.blue()),(maxKgamma,alpha.green())])
		if red+blue+green>(maxKgamma*(2-(maxKgamma*0.10))): #maxKGamma*2=at least two channel very high, plus a 10% margin
			red-=1
			green-=1
			blue-=1
		multiplier=1
		(xred,xblue,xgreen)=map(adjustCompatValue,[[multiplier,minXgamma,xred],[multiplier,minXgamma,xblue],[multiplier,minXgamma,xgreen]])
		multiplier=5
		(red,blue,green)=map(adjustCompatValue,[[multiplier,minKgamma,red],[multiplier,minKgamma,blue],[multiplier,minKgamma,green]])
		brightness=1
		xgamma=["xgamma","-screen","0","-rgamma","{0:.2f}".format(xred),"-ggamma","{0:.2f}".format(xgreen),"-bgamma","{0:.2f}".format(xblue)]
		cmd=subprocess.run(xgamma,capture_output=True,encoding="utf8")
		return(xgamma,red,green,blue)
	#def setRGBFilter

	def currentRGBValue(self,*args,**kwargs):
		cmd=subprocess.run(["xgamma"],capture_output=True,encoding="utf8")
		values=cmd.stderr.strip().split(" ")
		rgba=[]
		color=QColor()
		for val in values:
			if len(val)==0:
				continue
			val=val.replace(",","").replace("\n","")
			fval=0
			if isinstance(val,float):
				fval=round((val*255)/3.5)
			elif isinstance(val,str) and val[0].isdigit():
				fval=round((float(val)*255)/3.5)
			else:
				continue
			#<72 is too dark so discard
			if fval<=73:
				fval=0
			rgba.append(fval)
		rgba.append(1.0)
		if len(rgba)==4:
			color.setRgb(rgba[0],rgba[1],rgba[2],rgba[3])
		return(color)
	#def currentRGBValue

	def setCursorSize(self,size):
		self._debug("Sizing to: {}".format(size))
		xdefault=os.path.join(os.environ.get("HOME"),".Xdefaults")
		xcursor="Xcursor.size: {}\n".format(size)
		fcontents=[]
		if os.path.isfile(xdefault):
			with open(xdefault,"r") as f:
				fcontents=f.readlines()
		newContent=[]
		for line in fcontents:
			if line.startswith("Xcursor.size:")==False:
				line=line.strip()
				newContent.append("{}\n".format(line))
		newContent.append(xcursor)
		with open(xdefault,"w") as f:
			f.writelines(newContent)
		cmd=["xrdb","-merge",xdefault]
		subprocess.run(cmd)
	#def setCursorSize

	def setCursor(self,theme="default",size="",applyChanges=False):
		if theme=="default":
			theme=self.getCursorTheme()
		err=0
		if ("[") in theme:
			theme=theme.split("[")[1].replace("[","").replace("]","")
		os.environ["XCURSOR_THEME"]=theme
		if size!="":
			if (isinstance(size,str))==False:
				size=str(size)
			self.setCursorSize(size)
			try:
				p=Process(target=self._runSetCursorApp,args=(theme,size,))
				p.start()
				p.join()
			except Exception as e:
				print(e)
				err=2
		return(err)
	#def setCursor

	def _runSetCursorApp(self,theme,size):
		cmd=["/usr/share/accesshelper/helper/setcursortheme","-r","1",theme,size]
		subprocess.Popen(cmd,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	#def _runSetCursorApp

	def getCursorTheme(self):
		themes=self.getCursors()
		theme="Adwaita"
		for available in themes:
			if ("(") in available:
				theme=available.split("[")[1].replace("[","").replace("]","")
				theme=theme.split(" ")[0]
				break
		return(theme)
	#def getCursorTheme

	def getCursors(self):
		availableThemes=[]
		themes=""
		try:
			themes=subprocess.run(["plasma-apply-cursortheme","--list-themes"],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
		if themes:
			out=themes.stdout.decode()
			for line in out.split("\n"):
				theme=line.strip()
				if theme.startswith("*"):
					availableThemes.append(theme.replace("*","").strip())
		return(availableThemes)
	#def getCursors

	def getPointerImage(self,theme):
		icon=os.path.join("/usr/share/icons",theme,"cursors","left_ptr")
		self._debug("Extracting imgs for icon {}".format(icon))
		qicon=""
		sizes=[]
		if os.path.isfile(icon)==True:
			tmpDir=tempfile.TemporaryDirectory()
			cmd=["xcur2png","-q","-c","-","-d",tmpDir.name,icon]
			try:
				subprocess.run(cmd,stdout=subprocess.PIPE)
			except Exception as e:
				print("{}".format(e))
			maxw=0
			img=""
			pixmap=""
			for i in os.listdir(tmpDir.name):
				pixmap=os.path.join(tmpDir.name,i)
				qpixmap=QPixmap(pixmap)
				size=qpixmap.size()
				if size.width()>maxw:
					maxw=size.width()
					img=qpixmap
				sizes.append(size)

			if img=="" and pixmap!="":
				img=pixmap
			qicon=QIcon(img)
			tmpDir.cleanup()
		return(qicon,sizes)
	#def getPointerImage

	def setGrubBeep(self,state,onlyPlasma=False):
		sw=True
		if state==True:
			state="enable"
		else:
			state="disable"
		if onlyPlasma==False:
			cmd=["pkexec","/usr/share/accesshelper/helper/enableGrubBeep.sh",state]
			try:
				pk=subprocess.run(cmd)
				if pk.returncode!=0:
					sw=False
			except Exception as e:
				self._debug(e)
				self._debug("Permission denied")
				sw=False
		return sw
	#def setGrubBeep

