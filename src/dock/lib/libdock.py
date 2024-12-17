#!/usr/bin/python3

#Library for handling desktop files for accessdock
import os,sys
from app2menu import App2Menu
import subprocess
from llxaccessibility import llxaccessibility

class libdock():
	def __init__(self):
		self.dbg=False
		self.launchersPath=os.path.join(os.environ.get("HOME"),".local","accesswizard","launchers")
		self.defaultPath=os.path.join("/","usr","share","accesswizard","dock","default")
		self.accesshelper=llxaccessibility.client()
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("dock: {}".format(msg))
	#def _debug

	def _loadLaunchersFromPath(self,path):
		app2menu=App2Menu.app2menu()
		launchers=[]
		if os.path.exists(path)==True:
			for f in sorted(os.scandir(path),key=lambda x: x.name):
				if f.name.endswith(".desktop")==False:
					continue
				app=app2menu.get_desktop_info(f.path)
				app.update({"fpath":f.path})
				if app.get("NoDisplay",False)==True:
					continue
				launchers.append((f.name,app))
		return(launchers)
	#def _loadLaunchersFromPath

	def getLaunchers(self):
		launchers=self._loadLaunchersFromPath(self.launchersPath)
		if len(launchers)==0 and os.path.exists(self.launchersPath)==False:
			self.initLaunchers()
			launchers=self._loadLaunchersFromPath(self.launchersPath)
		return(launchers)
	#def getLaunchers

	def loadDefaultLaunchers(self):
		launchers=self._loadLaunchersFromPath(self.defaultPath)
	#def loadDefaultLaunchers

	def initLaunchers(self):
		if os.path.exists(self.launchersPath):
			for f in os.scandir(self.launchersPath):
				os.unlink(f.path)
		if os.path.exists(self.defaultPath):
			if os.path.exists(self.launchersPath)==False:
				os.makedirs(self.launchersPath)
			for f in os.scandir(self.defaultPath):
				with open(f.path,"r") as defaultF:
					defContent=defaultF.read()
				with open(os.path.join(self.launchersPath,f.name),"w") as initF:
					initF.write(defContent)
	#def initLaunchers

	def getShortcut(self):
		cmd=["kreadconfig5","--file","kglobalshortcutsrc","--group","net.lliurex.accessibledock.desktop","--key","_launch"]
		out=subprocess.check_output(cmd,encoding="utf8",universal_newlines=True)
		return(out.strip())
	#def getShortcut

	def setShortcut(self,hkey):
		appname="accessibledock"
		cmdargs="{0},{0},{1}.desktop".format(hkey,appname)
		cmd=["kwriteconfig5","--file","kglobalshortcutsrc","--group","net.lliurex.accessibledock.desktop","--key","_launch",cmdargs]
		try:
			subprocess.check_call(cmd)
		except Exception as e:
			print("Failed to set shortcut")
			print(e)
		else:
			try:
				cmd=["kwriteconfig5","--file","kglobalshortcutsrc","--group","net.lliurex.accessibledock.desktop","--key","_k_friendly_name",appname]
				subprocess.run(cmd)
			except Exception as e:
				print(e)
	#def setShortcut

	def writeKValue(self,kfile,kgroup,key,value):
		self.accesshelper.writeKFile(kfile,kgroup,key,value)
	#def writeKValue

	def readKValue(self,kfile,kgroup,key):
		out=self.accesshelper.readKFile(kfile,kgroup,key)
		return(out)
	#def readKValue

	def getDockEnabled(self):
		return(self.accesshelper.getDockEnabled())
	#def getDockEnabled

	def setDockEnabled(self,*args):
		return(self.accesshelper.setDockEnabled(args))
	#def getDockEnabled
#class libdock
