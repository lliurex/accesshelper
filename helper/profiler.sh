#!/bin/bash
#Copyright 2021 Team LliureX
#Simple script to copy profiles to app dir
WRKDIR="/usr/share/accesshelper/profiles"
if [[ "$2" == "acceshelper_profiler.desktop" ]]
then
	WRKDIR="/etc/xdg/autostart"
fi

DESTPATH=${WRKDIR}/$(basename $2)

cp -r $1 $DESTPATH && chmod 644 $DESTPATH
#And that's all
