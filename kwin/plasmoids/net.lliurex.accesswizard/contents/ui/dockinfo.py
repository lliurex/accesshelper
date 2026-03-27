#!/usr/bin/python3
import dbus
import json
bus=dbus.Bus()
busobj=bus.get_object("net.lliurex.accessibility.Dock","/net/lliurex/accessibility/Dock")
launchers={}
for objLauncher in busobj.getLaunchers():
	jsonLauncher=json.loads(objLauncher)
	if len(jsonLauncher[0].strip())>0:
		launchers[jsonLauncher[0]]=jsonLauncher[1]
for l,d in launchers.items():
	for desc,val in d.items():
		if isinstance(val,str):
			d[desc]=val.replace("'","%%%%")
print(launchers)
