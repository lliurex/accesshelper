#!/bin/bash
#Copyright 2022 Team LliureX
#Simple script to control accessibility options
[ $# -ne 3 ] && exit 1
SW_GRUB=$1
SW_SDDM=$2
SW_ORCA=$3

function enableOrcaOnSddm()
{
	echo "TIMEOUT=10" > /usr/share/accesswizard/tools/timeout
	enableBeepOnSddm
}
function disableOrcaOnSddm()
{
	rm /usr/share/accesswizard/tools/timeout || true
}

function enableBeepOnSddm()
{
	systemctl enable pulse-sddm
}

function disableBeepOnSddm()
{
	systemctl disable pulse-sddm
}

function enableBeepOnGrub()
{
	BEEP="GRUB_INIT_TUNE"
	TUNE="480 440 1"
	GRUB="/etc/default/grub"
	if [[ -n $(grep "^#$BEEP" $GRUB)  ]]
	then 
		sed -i "s/^#$BEEP.*/$BEEP=\"$TUNE\"/g" $GRUB
	else
		if [[ -z $(grep "^$BEEP" /etc/default/grub)  ]]
		then
			echo "$BEEP=\"$TUNE\"" >> $GRUB
		fi
	fi
	update-grub
}

function disableBeepOnGrub()
{
	sed -i "s/\($BEEP.*\)/#\0/g" $GRUB
	update-grub
}

[ x$SW_GRUB == "xTrue" ] && enableBeepOnGrub
[ x$SW_GRUB == "xFalse" ] && disableBeepOnGrub
[ x$SW_SDDM == "xTrue" ] && enableBeepOnSddm
[ x$SW_SDDM == "xFalse" ] && disableBeepOnSddm
[ x$SW_ORCA == "xTrue" ] && enableOrcaOnSddm
[ x$SW_ORCA == "xFalse" ] && disableOrcaOnSddm
