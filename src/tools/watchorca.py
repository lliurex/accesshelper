#!/usr/bin/python3
import psutil
import os,sys
import subprocess
import dbus,dbus.exceptions
from orca import debug
import multiprocessing
import time
import pyatspi

def _launchDbusTh():
	proc=multiprocessing.Process(target=_launchDbus)
	proc.start()
	return(proc)
#def _launchDbusTh

def _launchDbus():
	cmd=["/usr/bin/dbus-launch","/usr/libexec/at-spi-bus-launcher","--launch-immediately","--a11y=1""--screen-reader=1"]
	#print(" ".join(cmd))
	subprocess.run(cmd)
#def _launchDbus

def _launchDbusRegistryTh():
	proc=multiprocessing.Process(target=_launchDbusRegistry)
	proc.start()
	return(proc)
#def _launchDbusRegistryTh():

def _launchDbusRegistry():
	cmd=["/usr/bin/dbus-launch","/usr/libexec/at-spi2-registryd"]
	#print(" ".join(cmd))
	subprocess.run(cmd)
#def _launchDbusRegistry():

def _launchOrcaTh():
	proc=multiprocessing.Process(target=_launchOrca)
	proc.start()
	return(proc)
#def _launchOrcaTh

def _launchOrca():
	cmd=["/usr/bin/orca","--replace"]
	#print(" ".join(cmd))
	subprocess.run(cmd)
#def _launchOrca

def _launchPlasmaReplacesTh():
	proc=multiprocessing.Process(target=_launchPlasmaReplaces)
	proc.start()
	return(proc)
#def _launchPlasmaReplacesTh

def _launchPlasmaReplaces():
	cmd=["/usr/bin/plasmashell","--replace"]
	#print(" ".join(cmd))
	subprocess.run(cmd)
#def _launchPlasmaReplaces

def _launchKWinReplacesTh():
	proc=multiprocessing.Process(target=_launchKWinReplaces)
	proc.start()
	return(proc)
#def _launchKWinReplacesTh

def _launchKWinReplaces():
	cmd=["/usr/bin/kwin","--replace"]
	#print(" ".join(cmd))
	subprocess.run(cmd)
#def _launchPlasmaReplaces

def launchDbus():
		print("LAUNCH DBUS")
		processes.append(_launchDbusTh())
		print("LANZADO")
		processes.append(_launchDbusRegistryTh())
#def launchDbus

def launchOrca():
	#print("LAUNCH ORCA")
	processes.append(_launchOrcaTh())
#def launchOrca

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
			#print("err: ".format(e))
			pass
		else:
			with open(fcontrol,"w") as f:
				f.write(".")
			os.chmod(fcontrol,0o777)
			sw=True
		 	#pyatspi.Registry().getDesktop(0)
		os._exit(sw)
		#return sw
	else:
		os.waitpid(pid, 0)
		sw=os.path.exists(fcontrol)
		return(sw)
#def _isDbusAccessible():

def _isOrcaAccessible():
	sw=False
	try:
		debug.examineProcesses()
		sw=True
	except:
		pass
	else:
		sw=_isOrcaRunning()
	return(sw)
#def _isOrcaAccessible

def _isOrcaRunning():
	sw=False
	user=os.environ.get("USER")
	#psutil process_iter is slow, even more if filters enabled
	cmd=["ps","-ef"]
	proc=subprocess.check_output(cmd,universal_newlines=True,encoding="utf8")
	u=os.environ.get("USER")
	for p in proc.split("\n"):
		pArray=p.split()
		if len(pArray)<9:
			continue
		if pArray[0]!=u:
			continue
		if pArray[8]=="/usr/bin/orca":
			sw=True
			break
	#it would be amazing if were working...
	#bus=dbus.Bus()
	#dobj=bus.get_object("org.a11y.Bus","/org/a11y/bus")
	#dint=dbus.Interface(dobj,"org.freedesktop.DBus.Properties")
	#sw=bool(int.Get("org.a11y.Status","ScreenReaderEnabled"))
	return(sw)
#def _isOrcaRunning


def isAlive():
	swDbus=_isDbusAccessible()
	swOrca=False
	#print("ISALIE {}".format(sw))
	if swDbus==True:
		#print("CHECK ORCA")
		swOrca=_isOrcaAccessible()
	return([swDbus,swOrca])
#def isAlive

cmd=["/usr/bin/kreadconfig5","--file","kaccessrc","--group","ScreenReader","--key","Enabled"]
out=subprocess.check_output(cmd,universal_newlines=True,encoding="utf8")
if out.strip().lower()!="true":
	sys.exit(0)
processes=[]
cont=0
while True:
	swDbus,swOrca=isAlive()
	if swDbus&swOrca==False:
		if swDbus==False:
			launchDbus()
		if swOrca==False:
			launchOrca()
			if cont==1:
				processes.append(_launchKWinReplacesTh())
				time.sleep(2)
				processes.append(_launchPlasmaReplacesTh())
			cont=1
	#else:
		#print("OK")
	time.sleep(10)
