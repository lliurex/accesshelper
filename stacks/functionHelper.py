#!/usr/bin/python3
import logging
import subprocess
import os

plugins=[("invertEnabled",""),("invertWindow",""),("magnifierEnabled",""),("lookingglassEnabled",""),("trackmouseEnabled",""),("zoomEnabled",""),("snaphelperEnabled",""),("mouseclickEnabled","")]
windows=[("FocusPolicy","")]
kde=[("singleClick","")]
bell=[("SystemBell",""),("VisibleBell","")]
hotkeys_kwin=[("ShowDesktopGrid",""),("Invert",""),("InvertWindow",""),("ToggleMouseClick",""),("TrackMouse",""),("view_zoom_in",""),("view_zoom_out","")]
dictFileData={"kaccesrc":{"Bell":bell},"kwinrc":{"Plugins":plugins,"Windows":windows},"kdeglobals":{"KDE":kde},"kglobalshortcutsrc":{"kwin":hotkeys_kwin}}

def _debug(msg):
	print("{}".format(msg))

def getSystemConfig(wrkFile=''):
	dictValues={}
	data=''
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
				value=_getKdeConfigSetting(group,key,kfile)
				settingData.append((key,value))
			data[kfile].update({group:settingData})
	return (data)

def _getKdeConfigSetting(group,key,kfile="kaccessrc"):
	_debug("Reading value {} from {}".format(key,kfile))
	kPath=os.path.join(os.environ.get('HOME',"/usr/share/acccessibility"),".config",kfile)
	value=""
	if os.path.isfile(kPath):
		cmd=["kreadconfig5","--file",kPath,"--group",group,"--key",key]
		try:
			value=subprocess.check_output(cmd,universal_newlines=True).strip()
		except Exception as e:
			print(e)
	_debug("Read value: {}".format(value))
	return(value)

def setKdeConfigSetting(self,group,key,value,kfile="kaccessrc"):
	#kfile=kaccessrc
	self._debug("Writing value {} from {} -> {}".format(key,kfile,value))
	cmd=["kwriteconfig5","--file",os.path.join(os.environ['HOME'],".config",kfile),"--group",group,"--key",key,"{}".format(value)]
	ret='false'
	try:
		ret=subprocess.check_output(cmd,universal_newlines=True).strip()
	except Exception as e:
		print(e)
	self._debug("Write value: {}".format(ret))
	return(ret)
