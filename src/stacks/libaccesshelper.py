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

class functionHelperClass():
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
		if desc=="":
			data=""
		else:
			desc="{0},{0},{1}".format(hotkey,desc)
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

	def takeSnapshot(self,profilePath,appconfrc=''):
		home=os.environ.get("HOME")
		if appconfrc=='':
			appconfrc=os.path.join(home,".config/accesshelper/accesshelper.json")
		self._debug("Take snapshot {} {}".format(profilePath,appconfrc))
		destName=os.path.basename(profilePath)
		destDir=os.path.dirname(profilePath)
		destPath=os.path.join(destDir,destName)
		self._debug("Destination {}".format(destPath))
		#Generate tmp folders
		tmpFolder=tempfile.mkdtemp()
		#Plasma config goes to .config
		plasmaPath=os.path.join(tmpFolder,".config")
		os.makedirs(plasmaPath)
		#accesshelper to .config/accesshelper
		configPath=os.path.join(tmpFolder,".config/accesshelper")
		onboard=os.path.join(os.path.dirname(appconfrc),"onboard.dconf")
		os.makedirs(configPath)
		#autostart
		desktopStartPath=os.path.join(tmpFolder,".config/autostart")
		os.makedirs(desktopStartPath)
		autostartPath=os.path.join(home,".config","autostart")
		#autoshutdown
		desktopShutdownPath=os.path.join(tmpFolder,".config/plasma-workspace/shutdown")
		os.makedirs(desktopShutdownPath)
		autoshutdownPath=os.path.join(home,".config",".config/plasma-workspace/shutdown")
		#mozilla
		mozillaPath=os.path.join(tmpFolder,".mozilla")
		os.makedirs(mozillaPath)
		#gtk
		gtkPath=os.path.join(tmpFolder,".config")
		if os.path.isdir(gtkPath)==False:
			os.makedirs(gtkPath)

		flist=[]
		for kfile in self.dictFileData.keys():
			kPath=os.path.join(os.environ['HOME'],".config",kfile)
			if os.path.isfile(kPath):
				shutil.copy(kPath,plasmaPath)
		if os.path.isfile(appconfrc):
			shutil.copy(appconfrc,configPath)
		if os.path.isfile(onboard):
			shutil.copy(onboard,configPath)
		for auto in [autostartPath,autoshutdownPath]:
			if os.path.isdir(auto):
				for f in os.listdir(auto):
					if f.startswith("access"):
						autostart=os.path.join(auto,f)
						if auto==autostartPath:
							shutil.copy(autostart,desktopStartPath)
						else:
							shutil.copy(autostart,desktopShutdownPath)
		mozillaFiles=self._getMozillaSettingsFiles()
		for mozillaFile in mozillaFiles:
			destdir=os.path.basename(os.path.dirname(mozillaFile))
			destdir=os.path.join(mozillaPath,destdir)
			os.makedirs(destdir)
			shutil.copy(mozillaFile,destdir)
		gtkFiles=self._getGtkSettingsFiles(True)
		for gtkFile in gtkFiles:
			destdir=os.path.basename(os.path.dirname(gtkFile))
			destdir=os.path.join(gtkPath,destdir)
			os.makedirs(destdir)
			shutil.copy(gtkFile,destdir)
		(osHdl,tmpFile)=tempfile.mkstemp()
		oldCwd=os.getcwd()
		os.chdir(tmpFolder)
		with tarfile.open(tmpFile,"w") as tarFile:
			for f in os.listdir(tmpFolder):
				tarFile.add(os.path.basename(f))
		os.chdir(oldCwd)
		self._debug("Copying {0}->{1}".format(tmpFile,destPath))
		self._copyTarProfile(tmpFile,destPath)
		os.remove(tmpFile)
		return(os.path.join(destPath,os.path.basename(tmpFile)))
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

	def _checkSnapshot(self,profileTar):
		sw=False
		if os.path.isfile(profileTar):
			sw=tarfile.is_tarfile(profileTar)
		if sw==False:
			print("Error: {} is not a valid tar".format(profileTar))
		self._debug("{0} {1}".format(profileTar,sw))
		return(sw)

	def restoreSnapshot(self,profileTar,merge=False):
		sw=self._checkSnapshot(profileTar)
		if sw:
			tarProfile=tarfile.open(profileTar,'r')
			tmpFolder=tempfile.mkdtemp()
			tarProfile.extractall(path=tmpFolder)
			basePath=os.path.join(tmpFolder,".config")
			self._loadPlasmaConfigFromFolder(basePath)
			confPath=os.path.join(tmpFolder,".config/accesshelper")
			jcontents={}
			desktopPath=os.path.join(tmpFolder,".config/autostart")
			if os.path.isdir(desktopPath)==True:
				autostartFolder=os.path.join(os.environ.get('HOME'),".config","autostart")
				autoshutdownFolder=os.path.join(os.environ.get('HOME'),".config","plasma-workspace/shutdown")
				if os.path.isdir(autostartFolder)==False:
					os.makedirs(autostartFolder)
				if os.path.isdir(autoshutdownFolder)==False:
					os.makedirs(autoshutdownFolder)
				#Clean operations
				self.cleanHome(autostartFolder,autoshutdownFolder)
				for f in os.listdir(desktopPath):
					if "profiler" in f:
						continue
					desktopFile=os.path.join(desktopPath,f)
					shutil.copy(desktopFile,autostartFolder)
			if os.path.isdir(confPath)==True:
				usrFolder=os.path.join(os.environ.get('HOME'),".config/accesshelper")
				if os.path.isdir(usrFolder)==False:
					os.makedirs(usrFolder)
				for confFile in os.listdir(confPath):
					sourceFile=os.path.join(confPath,confFile)
					self._debug("Cp {} {}".format(sourceFile,usrFolder))
					#Modify profile value.
					with open(sourceFile,"r") as f:
						fcontents=f.read()
					try:
						jcontents=json.loads(fcontents)
					except:
						jcontents.update({"profile":"{}".format(os.path.basename(profileTar))})
					(profile,oldConfig)=self._getOldProfile(profileTar,usrFolder)
					startup=oldConfig.get("startup","false")
					jcontents.update({"startup":startup})
					jcontents.update({"autoprofile":profile})
					if startup=="true":
						#Apply changes on startup/shutdown
						cmd="/usr/share/accesshelper/accesshelp.py --set {}".format(profile)
						self.generateAutostartDesktop(cmd,"accesshelper_profiler.desktop","plasma-workspace/shutdown")
						cmd="{} apply".format(cmd)
						self.generateAutostartDesktop(cmd,"accesshelper_profiler.desktop")
					with open(sourceFile,"w") as f:
						json.dump(jcontents,f,indent=4)
					shutil.copy(sourceFile,usrFolder)
				data=self.getPlasmaConfig()
			mozillaPath=os.path.join(tmpFolder,".mozilla")
			if os.path.isdir(mozillaPath)==True:
				mozillaFolder=os.path.join(os.environ.get('HOME'),".mozilla/firefox")
				for folder in os.listdir(mozillaPath):
					sourceFolder=os.path.join(mozillaPath,folder)
					destFolder=os.path.join(mozillaFolder,folder)
					if os.path.isdir(destFolder)==True:
						for mozillaFile in os.listdir(os.path.join(mozillaPath,folder)):
							sourceFile=os.path.join(sourceFolder,mozillaFile)
							self._debug("Cp {} {}".format(sourceFile,destFolder))
							shutil.copy(sourceFile,destFolder)
			if os.path.isdir(basePath):
				for folder in os.listdir(basePath):
					if folder.startswith('gtk') and os.path.isdir(os.path.join(basePath,folder)):
						destFolder=os.path.join(os.environ.get('HOME'),".config",folder)
						if os.path.isdir(destFolder)==False:
							os.makedirs(destFolder)
						sourceFolder=os.path.join(basePath,folder)
						for gtkFile in os.listdir(sourceFolder):
							sourceFile=os.path.join(sourceFolder,gtkFile)
							self._debug("Cp {} {}".format(sourceFile,destFolder))
							shutil.copy(sourceFile,destFolder)
			self._setNewConfig()
		return(sw)
	#def restore_snapshot

	def cleanHome(self,autostartFolder,autoshutdownFolder):
		self.removeAutostartDesktop("accesshelper_rgbFilter.desktop")
		for f in os.listdir(autostartFolder):
			if f.startswith("accesshelper_"):
				os.remove(os.path.join(autostartFolder,f))
		for f in os.listdir(autoshutdownFolder):
			if f.startswith("accesshelper_"):
				os.remove(os.path.join(autoshutdownFolder,f))
	#def cleanHome

	def _getOldProfile(self,profileTar,usrFolder):
		profile=profileTar
		startup="false"
		oldconf=os.path.join(usrFolder,"accesshelper.json")
		joldcontents={}
		if os.path.isfile(oldconf)==True:
			with open(oldconf,"r") as f:
				foldcontents=f.read()
			joldcontents=json.loads(foldcontents)
			if joldcontents.get("startup","")=="true":
				startup="true"
				profile=joldcontents.get("profile","")
				profile=joldcontents.get("autoprofile",profile)
		profile=os.path.basename(profile).replace(".tar","")
		return(profile,joldcontents)
	#def mergeHome

	def setNewConfig(self):
		self._setNewConfig()

	def _setNewConfig(self):
		usrConfig=os.path.join(os.environ.get('HOME'),".config/accesshelper/accesshelper.json")
		if os.path.isfile(usrConfig):
			jcontent={}
			with open(usrConfig,'r') as f:
				content=f.read()
			try:
				jcontent=json.loads(content)
			except:
				fcontent=content.split("}")
				fcontent="}".join(fcontent[:-1])+"}"
				try:
					jcontent=json.loads(fcontent)
				except:
					print(fcontent)
			bkg=''
			img=''
			theme=''
			scheme=''
			color=''
			cursor=''
			size=''
			scale='100'
			xscale='100'
			dockHk=''
			alpha=[]
			for key,data in jcontent.items():
				fline=""
				if key=="bkg":
					bkg=data
				elif key=="dockHk":
					dockHk=data
				elif key=="bkgColor":
					color=data
				elif key=="background":
					img=data
				elif key=="cursor":
					cursor=data
				elif key=="cursorSize":
					size=data
				elif key=="theme":
					theme=data
				elif key=="scheme":
					scheme=data
				elif key=="scale":
					scale=data
				elif key=="xscale":
					xscale=data
				elif key=="alpha" and isinstance(data,list) and len(data)==4:
					alpha=QColor(data[0],data[1],data[2],data[3])
			if bkg=="color":
				if color:
					qcolor=QColor(color)
					self.setBackgroundColor(qcolor)
			elif bkg=="image":
				if img:
					self.setBackgroundImg(img)
			if cursor and size:
				self.setCursor(cursor,size,applyChanges=True)
			if scale:
				self.setScaleFactor(float(scale)/100)
			self.removeAutostartDesktop("accesshelper_Xscale.desktop")
			if xscale:
				if xscale!="100":
					self.setXscale(xscale)
			self.removeRGBFilter()
			if isinstance(alpha,QColor):
				self.setRGBFilter(alpha)
			if theme!="":
				subprocess.run(["plasma-apply-desktoptheme",theme],stdout=subprocess.PIPE)
			if scheme!="":
				subprocess.run(["plasma-apply-colorscheme",scheme],stdout=subprocess.PIPE)
			if dockHk!="":
				self._debug("Set hotkey for dock: {}".format(dockHk))
				desc=""
				name="accessdock"
				self.setHotkey(dockHk,desc,name)
				desc="show accessdock"
				name="accessdock.desktop"
				self.setHotkey(dockHk,desc,name)
	#def _setNewConfig					

	def _loadPlasmaConfigFromFolder(self,folder):
		if os.path.isdir(folder)==True:
			config=self.getPlasmaConfig(sourceFolder=folder)
			for kfile,sections in config.items():
				for section,data in sections.items():
					for (desc,value) in data:
						self.setKdeConfigSetting(section,desc,value,kfile)
	#def _loadPlasmaConfigFromFolder

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

	def _runSetCursorApp(self,theme,size):
		cmd=["/usr/share/accesshelper/helper/setcursortheme","-r","1",theme,size]
		subprocess.Popen(cmd,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	#def _runSetCursorApp

	def setScaleFactor(self,scaleFactor,plasma=True,xrand=False):
		cmd=["xrandr","--listmonitors"]
		output=subprocess.run(cmd,capture_output=True,text=True)
		monitors=[]
		for line in output.stdout.split("\n"):
			if len(line.split(" "))>=4:
				monitors.append("{0}={1}".format(line.split(" ")[-1],scaleFactor))
		if xrand==True:
			for monitor in monitors:
				f=round(1-((scaleFactor-1)/3),2)
				output=monitor.split("=")[0]
				cmd=["xrandr","--output",output,"--scale","{}x{}".format(f,f)]
				try:
					subprocess.run(cmd)
				except Exception as e:
					print(" ".join(cmd))
					print(e)
		if plasma==True:
			self._debug("Setting plasma scale factor...")
			if monitors:
				screenScaleFactors="{};".format(";".join(monitors))
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
		for monitor in self._getMonitors():
			xrand=["xrandr","--output",monitor,"--gamma","1:1:1","--brightness","1"]
		xgamma=["xgamma","-screen","0","-rgamma","1","-ggamma","1","-bgamma","1"]
		cmd=subprocess.run(xgamma,capture_output=True,encoding="utf8")
		values=[("ggamma","1.00"),("bgamma","1.00"),("rgamma","1.00")]
		plasmaConfig={'kgammarc':{'Screen 0':values}}
		self.setPlasmaConfig(plasmaConfig)
		self.removeAutostartDesktop("accesshelper_rgbFilter.desktop")
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
		if onlyset==False:
			self.generateAutostartDesktop(xgamma,"accesshelper_rgbFilter.desktop")
		return(red,green,blue)
	#def setRGBFilter

	def setXscale(self,xscale):
		cmd=["xrandr","--listmonitors"]
		output=subprocess.run(cmd,capture_output=True,text=True)
		monitors=[]
		for line in output.stdout.split("\n"):
			if len(line.split(" "))>=4:
				monitors.append("{0}".format(line.split(" ")[-1]))
		cmd=[]
		for output in monitors:
			f=round(1-(((int(xscale)/100)-1)/3),2)
			cmd.append("sleep 5")
			cmd.append("xrandr --output {0} --scale {1}x{1}".format(output,f))
		self.generateAutostartDesktop(" && ".join(cmd),"accesshelper_Xscale.desktop")
	#def setXscale(self,xscale):

	def setCursorSize(self,size):
		self._debug("Sizing to: {}".format(size))
		self.setKdeConfigSetting("Mouse","cursorSize","{}".format(size),"kcminputrc")
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
		if applyChanges==True:
			try:
				subprocess.run(["plasma-apply-cursortheme",theme],stdout=subprocess.PIPE)
			except Exception as e:
				print(e)
				err=1
		os.environ["XCURSOR_THEME"]=theme
		print("Set theme: {}".format(theme))
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
		try:
			cmd=["qdbus","org.kde.klauncher5","/KLauncher","org.kde.KLauncher.setLaunchEnv","XCURSOR_THEME",theme]
			subprocess.run(cmd,stdout=subprocess.PIPE)
			cmd=["qdbus","org.kde.klauncher5","/KLauncher","org.kde.KLauncher.setLaunchEnv","XCURSOR_SIZE",size]
			subprocess.run(cmd,stdout=subprocess.PIPE)
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

class accesshelper():
	def __init__(self):
		self.dbg=False
		self.functionHelper=functionHelperClass()
		self.tmpDir=self.functionHelper.tmpDir
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("libaccess: {}".format(msg))
	#def _debug

	def removeTmpDir(self):
		if os.path.isdir(self.tmpDir):
			shutil.rmtree(self.tmpDir)
			os.makedirs(self.tmpDir)
	#def removeTmpDir

	def generateChangesFile(self,window,changesDict):
		if os.path.isdir(self.tmpDir)==False:
			os.makedirs(self.tmpDir)
		destPath=os.path.join(self.tmpDir,window)
		if os.path.isdir(destPath):
			shutil.rmtree(destPath)
		os.makedirs(destPath)
		destFile=os.path.join(destPath,"{}.json".format(window))
		with open(destFile,"w") as f:
			f.writelines(changesDict)	
	#def generateChangesFile

	def getMonitors(self,*args):
		return(self.functionHelper._getMonitors(*args))
	#def getMonitors

	def setOnboardConfig(self):
		home=os.environ.get("HOME")
		wrkFile=os.path.join(home,".config/accesshelper","onboard.dconf")
		if os.path.isfile(wrkFile):
			cmd=["cat",wrkFile]
			try:
				cat=subprocess.Popen(cmd,stdout=subprocess.PIPE)
			except:
				cat=None
			if cat!=None:
				cmd=["dconf","load","/org/onboard/"]
				try:
					dconf=subprocess.run(cmd,stdin=cat.stdout)
				except Exception as e:
					print(e)
				cat.communicate()
	#def setOnboardConfig

	def removeRGBFilter(self):
		self.functionHelper.removeRGBFilter()
	#def resetRGBFilter

	def removeXscale(self):
		self.removeAutostartDesktop("accesshelper_Xscale.desktop")
	#def removeXscale

	def removeAutostartDesktop(self,desktop,folder="autostart"):
		self.functionHelper.removeAutostartDesktop(desktop,folder)
	#def _removeAutostartDesktop

	def setRGBFilter(self,*args,**kwargs):
		return(self.functionHelper.setRGBFilter(*args,**kwargs))
	#def setRGBFilter

	def setXscale(self,*args):
		self.functionHelper.setXscale(*args)
	#def setXscale(self,xscale):

	def generateAutostartDesktop(self,cmd,fname,folder="autostart"):
		self.functionHelper.generateAutostartDesktop(cmd,fname,folder)
	#def generateAutostartDesktop

	def getCursors(self):
		return(self.functionHelper.getCursors())
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

	def setCursor(self,*args):
		self.functionHelper.setCursor(*args)
	#def setCursor

	def _runSetCursorApp(self,*args):
		self.functionHelper._runSetCursorApp(*args)
	#def _runSetCursorApp

	def setCursorSize(self,*args):
		self.functionHelper.setCursorSize(*args)
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

	def setBackgroundColor(self,*args):
		return(self.functionHelper.setBackgroundColor(*args))
	#def setBackgroundColor

	def setBackgroundImg(self,*args):
		return(self.functionHelper.setBackgroundImg(*args))
	#def setBackgroundImg

	def getBackgroundImg(self):
		#Dirt method to get wallpaper: parse plasma-org.kde.plasma.desktop-appletsrc
		confFile=os.path.join(os.environ.get("HOME",""),".config","plasma-org.kde.plasma.desktop-appletsrc")
		img=""
		if os.path.isfile(confFile):
			with open (confFile,"r") as f:
				for line in f.readlines():
					if line.startswith("Image=file://"):
						img=line.replace("Image=file://","")
						break
		return img.strip()
	#def getBackgroundImg

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
		return(self.functionHelper.getCursorTheme())
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
		catalanFestival="/usr/share/festival/voices/catalan"
		if os.path.isdir(catalanFestival):
			for i in os.listdir(catalanFestival):
				voices.append(i)
		return(voices)
	#def getFestivalVoices

	def getSettingForHotkey(self,*args):
		return(self.functionHelper.getSettingForHotkey(*args))
	#def getSettingForHotkey(self,*args):

	def setMozillaFirefoxFonts(self,size):
		for prefs in self.functionHelper._getMozillaSettingsFiles():
			with open(prefs,'r') as f:
				lines=f.readlines()
			newLines=[]
			for line in lines:
				if line.startswith('user_pref("font.minimum-size.x-unicode"'):
					continue
				elif line.startswith('user_pref("font.minimum-size.x-western"'):
					continue
				newLines.append(line)
			line='user_pref("font.minimum-size.x-western", {});\n'.format(size)
			newLines.append(line)
			line='user_pref("font.minimum-size.x-unicode", {});\n'.format(size)
			newLines.append(line)
			self._debug("Writting MOZILLA {}".format(prefs))
			with open(os.path.join(prefs),'w') as f:
				f.writelines(newLines)
	#def setMozillaFirefoxFonts

	def setGtkFonts(self,font):
		fontArray=font.split(',')
		gtkFont="{0}, {1} {2}".format(fontArray[0],fontArray[-1],fontArray[1])
		gtkDirs=[os.path.join("/home",os.environ.get('USER',''),".config/gtk-3.0"),os.path.join("/home",os.environ.get('USER',''),".config/gtk-4.0")]
		for gtkFile in self.functionHelper._getGtkSettingsFiles():
			fcontent=[]
			if os.path.isfile(gtkFile)==True:
				with  open(gtkFile,"r") as f:
					for line in f.readlines():
						if line.startswith("gtk-font-name")==False:
							fcontent.append(line)
			fcontent.append("gtk-font-name={}\n".format(gtkFont))
			with  open(gtkFile,"w") as f:
				try:
					f.writelines(fcontent)
				except Exception as e:
					self._debug("error saving gtk fonts")
	#def setGtkFonts

	def setGrubBeep(self,state):
		sw=True
		if state==True:
			state="enable"
		else:
			state="disable"
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

	def setScaleFactor(self,*args,**kwargs):
		return(self.functionHelper.setScaleFactor(*args,**kwargs))
	#def setScaleFactor

	def setNewConfig(self,*args):
		self.functionHelper.setNewConfig()
	#def setNewConfig(self,*args):

	def applyChanges(self,setconf=True):
		if setconf:
			self.setNewConfig()
		cmd=["qdbus","org.kde.kded","/kded","unloadModule","powerdevil"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["qdbus","org.kde.keyboard","/modules/khotkeys","reread_configuration"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["qdbus","org.kde.kded","/kbuildsycoca","recreate"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["qdbus","org.kde.kded","/kded","reconfigure"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["qdbus","org.kde.plasma-desktop","/MainApplication","reparseConfiguration"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["qdbus","org.kde.kwin","/KWin","reconfigure"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["qdbus","org.kde.kded","/kded","loadModule","powerdevil"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		print("Changes applied!")


		cmd=["plasmashell","--replace"]
		subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
#		cmd=["kquitapp5","kglobalaccel5"]
#		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
#		cmd=["kstart5","kglobalaccel5"]
#		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
#		cmd=["qdbus","org.kde.KWin","/KWin","org.kde.KWin.reconfigure"]
#		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		time.sleep(5)
		cmd=["pidof","plasmashell"]
		p=subprocess.run(cmd)
		if p.returncode!=0:
			cmd=["plasmashell","--replace"]
			subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
	#def _applyChangeswaitForPlasma
		
	def restartSession(self):
		cmd=["qdbus","org.kde.ksmserver","/KSMServer","org.kde.KSMServerInterface.logout","1","3","3"]
		#cmd=["qdbus","org.kde.Shutdown","/Shutdown","org.kde.Shutdown.logout"]
		subprocess.run(cmd)
	#def restartSession
