#!/usr/bin/python3
import dbus
import json
bus=dbus.Bus()
busobj=bus.get_object("net.lliurex.accessibledock","/net/lliurex/accessibledock")
launchers={}
for objLauncher in busobj.getLaunchers():
	jsonLauncher=json.loads(objLauncher)
	if len(jsonLauncher[0].strip())>0:
		launchers[jsonLauncher[0]]=jsonLauncher[1]
print(launchers)
