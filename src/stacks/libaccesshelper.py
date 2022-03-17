#!/usr/bin/python3
import subprocess,os
import tarfile
import tempfile
import shutil

class functionHelperClass():
	def __init__(self):
		self.dbg=True
		self.dictFileData={}
		self._initValues()

	def _initValues(self):
		plugins=[("invertEnabled",""),("invertWindow",""),("magnifierEnabled",""),("lookingglassEnabled",""),("trackmouseEnabled",""),("zoomEnabled",""),("snaphelperEnabled",""),("mouseclickEnabled","")]
		windows=[("FocusPolicy","")]
		kde=[("singleClick",""),("ScrollbarLeftClickNavigatesByPage","")]
		bell=[("SystemBell",""),("VisibleBell","")]
		hotkeys_kwin=[("ShowDesktopGrid",""),("Invert",""),("InvertWindow",""),("ToggleMouseClick",""),("TrackMouse",""),("view_zoom_in",""),("view_zoom_out","")]
		kgammaConfig=[("use","")]
		kgammaValues=[("bgamma",""),("rgamma",""),("ggamma","")]
		kgammaSync=[("sync","")]
		mouse=[("cursorSize","")]
		general=[("Name",""),("fixed",""),("font",""),("menuFont",""),("smallestReadableFont",""),("toolBarFont","")]
		self.dictFileData={"kaccesrc":{"Bell":bell},"kwinrc":{"Plugins":plugins,"Windows":windows},"kdeglobals":{"KDE":kde,"General":general},"kglobalshortcutsrc":{"kwin":hotkeys_kwin},"kcminputrc":{"Mouse":mouse},"kgammarc":{"ConfigFile":kgammaConfig,"Screen 0":kgammaValues,"SyncBox":kgammaSync}}
		self.settingsHotkeys={"invertWindow":"InvertWindow","invertEnabled":"Invert","trackmouseEnabled":"TrackMouse","mouseclickEnabled":"ToggleMouseClick","view_zoom_in":"","view_zoom_out":""}
	#def _initValues

	def _debug(self,msg):
		if self.dbg:
			print("libaccess: {}".format(msg))

	def cssStyle(self):
		style="""
			QListWidget{
				}
			QListWidget::item{
				margin:3px;
				padding:3px;
				}
		"""
		return(style)

	def getSystemConfig(self,wrkFile='',sourceFolder=''):
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
				data[kfile].update({group:settingData})
		return (data)

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
		#_debug("Read value: {}".format(value))
		return(value)

	def getHotkey(self,setting):
		hk=""
		hksection=""
		data=""
		name=""
		hksetting=self.settingsHotkeys.get(setting,"")
		if hksetting:
			sc=self.getSystemConfig(wrkFile="kglobalshortcutsrc")
			for kfile,sections in sc.items():
				for section,settings in sections.items():
					hksection=section
					for setting in settings:
						(name,data)=setting
						if name.lower()==hksetting.lower():
							data=data.split(",")
							hk=data[0]
							data=",".join(data)
							break
					if hk!="":
						break
				if hk!="":
					break
		return(hk,data,name,hksection)

	def setKdeConfigSetting(self,group,key,value,kfile="kaccessrc"):
		#kfile=kaccessrc
		#_debug("Writing value {} from {} -> {}".format(key,kfile,value))
		kfilePath=os.path.join(os.environ['HOME'],".config",kfile)
		if os.path.isfile(kfile)==False and kfile.endswith(".profile"):
			kfilePath=os.path.join(os.environ['HOME'],".local/share/konsole/",kfile)
		if len(value):
			cmd=["kwriteconfig5","--file",kfilePath,"--group",group,"--key",key,"{}".format(value)]
		else:
			cmd=["kwriteconfig5","--file",kfilePath,"--group",group,"--key",key,"--delete"]
		ret='false'
		try:
			ret=subprocess.check_output(cmd,universal_newlines=True).strip()
		except Exception as e:
			print(e)
		#_debug("Write value: {}".format(ret))
		return(ret)

	def setSystemConfig(self,config,wrkFile=''):
		for kfile,sections in config.items():
			for section,data in sections.items():
				for setting in data:
					try:
						(desc,value)=setting
						if desc=="":
							continue
						self._debug("Setting {} -> {}".format(desc,value))
						self.setKdeConfigSetting(section,desc,value,kfile)
					except Exception as e:
						print("Error on setting {}".format(setting))
						print(e)
	def takeSnapshot(self,profilePath,appconfrc=''):
		self._debug("Take snapshot {} {}".format(profilePath,appconfrc))
		destName=os.path.basename(profilePath)
		destDir=os.path.dirname(profilePath)
		destPath=os.path.join(destDir,destName)
		self._debug("Destination {}".format(destPath))
		tmpFolder=tempfile.mkdtemp()
		plasmaPath=os.path.join(tmpFolder,"plasma")
		os.makedirs(plasmaPath)
		configPath=os.path.join(tmpFolder,"appconfig")
		os.makedirs(configPath)
		flist=[]
		for kfile in self.dictFileData.keys():
			kPath=os.path.join(os.environ['HOME'],".config",kfile)
			if os.path.isfile(kPath):
				shutil.copy(kPath,plasmaPath)
		if os.path.isfile(appconfrc):
			shutil.copy(appconfrc,configPath)
		(osHdl,tmpFile)=tempfile.mkstemp()
		oldCwd=os.getcwd()
		os.chdir(tmpFolder)
		sw=True
		with tarfile.open(tmpFile,"w") as tarFile:
			for f in os.listdir(tmpFolder):
				tarFile.add(os.path.basename(f))
		os.chdir(oldCwd)
		self._debug("Copying {0}->{1}".format(tmpFile,destPath))
		self._copyTarProfile(tmpFile,destPath)
		os.remove(tmpFile)
	#def take_snapshot

	def _copyTarProfile(self,orig,dest):
		if os.path.isdir(os.path.dirname(dest))==False:
			os.makedirs(os.path.dirname(dest))
		try:
			shutil.copy(orig,dest)
		except Exception as e:
			self._debug(e)
			cmd=["pkexec","/usr/share/accesshelper/helper/profiler.sh",orig,dest]
			try:
				pk=subprocess.run(cmd)
				if pk.returncode!=0:
					sw=False
			except Exception as e:
				self._debug(e)
				self._debug("Permission denied for {}".format(dest))
				sw=False
	#def _copyTarProfile
			
	def importExportSnapshot(self,tarFile,dest):
		self._debug(tarFile)
		if os.path.isfile(tarFile):
			if tarfile.is_tarfile(tarFile)==True:
				self._debug("Import {} to {}".format(tarFile,dest))
				self._copyTarProfile(tarFile,dest)
	#def importSnapshot

	def restoreSnapshot(self,profileTar):
		sw=False
		if os.path.isfile(profileTar):
			if tarfile.is_tarfile(profileTar)==False:
				if tarfile.istarfile("{}.tar",profileTar)==True:
					profileTar="{}.tar".format(profileTar)
					sw=True
			else:
				sw=True
		self._debug(profileTar)
		if sw:
			tarProfile=tarfile.open(profileTar,'r')
			tmpFolder=tempfile.mkdtemp()
			tarProfile.extractall(path=tmpFolder)
			plasmaPath=os.path.join(tmpFolder,"plasma")
			if os.path.isdir(plasmaPath)==True:
				config=self.getSystemConfig(sourceFolder=plasmaPath)
				for kfile,sections in config.items():
					for section,data in sections.items():
						for (desc,value) in data:
							self.setKdeConfigSetting(section,desc,value,kfile)
			confPath=os.path.join(tmpFolder,"appconfig","accesshelper.json")
			if os.path.isfile(confPath)==True:
				usrFolder=os.path.join(os.environ.get('HOME'),".config/accesshelper")
				if os.path.isdir(usrFolder)==False:
					os.makedirs(usrFolder)

				self._debug("Cp {} {}".format(confPath,usrFolder))
				shutil.copy(confPath,usrFolder)
		return(sw)
	#def restore_snapshot

class accesshelper():
	def __init__(self):
		self.functionHelper=functionHelperClass()

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

	def setCursor(self,theme):
		err=0
		try:
			subprocess.run(["plasma-apply-cursortheme",theme],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
			err=1
		return(err)

	def setCursorSize(self,size):
		self.functionHelper.setKdeConfigSetting("Mouse","cursorSize","{}".format(size),"kcminputrc")

	def setScheme(self,scheme):
		err=0
		try:
			subprocess.run(["plasma-apply-colorscheme",scheme],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
			err=1
		return(err)

	def setTheme(self,theme):
		err=0
		try:
			subprocess.run(["plasma-apply-desktoptheme",theme],stdout=subprocess.PIPE)
		except Exception as e:
			err=1
			print(e)
		return(err)

	def cssStyle(self,*args):
		return(self.functionHelper.cssStyle(*args))

	def getHotkey(self,*args):
		return(self.functionHelper.getHotkey(*args))

	def getSystemConfig(self,*args):
		return(self.functionHelper.getSystemConfig(*args))

	def setSystemConfig(self,*args):
		return(self.functionHelper.setSystemConfig(*args))

	def getKdeConfigSetting(self,*args):
		return(self.functionHelper.getKdeConfigSetting(*args))

	def setKdeConfigSetting(self,*args):
		return(self.functionHelper.setKdeConfigSetting(*args))

	def takeSnapshot(self,*args,**kwargs):
		return(self.functionHelper.takeSnapshot(*args,**kwargs))

	def restoreSnapshot(self,*args):
		return(self.functionHelper.restoreSnapshot(*args))

	def importExportSnapshot(self,*args,**kwargs):
		return(self.functionHelper.importExportSnapshot(*args,**kwargs))
