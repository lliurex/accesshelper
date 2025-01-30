#!/usr/bin/python3
import sys,os,signal
from llxaccessibility import llxaccessibility

accessibility=llxaccessibility.client()

def _print(self,*args):
	print(args)
try:
	accessibility.trackFocus(_print)
except Exception as e:
	print(e)
	pass

