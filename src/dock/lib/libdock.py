#!/usr/bin/python3

#Library for handling desktop files for accessdock
import os,sys
from app2menu import App2Menu

class libdock():
	def __init__(self):
		self.dbg=False
		self.launchersPath=os.path.join(os.environ.get("HOME"),".config","accessibility","launchers")
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
				if app.get("NoDisplay",False)==True:
					continue
				launchers.append((f.name,app))
		return(launchers)
#class libdock
