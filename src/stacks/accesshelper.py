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
	

#class client
