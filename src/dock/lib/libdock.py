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
		self.accesshelper=llxaccessibility.client()
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("dock: {}".format(msg))
	#def _debug
	
	def getLaunchers(self):
		app2menu=App2Menu.app2menu()
		launchers=[]
		if os.path.exists(self.launchersPath)==True:
			for f in sorted(os.scandir(self.launchersPath),key=lambda x: x.name):
				if f.name.endswith(".desktop")==False:
					continue
				app=app2menu.get_desktop_info(f.path)
				app.update({"fpath":f.path})
				if app.get("NoDisplay",False)==True:
					continue
				launchers.append((f.name,app))
		return(launchers)
	#def getLaunchers

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
