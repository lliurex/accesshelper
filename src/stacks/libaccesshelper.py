#!/usr/bin/python3
import subprocess,os
import tarfile
import tempfile
import shutil
from collections import OrderedDict
from PySide2.QtGui import QIcon,QPixmap

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
	#def cssStyle

	def getPlasmaConfig(self,wrkFile='',sourceFolder=''):
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
		#_debug("Read value: {}".format(value))
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
		else:
			for kfile,sections in sc.items():
				if setting.lower() in sections.keys():
					(name,data)=sections[setting][0]
					if name.lower()=="_launch":
						data=data.split(",")
						hk=data[0]
						hksection=setting
						data=",".join(data)
		self._debug("-------------------")
		self._debug("{0} {1} {2} {3}".format(hk,data,name,hksection))
		self._debug("-------------------")
		return(hk,data,name,hksection)
	#def getHotkey

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
	#def setKdeConfigSetting

	def setPlasmaConfig(self,config,wrkFile=''):
		self._debug("Config: {}".format(config))
		for kfile,sections in config.items():
			for section,data in sections.items():
				self._debug("Section {}".format(section))
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
	#def setPlasmaConfig

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
		self._debug("{0} {1}".format(profileTar,sw))
		if sw:
			tarProfile=tarfile.open(profileTar,'r')
			tmpFolder=tempfile.mkdtemp()
			tarProfile.extractall(path=tmpFolder)
			plasmaPath=os.path.join(tmpFolder,"plasma")
			if os.path.isdir(plasmaPath)==True:
				config=self.getPlasmaConfig(sourceFolder=plasmaPath)
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
				data=self.getPlasmaConfig()
		return(sw)
	#def restore_snapshot

	def getPointerImage(self,theme):
		icon=os.path.join("/usr/share/icons",theme,"cursors","left_ptr")
		self._debug("Extracting imgs for icon {}".format(icon))
		if os.path.isfile(icon)==False:
			icon=os.path.join(os.environ.get("HOME",""),".icons",theme,"cursors","left_ptr")
		qicon=""
		sizes=[]
		if os.path.isfile(icon):
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

class accesshelper():
	def __init__(self):
		self.dbg=True
		self.functionHelper=functionHelperClass()
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("libaccess: {}".format(msg))
	#def _debug

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

	def setCursor(self,theme="default"):
		if theme=="default":
			theme=self._getCursorTheme()
		err=0
		try:
			subprocess.run(["plasma-apply-cursortheme",theme],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
			err=1
		os.environ["XCURSOR_THEME"]=theme
		return(err)
	#def setCursor

	def setCursorSize(self,size):
		self._debug("Sizing to: {}".format(size))
		self.setKdeConfigSetting("Mouse","cursorSize","{}".format(size),"kcminputrc")
		xdefault=os.path.join(os.environ.get("HOME"),".Xdefaults")
		xcursor="Xcursor.size:{}\n".format(size)
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
		#os.environ["XCURSOR_SIZE"]=str(size)
	#def setCursorSize

	def setScheme(self,scheme):
		err=0
		try:
			subprocess.run(["plasma-apply-colorscheme",scheme],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
			err=1
		return(err)
	#def setScheme

	def setTheme(self,theme):
		err=0
		try:
			subprocess.run(["plasma-apply-desktoptheme",theme],stdout=subprocess.PIPE)
		except Exception as e:
			err=1
			print(e)
		return(err)
	#def setTheme

	def cssStyle(self,*args):
		return(self.functionHelper.cssStyle(*args))
	#def cssStyle

	def getHotkey(self,*args):
		return(self.functionHelper.getHotkey(*args))
	#def getHotkey

	def getPlasmaConfig(self,*args):
		return(self.functionHelper.getPlasmaConfig(*args))
	#def getPlasmaConfig

	def setPlasmaConfig(self,*args):
		return(self.functionHelper.setPlasmaConfig(*args))
	#def setPlasmaConfig

	def getKdeConfigSetting(self,*args):
		return(self.functionHelper.getKdeConfigSetting(*args))
	#def getKdeConfigSetting

	def setKdeConfigSetting(self,*args):
		return(self.functionHelper.setKdeConfigSetting(*args))
	#def setKdeConfigSetting

	def takeSnapshot(self,*args,**kwargs):
		return(self.functionHelper.takeSnapshot(*args,**kwargs))
	#def takeSnapshot

	def restoreSnapshot(self,*args):
		return(self.functionHelper.restoreSnapshot(*args))
	#def restoreSnapshot

	def importExportSnapshot(self,*args,**kwargs):
		return(self.functionHelper.importExportSnapshot(*args,**kwargs))
	#def importExportSnapshot
	
	def _getCursorTheme(self):
		themes=self.getCursors()
		theme="default"
		for available in themes:
			if ("current") in available:
				theme=available.split("(")[1].replace("(","").replace(")","")
				theme=theme.split(" ")[0]
				break
		return(theme)
	#def _getCursorTheme

	def getPointerImage(self,*args,theme="default"):
		if theme=="default":
			theme=self._getCursorTheme()
		return(self.functionHelper.getPointerImage(*args,theme))
	#def getPointerImage

	def getPointerSize(self,*args):
		plasmaConfig=self.getPlasmaConfig("kcminputrc")
		cursorSettings=plasmaConfig.get('kcminputrc',{}).get('Mouse',[])
		cursorSize=32
		for setting in cursorSettings:
			if isinstance(setting,tuple):
				if setting[0]=="cursorSize":
					size=setting[1]
					if not size:
						size=32
					cursorSize=int(size)
		return(cursorSize)
	#def getPointerSize

	def getTtsFiles(self):
		ttsDir=os.path.join(os.environ.get('HOME'),".config/accesshelper/tts")
		allDict={}
		if os.path.isdir(ttsDir)==True:
			mp3Dir=os.path.join(ttsDir,"mp3")
			txtDir=os.path.join(ttsDir,"txt")
			txtDict={}
			mp3Dict={}
			for f in os.listdir(mp3Dir):
				if f.endswith(".mp3") and "_" in f:
					mp3Dict[f.replace(".mp3","")]=f
			for f in os.listdir(txtDir):
				if f.endswith(".txt") and "_" in f:
					txtDict[f.replace(".txt","")]=f
			for key,item in mp3Dict.items():
				allDict[key]={"mp3":item}
			for key,item in txtDict.items():
				if allDict.get(key):
					allDict[key].update({"txt":item})
				else:
					allDict[key]={"txt":item}
		ordDict=OrderedDict(sorted(allDict.items(),reverse=True))
		return(ordDict)
	#def getTtsFiles

	def getFestivalVoices(self):
		voices=[]
		spanishFestival="/usr/share/festival/voices/spanish"
		if os.path.isdir(spanishFestival):
			for i in os.listdir(spanishFestival):
				voices.append(i)
		return(voices)
	#def getFestivalVoices

	def applyChanges(self):
		cmd=["qdbus","org.kde.KWin","/KWin","org.kde.KWin.reconfigure"]
		subprocess.run(cmd)
		cmd=["kquitapp5","kglobalaccel"]
		subprocess.run(cmd)
		cmd=["kstart5","kglobalaccel"]
		subprocess.run(cmd)
		#cmd=["kquitapp5","plasmashell"]
		#subprocess.run(cmd)
		cmd=["plasmashell","--replace"]
		subprocess.Popen(cmd)
	#def applyChanges
