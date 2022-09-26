#!/bin/bash
#Copyright 2022 Team LliureX
#Simple script to control beep on machine boot
BEEP="GRUB_INIT_TUNE"
TUNE="480 440 1"
GRUB="/etc/default/grub"
if [ x$1 == "xenable" ]
then
	if [[ -n $(grep "^#$BEEP" $GRUB)  ]]
	then 
		sed -i "s/^#$BEEP.*/$BEEP=\"$TUNE\"/g" $GRUB
	else
		if [[ -z $(grep "^$BEEP" /etc/default/grub)  ]]
		then
			echo "$BEEP=\"$TUNE\"" >> $GRUB
		fi
	fi
else
	sed -i "s/\($BEEP.*\)/#\0/g" $GRUB
fi

update-grub
