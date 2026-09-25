from llxaccessibility import llxaccessibility
from PySide2.QtCore import Qt,QThread,Signal,QSize
import os

class thLauncher(QThread):
	finished=Signal("PyObject")
	def __init__(self,rebost,parent=None,*args,**kwargs):
		super().__init__()
		self.accesshelper=llxaccessibility.client()
		self.rebost=rebost
		self.cmd=""

	def setParms(self,cmd):
		self.cmd=cmd
	#def setParms

	def _getCmdArray(self,*args):
		cmd=args[0]
		procCmd=[]
		self.parms=[]
		if " " in cmd:
			procCmd.extend(cmd[0].split(" ")[1:])
			F
			procCmd.insert(0,cmd[0].split(" ")[0])
		else:
			if isinstance(cmd,str):
				procCmd=cmd.split(" ")
			else:
				procCmd=cmd
		self.cmd=procCmd[0]
		self.cmd.extend(cmd[1:])
	#def setParms

	def _getAppCmd(self,app):
		cmdPath=self._getPathForCmd(app)
		if len(cmdPath)>0:
			cmd=[cmdPath]
			if cmdPath.endswith("/orca"):
				cmd.append("-s")
		else:
			cmd=["/usr/bin/lliurex-store","appsedu://{}".format(app)]
			appraw=json.loads(self.rebost.showApp(app))
			bundle=""
			if len(appraw)>0:
				app=appraw[0]
				for bun in app.get("bundle",{}).keys():
					if bun.lower()=="unknown":
						continue
					if app.get("status",{}).get(bun,"1")=="0":
						bundle=bun
						break
				if bundle=="package":
					cmd=["gtk-launch",app.get("id",'')]
				elif bundle=="flatpak":
					cmd=["flatpak","run",app.get("bundle",{}).get("flatpak","")]
				elif bundle=="snap":
					cmd=["snap","run",app.get("bundle",{}).get("snap","")]
				elif bundle=="appimage":
					cmd=["gtk-launch","{}-appimage".format(app.get("pkgname",''))]
				#proc=subprocess.run(cmd)
		return(cmd)
	#def _getAppCmd

	def _getPathForCmd(self,cmd):
		cmdPath=None
		if os.path.isfile(cmd)==False:
			cmdPath=shutil.which(os.path.basename(cmd.split(" ")[0]))
		if cmdPath==None:
			cmdPath=""
		return(cmdPath)

	def run(self):
		if self.cmd=="ACCE":
			mod="kcm_access"
			self.cmd="kcm_access"
		else:
			if self.cmd=="ORCA":
				self.cmd=self._getAppCmd("orca")
			elif self.cmd=="LTTS":
				self.cmd=os.path.join(os.path.dirname(__file__),"..","..","tools","ttsmanager.py")
			elif self.cmd=="DOCK":
				self.cmd=os.path.join(os.path.dirname(__file__),"..","..","dock","accessdock-config.py")
			elif self.cmd=="ANTI":
				self.cmd=self._getAppCmd("antimicrox")
			elif self.cmd=="EVIA":
				self.cmd=self._getAppCmd("eviacam")
			elif self.cmd=="BROWS":
				self.cmd=os.path.join(os.path.dirname(__file__),"..","..","tools","browsermanager.py")
		print(self.cmd)
		if "kcm" in self.cmd:
			proc=self.accesshelper.launchKcmModule(self.cmd)
		else:
			proc=self.accesshelper.launchCmd(self.cmd)
		self.finished.emit(proc)
	#def run
#class thLauncher

