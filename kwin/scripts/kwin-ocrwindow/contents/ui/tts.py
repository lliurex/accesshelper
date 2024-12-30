#!/usr/bin/python3
### This library implements atspi communications
import os,shutil,sys
from llxaccessibility import llxaccessibility

accessibility=llxaccessibility.client()
accessibility.readScreen()
