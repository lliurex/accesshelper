#!/usr/bin/python3
### This library implements atspi communications
import os,shutil,sys
from llxaccessibility import llxaccessibility

#if len(sys.argv)!=6:
#	sys.exit(-1)
accessibility=llxaccessibility.client()
accessibility.readScreen(onlyScreen=True)
