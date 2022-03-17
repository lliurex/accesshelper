#!/usr/bin/python3
import subprocess
from . import functionHelper

class accesshelper():
	def __init__(*args):
		pass

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

	def setCursor(self,theme):
		err=0
		try:
			subprocess.run(["plasma-apply-cursortheme",theme],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
			err=1
		return(err)

	def setCursorSize(self,size):
		functionHelper._setKdeConfigSetting("Mouse","cursorSize","{}".format(size),"kcminputrc")

	def setScheme(self,scheme):
		err=0
		try:
			subprocess.run(["plasma-apply-colorscheme",theme],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
			err=1
		return(err)

	def setTheme(self,theme):
		err=0
		try:
			subprocess.run(["plasma-apply-desktoptheme",theme],stdout=subprocess.PIPE)
		except Exception as e:
			err=1
			print(e)
		return(err)
