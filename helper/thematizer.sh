#!/bin/bash
#Copyright 2021 Team LliureX
#Simple script to copy profiles to app dir
THEME=$1
SCHEME=$2
if [ "x$THEME" != "x" ]
then
	#applytheme
	plasma-apply-desktoptheme $THEME
fi

if [ "x$SCHEME" != "x" ]
then
	#applyscheme
	plasma-apply-colorscheme $SCHEME
fi

rm $HOME/.config/autostart/accesshelper_thematizer.desktop
