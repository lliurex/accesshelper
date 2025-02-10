#!/usr/bin/env python3
import sys
import zlib
import json
import signal
import dbus,dbus.service,dbus.exceptions
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from llxaccessibility import llxaccessibility
import logging

class accessibilityDbusMethods(dbus.service.Object):
	def __init__(self,bus_name,*args,**kwargs):
		super().__init__(bus_name,"/net/lliurex/accessibility")
		logging.basicConfig(format='%(message)s')
		self.dbg=True
#		signal.signal(signal.SIGUSR1, self._reloadSignal)
		self.accessibility=llxaccessibility.client()
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			logging.debug("accessibility-dbus: %s"%str(msg))
			print("accessibility-dbus: %s"%str(msg))
	#def _debug

	def _print(self,msg):
		logging.info("accessibility-dbus: %s"%str(msg))
	#def _print

	def _emitFocusChanged(self,*args,**kwargs):
		if len(args)>0:
			coords=args[0]
		print(args[0])
		if isinstance(coords,dict):
			fields=["x","y","w","h"]
			total=0
			for field in fields:
				total+=coords.get(field,0)
			if total>0:	
				self.focusChanged(str(coords))
	#def _updatedSignal

	@dbus.service.signal("net.lliurex.accessibility")
	def focusChanged(self,*args,**kwargs):
		pass
	#def focusChanged

	@dbus.service.method("net.lliurex.accessibility",
						 in_signature='', out_signature='b')
	def trackFocus(self):
		self.accessibility.trackFocus(self._emitFocusChanged)
		return(True)
	#def trackFocus

	@dbus.service.method("net.lliurex.accessibility",
						 in_signature='', out_signature='a{sn}')
	def getCurrentFocusCoords(self):
		coords=self.accessibility.getCurrentFocusCoords()
		self._emitFocusChanged(coords)
		return(coords)
	#def getCurrentFocusCoords

	def _reloadSignal(self,*args,**kwargs):
		self.reloadSignal()
	#def _reloadSignal
#class accessibilityDbusMethods

class accessibilityDBus():
	def __init__(self): 
		self._setDbus()
	#def __init__

	def _setDbus(self):
		DBusGMainLoop(set_as_default=True)
		loop = GLib.MainLoop()
		# Declare a name where our service can be reached
		try:
			bus_name = dbus.service.BusName("net.lliurex.accessibility",
											bus=dbus.Bus(),
											do_not_queue=True)
		except dbus.exceptions.NameExistsException:
			print("service is already running")
			sys.exit(1)

		accessibilityDbusMethods(bus_name)
		# Run the loop
		try:
			loop.run()
		except KeyboardInterrupt:
			print("keyboard interrupt received")
		except Exception as e:
			print("Unexpected exception occurred: '{}'".format(str(e)))
		finally:
			loop.quit()
	#def _setDbus
#class accessibilityDBus

accessibilityDBus()
