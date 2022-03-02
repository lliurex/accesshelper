#!/usr/bin/python3
import logging
import subprocess
import tarfile
import tempfile
import os,shutil
DBG=True

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
dictFileData={"kaccesrc":{"Bell":bell},"kwinrc":{"Plugins":plugins,"Windows":windows},"kdeglobals":{"KDE":kde,"General":general},"kglobalshortcutsrc":{"kwin":hotkeys_kwin},"kcminputrc":{"Mouse":mouse},"kgammarc":{"ConfigFile":kgammaConfig,"Screen 0":kgammaValues},"SyncBox":kgammaSync}
settingsHotkeys={"invertWindow":"InvertWindow","invertEnabled":"Invert","trackmouseEnabled":"TrackMouse","mouseclickEnabled":"ToggleMouseClick","view_zoom_in":"","view_zoom_out":""}

def _debug(msg):
	if DBG==True:
		logging.warning("FH: {}".format(msg))

def getSystemConfig(wrkFile='',sourceFolder=''):
	dictValues={}
	data=''
	#_debug("Reading folder {}".format(sourceFolder))
	if wrkFile:
		if dictFileData.get(wrkFile,None):
			data={wrkFile:dictFileData[wrkFile].copy()}
	if isinstance(data,str):
		data=dictFileData.copy()
	for kfile,groups in data.items():
		for group,settings in groups.items():
			settingData=[]
			for setting in settings:
				key,value=setting
				value=_getKdeConfigSetting(group,key,kfile,sourceFolder)
				settingData.append((key,value))
			data[kfile].update({group:settingData})
	return (data)

def _getKdeConfigSetting(group,key,kfile="kaccessrc",sourceFolder=''):
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

def setSystemConfig(config,wrkFile=''):
	for kfile,sections in config.items():
		for section,data in sections.items():
			for setting in data:
				(desc,value)=setting
				_debug("Setting {} -> {}".format(desc,value))
				_setKdeConfigSetting(section,desc,value,kfile)

def setKdeConfigSetting(group,key,value,kfile="kaccessrc"):
	return(_setKdeConfigSetting(group,key,value,kfile))

def _setKdeConfigSetting(group,key,value,kfile="kaccessrc"):
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

def getHotkey(setting):
	hk=""
	hksection=""
	data=""
	name=""
	hksetting=settingsHotkeys.get(setting,"")
	if hksetting:
		sc=getSystemConfig(wrkFile="kglobalshortcutsrc")
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

def cssStyle():
	style="""
		QListWidget{
			}
		QListWidget::item{
			margin:3px;
			padding:3px;
			}
	"""
	return(style)

def takeSnapshot(profilePath,appconfrc=''):
	_debug("Take snapshot {} {}".format(profilePath,appconfrc))
	destName=os.path.basename(profilePath)
	destDir=os.path.dirname(profilePath)
	destPath=os.path.join(destDir,destName)
	_debug("Destination {}".format(destPath))
	tmpFolder=tempfile.mkdtemp()
	plasmaPath=os.path.join(tmpFolder,"plasma")
	os.makedirs(plasmaPath)
	configPath=os.path.join(tmpFolder,"appconfig")
	os.makedirs(configPath)
	flist=[]
	for kfile in dictFileData.keys():
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
	_debug("Copying {0}->{1}".format(tmpFile,destPath))
	_copyTarProfile(tmpFile,destPath)
	os.remove(tmpFile)
#def take_snapshot

def _copyTarProfile(orig,dest):
	try:
		shutil.copy(orig,dest)
	except Exception as e:
		_debug(e)
		cmd=["pkexec","/usr/share/accesshelper/helper/profiler.sh",orig,dest]
		try:
			pk=subprocess.run(cmd)
			if pk.returncode!=0:
				sw=False
		except Exception as e:
			_debug(e)
			_debug("Permission denied for {}".format(dest))
			sw=False
#def _copyTarProfile
		
def importExportSnapshot(tarFile,dest):
	if os.path.isfile(tarFile):
		if tarfile.is_tarfile(tarFile)==True:
			_debug("Import {} to {}".format(tarFile,dest))
			_copyTarProfile(tarFile,dest)
#def importSnapshot

def restoreSnapshot(profileTar):
	sw=False
	if os.path.isfile(profileTar):
		if tarfile.is_tarfile(profileTar)==False:
			if tarfile.istarfile("{}.tar",profileTar)==True:
				profileTar="{}.tar".format(profileTar)
				sw=True
		else:
			sw=True
	_debug(profileTar)
	if sw:
		tarProfile=tarfile.open(profileTar,'r')
		tmpFolder=tempfile.mkdtemp()
		tarProfile.extractall(path=tmpFolder)
		plasmaPath=os.path.join(tmpFolder,"plasma")
		if os.path.isdir(plasmaPath)==True:
			config=getSystemConfig(sourceFolder=plasmaPath)
			for kfile,sections in config.items():
				for section,data in sections.items():
					for (desc,value) in data:
						_setKdeConfigSetting(section,desc,value,kfile)
		confPath=os.path.join(tmpFolder,"appconfig","accesshelper.json")
		if os.path.isfile(confPath)==True:
			usrFolder=os.path.join(os.environ.get('HOME'),".config/accesshelper")
			if os.path.isdir(usrFolder)==False:
				os.makedirs(usrFolder)

			_debug("Cp {} {}".format(confPath,usrFolder))
			shutil.copy(confPath,usrFolder)
	return(sw)
#def restore_snapshot
