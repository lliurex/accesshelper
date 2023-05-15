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

class plasmaHelperClass():
	def __init__(self):
		self.dbg=False
		self.dictFileData={}
		self._initValues()
		self.tmpDir="/tmp/.accesstmp"

	def _initValues(self):
		plugins=[("invertEnabled",""),("invertWindow",""),("magnifierEnabled",""),("lookingglassEnabled",""),("trackmouseEnabled",""),("zoomEnabled",""),("snaphelperEnabled",""),("mouseclickEnabled","")]
		windows=[("FocusPolicy","")]
		kde=[("singleClick",""),("ScrollbarLeftClickNavigatesByPage","")]
		bell=[("SystemBell",""),("VisibleBell","")]
		hotkeys_kwin=[("ShowDesktopGrid",""),("Invert",""),("InvertWindow",""),("ToggleMouseClick",""),("TrackMouse",""),("view_zoom_in",""),("view_zoom_out","")]
		hotkeys_dock=[("_launch","")]
		kgammaConfig=[("use","")]
		kgammaValues=[("bgamma",""),("rgamma",""),("ggamma","")]
		kgammaSync=[("sync","")]
		mouse=[("cursorSize","")]
		general=[("Name",""),("fixed",""),("font",""),("menuFont",""),("smallestReadableFont",""),("toolBarFont","")]
		self.dictFileData={"kaccesrc":{"Bell":bell},"kwinrc":{"Plugins":plugins,"Windows":windows},"kdeglobals":{"KDE":kde,"General":general},"kglobalshortcutsrc":{"kwin":hotkeys_kwin,"accessdock.desktop":hotkeys_dock},"kcminputrc":{"Mouse":mouse},"kgammarc":{"ConfigFile":kgammaConfig,"Screen 0":kgammaValues,"SyncBox":kgammaSync}}
		self.settingsHotkeys={"invertWindow":"InvertWindow","invertEnabled":"Invert","trackmouseEnabled":"TrackMouse","mouseclickEnabled":"ToggleMouseClick","view_zoom_in":"","view_zoom_out":""}
	#def _initValues

	def _debug(self,msg):
		if self.dbg:
			print("libhelper: {}".format(msg))
	#def _debug

	def _getEnv(self,values={}):
		env=os.environ
		if len(values)>0 and isinstance(values,dict):
			env.update(values)
		elif env.get("XCURSOR_SIZE","")!="":
			env.pop("XCURSOR_SIZE")
		return(env)
	#def _getEnv

	def getPlasmaConfig(self,wrkFile='',sourceFolder=''):
		if sourceFolder:
			self._debug("Reading kfiles from {}".format(sourceFolder))
		dictValues={}
		data=''
		if wrkFile:
			if self.dictFileData.get(wrkFile,None):
				data={wrkFile:self.dictFileData[wrkFile].copy()}
		if isinstance(data,str):
			data=self.dictFileData.copy()
		for kfile,groups in data.items():
			for group,settings in groups.items():
				settingData=[]
				for setting in settings:
					key,value=setting
					value=self.getKdeConfigSetting(group,key,kfile,sourceFolder)
					settingData.append((key,value))
					self._debug("Wrting {0}->{1}".format(key,value))
				data[kfile].update({group:settingData})
		return (data)
	#def getPlasmaConfig

	def getKdeConfigSetting(self,group,key,kfile="kaccessrc",sourceFolder=''):
		if sourceFolder=='':
			sourceFolder=os.path.join(os.environ.get('HOME',"/usr/share/acccessibility"),".config")
		kPath=os.path.join(sourceFolder,kfile)
		value=""
		if os.path.isfile(kPath):
			cmd=["kreadconfig5","--file",kPath,"--group",group,"--key",key]
			try:
				value=subprocess.check_output(cmd,universal_newlines=True).strip()
			except Exception as e:
				print(e)
		self._debug("Read value: {}".format(value))
		return(value)
	#def getKdeConfigSetting

	def getHotkey(self,setting):
		hk=""
		hksection=""
		data=""
		name=""
		self._debug("Hotkey for {}".format(setting))
		hksetting=self.settingsHotkeys.get(setting,"")
		sc=self.getPlasmaConfig(wrkFile="kglobalshortcutsrc")
		if hksetting:
			sw=False
			for kfile,sections in sc.items():
				for section,settings in sections.items():
					hksection=section
					for setting in settings:
						(name,data)=setting
						if name.lower()==hksetting.lower():
							data=data.split(",")
							hk=data[0]
							data=",".join(data)
							sw=True
							break
					if sw==True:
						break
				if sw==True:
					break
		else:
			for kfile,sections in sc.items():
				if setting.lower() in sections.keys():
					(name,data)=sections[setting][0]
					if name.lower()=="_launch":
						data=data.split(",")
						hk=data[0]
						hksection=setting
						data=",".join(data)
		return(hk,data,name,hksection)
	#def getHotkey

	def getSettingForHotkey(self,hotkey):
		kfile="kglobalshortcutsrc"
		assigned=""
		sourceFolder=os.path.join(os.environ.get('HOME',"/usr/share/acccessibility"),".config")
		kPath=os.path.join(sourceFolder,kfile)
		with open(kPath,"r") as f:
			lines=f.readlines()
		for line in lines:
			if len(line.split(","))>2:
				if hotkey.lower()==line.split(",")[-2].lower():
					assigned=line.split(",")[-1]
					break
		return(assigned)
	#def getSettingForHotkey

	def setHotkey(self,hotkey,desc,name):
		cmd=name.replace(".desktop","")
		hotkey=hotkey.replace("Any","Space")
		if desc=="":
			data=""
		else:
			desc="{0},none,{1}".format(hotkey,desc)
			data=[("_launch",desc),("_k_friendly_name",cmd)]
		config={'kglobalshortcutsrc':{name:data}}
		self.setPlasmaConfig(config)
	#def setHotkey
				
	def _getMozillaSettingsFiles(self):
		mozillaFiles=[]
		mozillaDir=os.path.join(os.environ.get('HOME',''),".mozilla/firefox")
		if os.path.isdir(mozillaDir)==True:
			for mozillaF in os.listdir(mozillaDir):
				self._debug("Reading MOZILLA {}".format(mozillaF))
				fPath=os.path.join(mozillaDir,mozillaF)
				if os.path.isdir(fPath):
					self._debug("Reading DIR {}".format(mozillaF))
					if "." in mozillaF:
						self._debug("Reading DIR {}".format(mozillaF))
						prefs=os.path.join(mozillaDir,mozillaF,"prefs.js")
						if os.path.isfile(prefs):
							mozillaFiles.append(prefs)
		return mozillaFiles
	#def _getMozillaSettingsFiles

	def _getGtkSettingsFiles(self,checkExists=False):
		gtkFiles=[]
		gtkDirs=[os.path.join("/home",os.environ.get('USER',''),".config/gtk-3.0"),os.path.join("/home",os.environ.get('USER',''),".config/gtk-4.0")]
		for gtkDir in gtkDirs:
			if checkExists==False:
				gtkFiles.append(os.path.join(gtkDir,"settings.ini"))
			elif os.path.isfile(os.path.join(gtkDir,"settings.ini"))==True:
				gtkFiles.append(os.path.join(gtkDir,"settings.ini"))
		return gtkFiles
	#def _getGtkFiles

	def setKdeConfigSetting(self,group,key,value,kfile="kaccessrc",tmpDir=''):
		#kfile=kaccessrc
		#_debug("Writing value {} from {} -> {}".format(key,kfile,value))
		if tmpDir!='':
			if tmpDir.startswith("/tmp/.accesshelper")==False:
				tmpDir=os.path.join("/tmp/.accesshelper",tmpDir)
			if os.path.isdir(tmpDir)==False:
				os.makedirs(tmpDir)
			kfilePath=os.path.join(tmpDir,kfile)
		else:
			kfilePath=os.path.join(os.environ['HOME'],".config",kfile)
		if os.path.isfile(kfile)==False and kfile.endswith(".profile"):
			kfilePath=os.path.join(os.environ['HOME'],".local/share/konsole/",kfile)
		if len(value):
			cmd=["kwriteconfig5","--file",kfilePath,"--group",group,"--key",key,"{}".format(value)]
		else:
			cmd=["kwriteconfig5","--file",kfilePath,"--group",group,"--key",key,"--delete"]
		self._debug("Write command: {}".format(" ".join(cmd)))
		ret='false'
		try:
			ret=subprocess.run(cmd,universal_newlines=True)
		except Exception as e:
			print(e)
		self._debug("Write value: {}".format(ret))
		return(ret)
	#def setKdeConfigSetting

	def setPlasmaConfig(self,config,tmpDir=''):
		self._debug("ConfDir: {0} Config: {1}".format(tmpDir,config))
		for kfile,sections in config.items():
			for section,data in sections.items():
				self._debug("Section {}".format(section))
				self._debug("Data {}".format(data))
				for setting in data:
					try:
						(desc,value)=setting
					except Exception as e:
						print("Error on setting {}".format(setting))
						print(e)
						desc=""
					if desc=="":
						continue
					self._debug("Setting {0} -> {1}, Files: {2} {3}".format(desc,value,kfile,tmpDir))
					self.setKdeConfigSetting(section,desc,value,kfile,tmpDir=tmpDir)
	#def setPlasmaConfig

	def consolidatePlasmaConfig(self):
		self._debug("Consolidating plasma config")
		self._loadPlasmaConfigFromFolder(self.tmpDir)
	#def consolidatePlasmaConfig(self):

	def _loadPlasmaConfigFromFolder(self,folder):
		if os.path.isdir(folder)==True:
			config=self.getPlasmaConfig(sourceFolder=folder)
			for kfile,sections in config.items():
				for section,data in sections.items():
					for (desc,value) in data:
						self.setKdeConfigSetting(section,desc,value,kfile)
	#def _loadPlasmaConfigFromFolder

	def setBackgroundColor(self,qcolor):
		(r,g,b,alpha)=qcolor.getRgbF()
		r=int(r*255)
		g=int(g*255)
		b=int(b*255)
		color="{0},{1},{2}".format(r,g,b)
		plugin='org.kde.color'
		jscript = """
		var allDesktops = desktops();
		print (allDesktops);
		for (i=0;i<allDesktops.length;i++) {
			d = allDesktops[i];
			d.wallpaperPlugin = "%s";
			d.currentConfigGroup = Array("Wallpaper", "%s", "General");
			d.writeConfig("Color", "%s")
		}
		"""
		bus = dbus.SessionBus()
		try:
			plasma = dbus.Interface(bus.get_object(
			'org.kde.plasmashell', '/PlasmaShell'), dbus_interface='org.kde.PlasmaShell')
			plasma.evaluateScript(jscript % (plugin, plugin, color))
		except:
			print("Plasma dbus error")
	#def setBackgroundColor

	def setBackgroundImg(self,imgFile):
		plugin='org.kde.image'
		jscript = """
		var allDesktops = desktops();
		print (allDesktops);
		for (i=0;i<allDesktops.length;i++) {
			d = allDesktops[i];
			d.wallpaperPlugin = "%s";
			d.currentConfigGroup = Array("Wallpaper", "%s", "General");
			d.writeConfig("Image", "%s")
		}
		"""
		bus = dbus.SessionBus()
		try:
			plasma = dbus.Interface(bus.get_object(
				'org.kde.plasmashell', '/PlasmaShell'), dbus_interface='org.kde.PlasmaShell')
			plasma.evaluateScript(jscript % (plugin, plugin, imgFile))
		except:
			print("plasmashell not running")
	#def setBackgroundImg

	def setScaleFactor(self,scaleFactor,xrand=False,plasma=True):
		if plasma==False:
			return
		self._debug("Setting plasma scale factor...")
		cmd=["xrandr","--listmonitors"]
		output=subprocess.run(cmd,capture_output=True,text=True)
		monitors=[]
		for line in output.stdout.split("\n"):
			if len(line.split(" "))>=4:
				monitors.append("{0}".format(line.split(" ")[-1]))
		if monitors:
			monitorsScale=[]
			for monitor in monitors:
				monitorsScale.append("{0}={1}".format(monitor,scaleFactor))
			screenScaleFactors="{};".format(";".join(monitorsScale))
			self.setKdeConfigSetting("KScreen","ScreenScaleFactors",screenScaleFactors,"kdeglobals")
		if scaleFactor==1:
			scaleFactor=""
		self.setKdeConfigSetting("KScreen","ScaleFactor",str(scaleFactor),"kdeglobals")
	#def setScaleFactor

	def removeAutostartDesktop(self,desktop,folder="autostart"):
		home=os.environ.get("HOME")
		if home:
			if "shutdown" in folder:
				desktop=desktop.replace(".desktop",".sh")
			wrkFile=os.path.join(home,".config",folder,desktop)
			if os.path.isfile(wrkFile):
				os.remove(wrkFile)
	#def _removeAutostartDesktop

	def generateAutostartDesktop(self,cmd,fname,folder="autostart"):
		desktop=[]
		if "shutdown" in folder:
			if isinstance(cmd,list):
				cmd=" ".join(cmd)
			cmd="#!/bin/bash\n{}".format(cmd)
			fname=fname.replace(".desktop",".sh")
			desktop=cmd.split("\n")
		else:
			if isinstance(cmd,list):
				cmd=" ".join(cmd)
			desktop.append("[Desktop Entry]")
			desktop.append("Encoding=UTF-8")
			desktop.append("Type=Application")
			desktop.append("Name={}".format(fname.replace(".desktop","")))
			desktop.append("Comment=Apply rgb filters")
			desktop.append("Exec={}".format(cmd))
			desktop.append("StartupNotify=false")
			desktop.append("Terminal=false")
			desktop.append("Hidden=false")
		home=os.environ.get("HOME")
		if home:
			wrkFile=os.path.join(home,".config",folder,fname)
			if os.path.isdir(os.path.dirname(wrkFile))==False:
				os.makedirs(os.path.dirname(wrkFile))
			with open(wrkFile,"w") as f:
				f.write("\n".join(desktop))
			if "shutdown" in folder:
				os.chmod(wrkFile,0o755)
	#def generateAutostartDesktop

	def removeRGBFilter(self):
		values=[("ggamma","1.00"),("bgamma","1.00"),("rgamma","1.00")]
		plasmaConfig={'kgammarc':{'Screen 0':values}}
		self.setPlasmaConfig(plasmaConfig)
		self.removeAutostartDesktop("accesshelper_rgbFilter.desktop")
	#def resetRGBFilter

	def setRGBFilter(self,red,green,blue,onlyset=False):
		values=[]
		plasmaConfig={}
		values.append(("bgamma","{0:.2f}".format(blue)))
		values.append(("rgamma","{0:.2f}".format(red)))
		values.append(("ggamma","{0:.2f}".format(green)))
		plasmaConfig['kgammarc']={'ConfigFile':[("use","kgammarc")]}
		plasmaConfig['kgammarc'].update({'SyncBox':[("sync","yes")]})
		plasmaConfig['kgammarc'].update({'Screen 0':values})
		self.setPlasmaConfig(plasmaConfig)
	#def setRGBFilter

	def setCursorSize(self,size):
		self._debug("Sizing to: {}".format(size))
		self.setKdeConfigSetting("Mouse","cursorSize","{}".format(size),"kcminputrc")
	#def setCursorSize

	def setCursor(self,theme="default",size="",applyChanges=False,commitChanges=True):
		if theme=="default":
			theme=self.getCursorTheme()
		if (isinstance(size,str))==False:
			size=str(size)
		err=0
		if ("[") in theme:
			theme=theme.split("[")[1].replace("[","").replace("]","")
		if commitChanges==True:
			if size!="":
				self.setCursorSize(size)
		if applyChanges==True:
			self._debug("Set theme: {}".format(theme))
			env=self._getEnv({"XCURSOR_SIZE":size,"XCURSOR_THEME":theme})
			try:
				subprocess.run(["plasma-apply-cursortheme",theme],stdout=subprocess.PIPE,env=env)
			except Exception as e:
				print(e)
				err=1
			try:
				cmd=["qdbus","org.kde.klauncher5","/KLauncher","org.kde.KLauncher.setLaunchEnv","XCURSOR_THEME",theme]
				subprocess.run(cmd,stdout=subprocess.PIPE,env=env)
				cmd=["qdbus","org.kde.klauncher5","/KLauncher","org.kde.KLauncher.setLaunchEnv","XCURSOR_SIZE",size]
				subprocess.run(cmd,stdout=subprocess.PIPE,env=env)
			except Exception as e:
				print(e)
				err=3
		return(err)
	#def setCursor

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

	def getSchemes(self):
		availableSchemes=[]
		schemes=""
		try:
			schemes=subprocess.run(["plasma-apply-colorscheme","--list-schemes"],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
		if schemes:
			out=schemes.stdout.decode()
			for line in out.split("\n"):
				scheme=line.strip()
				if scheme.startswith("*"):
					availableSchemes.append(scheme.replace("*","").strip())
		return availableSchemes
	#def getSchemes

	def getThemes(self):
		availableThemes=[]
		themes=""
		try:
			themes=subprocess.run(["plasma-apply-desktoptheme","--list-themes"],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
		if themes:
			out=themes.stdout.decode()
			for line in out.split("\n"):
				theme=line.strip()
				if theme.startswith("*"):
					availableThemes.append(theme.replace("*","").strip())
		return (availableThemes)
	#def getThemes

	def setStartBeep(self,state):
		if state==True:
			state="enable"
		else:
			state="disable"
		if state=="enable":
			config={"plasma_workspace.notifyrc":{"Event/startkde":[("Action","Sound")]}}
			config["plasma_workspace.notifyrc"].update({"Event/exitkde":[("Action","Sound")]})
		else:
			config={"plasma_workspace.notifyrc":{"Event/startkde":[("Action","")]}}
			config["plasma_workspace.notifyrc"].update({"Event/exitkde":[("Action","")]})
		self.setPlasmaConfig(config)
	#def setStartBeep

	def _setThemeSchemeLauncher(self,*args,theme="",scheme=""):
		home=os.environ.get('HOME')
		if home:
			autostart=os.path.join(home,".config/autostart")
			if os.path.isdir(autostart)==False:
				os.makedirs(autostart)
			desktop="accesshelper_thematizer.desktop"
			source=os.path.join("/usr/share/accesshelper/helper/",desktop)
			destpath=os.path.join(autostart,desktop)
			content=[]
			newcontent=[]
			if os.path.isfile(destpath):
				with open(destpath,'r') as f:
					content=f.readlines()
				if "".join(content).strip()=="":
					content=[]
			if content==[]:
				if os.path.isfile(source):
					with open(source,'r') as f:
						content=f.readlines()
			for line in content:
				newline=line
				if line.startswith("Exec="):
					array=line.split(" ")
					if theme:
						array[1]=theme
					if scheme:
						array[2]=scheme
					newline=" ".join(array)
				newcontent.append(newline)
			with open(destpath,'w') as f:
				f.writelines(newcontent)
				f.write("\n")
	#def _setThemeSchemeLauncher

	def applyChanges(self):
		env=self._getEnv()
		cmd=["killall","kwin_x11"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
		cmd=["qdbus","org.kde.kded","/kded","unloadModule","powerdevil"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
		cmd=["qdbus","org.kde.keyboard","/modules/khotkeys","reread_configuration"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
		cmd=["qdbus","org.kde.kded","/kbuildsycoca","recreate"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
		cmd=["qdbus","org.kde.kded","/kded","reconfigure"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
		cmd=["qdbus","org.kde.plasma-desktop","/MainApplication","reparseConfiguration"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
		cmd=["qdbus","org.kde.kded","/kded","loadModule","powerdevil"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
		cmd=["qdbus","org.kde.kglobalaccel","/MainApplication","quit"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
		cmd=["kstart5","kglobalaccel5"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
		cmd=["qdbus","org.kde.plasmashell","/PlasmaShell","refreshCurrentShell"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["kstart5","kwin_x11"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
		print("Changes applied!")

