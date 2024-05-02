#!/usr/bin/python3
import subprocess,os
import multiprocessing
import dbus,dbus.exceptions
import tarfile
import tempfile
import shutil
#from PySide2.QtGui import QColor
import json
import random

class client():
	def __init__(self):
		self.dbg=True
		self.bus=None
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("libaccess: {}".format(msg))
	#def _debug

	def _connectBus(self):
		try:
			self.bus=dbus.Bus()
		except Exception as e:
			print("Could not get session bus: %s\nAborting"%e)
			sys.exit(1)
	#def _connectBus

	def _readMetadataDesktop(self,path):
		data={}
		with open(path,"r") as f:
			fdata=f.readlines()
		if len(fdata)>0:
			data.update({"KPackageStructure":"KWin/Effect"})
			data.update({"KPlugin":{}})
			for line in fdata:
				fields=line.split("=")
				if fields[0]=="Name":
					data["KPlugin"].update({fields[0]:fields[1].strip()})
				elif fields[0]=="Comment":
					data["KPlugin"].update({"Description":fields[1].strip()})
				elif fields[0]=="Icon":
					data["KPlugin"].update({fields[0]:fields[1].strip()})
				elif fields[0]=="X-KDE-ServiceTypes":
					data["KPackageStructure"]=fields[1].strip()
				elif fields[0]=="X-KDE-PluginInfo-Name":
					data["KPlugin"].update({"Id":fields[1].strip()})
				elif fields[0]=="X-KDE-PluginInfo-Category":
					data["KPlugin"].update({"Category":fields[1].strip()})
		return(data)
	#def _readMetadataDesktop

	def _readMetadataJson(self,path):
		data="{}"
		with open(path,"r") as f:
			data=f.read()
		data=json.loads(data)
		return(data)
	#def _readMetadataJson

	def _readMetadata(self,path):
		metapath=""
		data={}
		exts=["json","desktop"]
		if os.path.isdir(path):
			for ext in exts:
				if os.path.isfile(os.path.join(path,"metadata.{}".format(ext))):
					metapath=os.path.join(path,"metadata.{}".format(ext))
					break
		else:
			for ext in exts:
				if os.path.basename(path)=="metadata.{}".format(ext) and os.path.isfile(path):
					metapath=path
					break
		if metapath.endswith(".json"):
			data=self._readMetadataJson(metapath)
		elif metapath.endswith(".desktop"):
			data=self._readMetadataDesktop(metapath)
		return(data)
	#def _readMetadata

	def _getKWinEffects(self):
		paths=["/usr/share/kwin/builtin-effects","/usr/share/kwin/effects",os.path.join(os.getenv("HOME"),".local","share","kwin","effects")]
		effects={}
		for i in paths:
			if os.path.exists(i):
				for effect in os.scandir(i):
					data=self._readMetadata(effect.path)
					if len(data)>0:
						if "KPackageStructure" not in data:
							data["KPackageStructure"]="KWin/Effect"
						effects.update({effect.name:data})
		return(effects)
	#def getKWinEffects

	def _getKWinScripts(self):
		paths=["/usr/share/kwin/scripts",os.path.join(os.getenv("HOME"),".local","share","kwin","scripts")]
		scripts={}
		for i in paths:
			if os.path.exists(i):
				for script in os.scandir(i):
					data=self._readMetadata(script.path)
					scripts.update({script.name:data})
		return(scripts)
	#def _getKWinScripts(self):

	def getKWinPlugins(self,categories=["Accessibility"]):
		plugins={}
		plugins.update(self._getKWinEffects())
		plugins.update(self._getKWinScripts())
		if len(categories)>0:
			filteredplugins={}
			for plugin,data in plugins.items():
				if len(data)==0 or "KPackageStructure" not in data:
					continue
				if data["KPackageStructure"]=="KWin/Effect":
					if data["KPlugin"].get("Category") in categories:
						filteredplugins.update({plugin:data})
				else:
					filteredplugins.update({plugin:data})
			plugins=filteredplugins.copy()
		return(plugins)
	#def getKWinPlugins

	def _getDbusInterfaceForPlugin(self,plugin):
		plugtype=plugin.get("KPackageStructure","")
		dwin=None
		dinterface=None
		if len(plugtype)>0:
			plugid=plugin.get("KPlugin",{}).get("Id","")
			if self.bus==None:
				self._connectBus()
			if "Script" in plugtype:
				dobject="/Scripting"
				dinterface="org.kde.kwin.Scripting"
			else:
				dobject="/Effects"
				dinterface="org.kde.kwin.Effects"
			try:
				dwin=self.bus.get_object("org.kde.KWin",dobject)
			except Exception as e:
				print("Could not connect to bus: %s\nAborting"%e)
				sys.exit(1)
		return(dwin,dinterface)
	#def _getDbusInterfaceForPlugin

	def getPluginEnabled(self,plugin):
		enabled=False
		(dKwin,dInt)=self._getDbusInterfaceForPlugin(plugin)
		if dKwin==None or dInt==None:
			return
		plugid=plugin.get("KPlugin",{}).get("Id","")
		if "Script" in plugin.get("KPackageStructure",""):
			if dKwin.isScriptLoaded(plugid)==1:
				enabled=True
		else:
			if dKwin.isEffectLoaded(plugid)==1:
				enabled=True
		return(enabled)
	#def getPluginEnabled

	def _writeKwinrc(self,group,key,data):
		cmd=["kwriteconfig5","--file","kwinrc","--group",group,"--key",key,data]
		out=subprocess.check_output(cmd)
		self._debug(out)
	#def _writeKwinrc

	def togglePlugin(self,plugin):
		enabled=False
		(dKwin,dInt)=self._getDbusInterfaceForPlugin(plugin)
		if dKwin==None or dInt==None:
			return
		plugid=plugin.get("KPlugin",{}).get("Id","")
		if plugin.get("KPackageStructure","")=="KWin/Script":
			if dKwin.isScriptLoaded(plugid)==0:
				enabled=True
			self._writeKwinrc("Plugins","{}Enabled".format(plugid),str(enabled).lower())
			self._debug("Script {} enabled: {}".format(plugid,enabled))
			self.applyKWinChanges()
		else:
			dKwin.toggleEffect(plugid)
			if dKwin.isEffectLoaded(plugid)==1:
				enabled=True
			self._debug("Effect {} enabled: {}".format(plugid,enabled))
		return(enabled)
	#def togglePlugin

	def applyKWinChanges(self):
		if self.bus==None:
			self._connectBus()
		dobject="/KWin"
		dInt="org.kde.kwin.reconfigure"
		dKwin=self.bus.get_object("org.kde.KWin",dobject)
		self._debug("Reloading kwin")
		dKwin.reconfigure()
	#def applyKWinChanges

	def _mpLaunchCmd(self,cmd):
		try:
			subprocess.run(cmd)
		except Exception as e:
			print (e)
	#def _mpLaunchKcm

	def launchKcmModule(self,kcmModule,mp=False):
		cmd=["kcmshell5",kcmModule]
		self.launchCmd(cmd,mp)
	#def launchKcmModule

	def launchCmd(self,cmd,mp=False):
		if mp==True:
			mp=multiprocessing.Process(target=self._mpLaunchCmd,args=(cmd,))
			mp.start()
		else:
			self._mpLaunchCmd(cmd)
	#def launchCmd

	def _generateProfileDirs(self,pname):
		tmpDirs={}
		#Generate tmp folders
		tmpFolder=tempfile.mkdtemp()
		tmpDirs.update({"tmp":tmpFolder})
		#Plasma config goes to .config
		plasmaPath=os.path.join(tmpFolder,".config")
		os.makedirs(plasmaPath)
		tmpDirs.update({"plasma":plasmaPath})
		#accesshelper to .config/accesshelper
		configPath=os.path.join(tmpFolder,".config/accesswizard")
		#onboard=os.path.join(os.path.dirname(appconfrc),"onboard.dconf")
		os.makedirs(configPath)
		tmpDirs.update({"config":configPath})
		#autostart
		desktopStartPath=os.path.join(tmpFolder,".config/autostart")
		os.makedirs(desktopStartPath)
		#autostartPath=os.path.join(home,".config","autostart")
		tmpDirs.update({"autostart":desktopStartPath})
		#autoshutdown
		desktopShutdownPath=os.path.join(tmpFolder,".config/plasma-workspace/shutdown")
		os.makedirs(desktopShutdownPath)
		#autoshutdownPath=os.path.join(home,".config",".config/plasma-workspace/shutdown")
		tmpDirs.update({"autoshutdown":desktopShutdownPath})
		#mozilla
		mozillaPath=os.path.join(tmpFolder,".mozilla")
		os.makedirs(mozillaPath)
		tmpDirs.update({"mozilla":mozillaPath})
		#gtk
		gtkPath=os.path.join(tmpFolder,".config")
		if os.path.isdir(gtkPath)==False:
			os.makedirs(gtkPath)
		tmpDirs.update({"gtk":gtkPath})
		return(tmpDirs)
	#def _generateProfileDirs

	def _copyKFiles(self,plasmaPath):
		klist=["kcminputrc","konsolerc","kglobalshortcutsrc","khotkeys","kwinrc","kaccessrc"]
		for kfile in klist:
			kPath=os.path.join(os.environ['HOME'],".config",kfile)
			if os.path.isfile(kPath):
				shutil.copy(kPath,plasmaPath)
	#def _copyKFiles(self):

	def _copyAccessConfig(self,configPath):
		conf=os.path.join(os.environ.get("HOME"),".config","accesswizard")
		if os.path.exists(conf):
			for f in os.scandir(conf):
				if os.path.isdir(f.path):
					continue
				shutil.copy(f.path,configPath)
	#def _copyAccessConfig

	def _copyStartShutdown(self,desktopstartPath,desktopshutdownPath):
		autoshutdownPath=os.path.join(os.environ.get("HOME"),".config",".config/plasma-workspace/shutdown")
		autostartPath=os.path.join(os.environ.get("HOME"),".config",".config/autostart")
		for auto in [autostartPath,autoshutdownPath]:
			if os.path.isdir(auto):
				for f in os.listdir(auto):
					if f.startswith("access"):
						autostart=os.path.join(auto,f)
						if auto==autostartPath:
							shutil.copy(autostart,desktopStartPath)
						else:
							shutil.copy(autostart,desktopShutdownPath)
	#def _copyStartShutdown

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

	def _copyMozillaFiles(self,mozillaPath):
		mozillaFiles=self._getMozillaSettingsFiles()
		for mozillaFile in mozillaFiles:
			destdir=os.path.basename(os.path.dirname(mozillaFile))
			destdir=os.path.join(mozillaPath,destdir)
			os.makedirs(destdir)
			shutil.copy(mozillaFile,destdir)
	#def _copyMozillaFiles

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

	def _copyGtkFiles(self,gtkPath):
		gtkFiles=self._getGtkSettingsFiles(True)
		for gtkFile in gtkFiles:
			destdir=os.path.basename(os.path.dirname(gtkFile))
			destdir=os.path.join(gtkPath,destdir)
			os.makedirs(destdir)
			shutil.copy(gtkFile,destdir)
	#def _copyGtkFiles(self):

	def _copyTarProfile(self,orig,dest):
		if os.path.isdir(os.path.dirname(dest))==False:
			os.makedirs(os.path.dirname(dest))
		try:
			shutil.copy(orig,dest)
		except Exception as e:
			self._debug(e)
			self._debug("Permission denied for {}".format(dest))
			sw=False
	#def _copyTarProfile
	
	def saveProfile(self,pname="profile"):
		profDir=os.path.join(os.environ.get("HOME"),".local","share","accesswizard","profiles",pname)
		profiles=[]
		if os.path.exists(os.path.dirname(profDir))==False:
			os.makedirs(profDir)
		if os.path.exists(profDir)==True:
			shutil.rmtree(profDir)
		os.makedirs(profDir)
		self._debug("Saving profile {}".format(profDir))
		profDirs=self._generateProfileDirs(pname)
		self._copyKFiles(profDirs["plasma"])
		self._copyAccessConfig(profDirs["config"])
		self._copyStartShutdown(profDirs["autostart"],profDirs["autoshutdown"])
		self._copyMozillaFiles(profDirs["mozilla"])
		self._copyGtkFiles(profDirs["gtk"])
		(osHdl,tmpFile)=tempfile.mkstemp()
		oldCwd=os.getcwd()
		tmpFolder=profDirs["tmp"]
		os.chdir(tmpFolder)
		with tarfile.open(tmpFile,"w") as tarFile:
			for f in os.listdir(tmpFolder):
				tarFile.add(os.path.basename(f))
		os.chdir(oldCwd)
		if profDir.endswith(".tar")==False:
			profDir+=".tar"
		self._debug("Copying {0}->{1}".format(tmpFile,profDir))
		self._copyTarProfile(tmpFile,profDir)
		os.remove(tmpFile)
		return(os.path.join(profDir,os.path.basename(tmpFile)))
	#def take_snapshot

#class client
