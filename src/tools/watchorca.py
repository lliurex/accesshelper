#!/usr/bin/python3
import psutil,signal
import os,sys
import subprocess
import dbus,dbus.exceptions
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
import multiprocessing
import time
import pyatspi
import gettext
gettext.textdomain('accesswizard')
_ = gettext.gettext

i18n={"ORCA_WARNING":_("Orca warning"),
	"PLASMA_RESTARTED":_("Due a system error Plasma has been restarted"),
	}

def _log(msg):
	#REM comment
	#return()
	with open("/tmp/orca.log","a") as f:
		f.write("{}\n".format(str(msg)))
#def _log
		
def _launchDbusTh():
	proc=multiprocessing.Process(target=_launchDbus)
	proc.start()
	return(proc)
#def _launchDbusTh

def _launchDbus():
	cmd=["/usr/bin/dbus-launch","/usr/libexec/at-spi-bus-launcher","--launch-immediately","--a11y=1""--screen-reader=1"]
	#_log(" ".join(cmd))
	subprocess.run(cmd)
#def _launchDbus

def _launchDbusRegistryTh():
	proc=multiprocessing.Process(target=_launchDbusRegistry)
	proc.start()
	return(proc)
#def _launchDbusRegistryTh():

def _launchDbusRegistry():
	cmd=["/usr/bin/dbus-launch","/usr/libexec/at-spi2-registryd"]
	#_log(" ".join(cmd))
	subprocess.run(cmd)
#def _launchDbusRegistry():

def _launchOrcaTh():
	proc=multiprocessing.Process(target=_launchOrca)
	proc.start()
	return(proc)
#def _launchOrcaTh

def _launchOrca():
	cmd=["/usr/bin/orca","--replace"]
	#_log(" ".join(cmd))
	p=subprocess.run(cmd)
	_log(p)
	_log("Orca returncode: {}".format(p.returncode))
#def _launchOrca

def _launchPlasmaReplacesTh():
	proc=multiprocessing.Process(target=_launchPlasmaReplaces)
	proc.start()
	return(proc)
#def _launchPlasmaReplacesTh

def _launchPlasmaReplaces():
	cmd=["/usr/bin/plasmashell","--replace"]
	subprocess.run(cmd)
#def _launchPlasmaReplaces

def _launchKWinReplacesTh():
	proc=multiprocessing.Process(target=_launchKWinReplaces)
	proc.start()
	return(proc)
#def _launchKWinReplacesTh

def _launchKWinReplaces():
	cmd=["/usr/bin/kwin","--replace"]
	#_log(" ".join(cmd))
	subprocess.run(cmd)
#def _launchPlasmaReplaces

def launchDbus():
		_log("Launching thread for D-Bus")
		#processes.append(_launchDbusTh())
		_launchDbusTh()
		_log("Register a11y")
		_launchDbusRegistryTh()
#def launchDbus

def _isDbusAccessible():
	sw=False
	fcontrol="/tmp/.dbuscontrolorca"
	if os.path.isfile(fcontrol):
		os.unlink(fcontrol)
	pid=os.fork()
	if pid==0:
		sw=False
		try:
			pyatspi.Registry().getDesktop(0)
		except Exception as e:
			#_log("err: ".format(e))
			pass
		else:
			with open(fcontrol,"w") as f:
				f.write(".")
			os.chmod(fcontrol,0o777)
			sw=True
		os._exit(sw)
	else:
		os.waitpid(pid, 0)
		sw=os.path.exists(fcontrol)
		return(sw)
#def _isDbusAccessible():

def getA11yScreenReaderEnabled():
	bus=dbus.Bus()
	dobj=bus.get_object("org.a11y.Bus","/org/a11y/bus")
	dint=dbus.Interface(dobj,"org.freedesktop.DBus.Properties")
	return(bool(dint.Get("org.a11y.Status","ScreenReaderEnabled")))
#def getConfigScreenReaderEnabled

def getConfigScreenReaderEnabled():
	cmd=["/usr/bin/kreadconfig5","--file","kaccessrc","--group","ScreenReader","--key","Enabled"]
	out=subprocess.check_output(cmd,universal_newlines=True,encoding="utf8")
	return(bool(out.capitalize()))
#def getConfigScreenReaderEnabled

def getOrcaPID():
	pid=0
	user=os.environ.get("USER")
	#psutil process_iter is slow, even more if filters enabled
	cmd=["ps","-ef"]
	proc=subprocess.check_output(cmd,universal_newlines=True,encoding="utf8")
	u=os.environ.get("USER")
	for p in proc.split("\n"):
		if p.startswith(u)==False:
			continue
		if p.count(" ")<9:
			continue
		if " /usr/bin/orca " not in p:
			continue
		pArray=p.split()
		if pArray[8]=="/usr/bin/orca":
			pid=int(pArray[1])
			break
	return pid
#def getOrcaPID

def orcaloop(*args):
	if _isDbusAccessible()==False:
		launchDbus()
	if getOrcaPID()==0:
		if getConfigScreenReaderEnabled()==True:
			if getA11yScreenReaderEnabled()==True:
			#There's no ORCA pid but is enabled by config
			#and a11y thinks that is enabled so restart it
				_launchOrcaTh()
			#Plasma, sometimes, doesn't work. Restarting it solves the issue
			#Not a good solution, better than a desktop muted anyway...
				if args[0]!="boot":
					_launchKWinReplacesTh()
					_launchPlasmaReplacesTh()
					time.sleep(5)
					bus=dbus.Bus()
					dobj=bus.get_object("org.freedesktop.Notifications","/org/freedesktop/Notifications")
					dint=dbus.Interface(dobj,"org.freedesktop.Notifications")
					dint.Notify("",0,"",i18n.get("ORCA_WARNING"),i18n.get("PLASMA_RESTARTED"),[],{"urgency": 1},10000)
	return True
#def orcaloop

## MAIN LOOP ##
orcaloop("boot")
GLib.timeout_add_seconds(10,orcaloop,"")
GLib.MainLoop().run()
