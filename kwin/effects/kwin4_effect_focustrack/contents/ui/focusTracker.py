#!/usr/bin/python3
from llxaccessibility import llxaccessibility

accessibility=llxaccessibility.client()
print(accessibility.getCurrentFocusCoords())
