#!/bin/bash
# Copyright 2024 LliureX Team
#Licensed under GPL-3 license
#https://www.gnu.org/licenses/gpl-3.0.en.html

function toggle
{
	qdbus org.kde.KWin /Effects org.kde.kwin.Effects.toggleEffect $ID
}

function load
{
	qdbus org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect $ID
}

function launchEffect
{
	echo "qdbus org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.invokeShortcut $NAME"
	qdbus org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.invokeShortcut ${NAME// /}
}

function enable
{
	if [[ $(qdbus org.kde.KWin /Effects org.kde.kwin.Effects.isEffectLoaded $ID) == "false" ]]
	then
		load
	fi
	[[ $(qdbus org.kde.KWin /Effects org.kde.kwin.Effects.loadedEffects | grep $ID) ]] || toggle
	[[ $(qdbus org.kde.KWin /Effects org.kde.kwin.Effects.activeEffects | grep $ID) ]] || launchEffect
}


METADATA=$1
ID=$(grep \"Id\" $METADATA)
ID=${ID/*: /}
ID=${ID//\"/}
ID=${ID/,/}
NAME=$(grep \"Name\" $METADATA)
NAME=${NAME/*: /}
NAME=${NAME//\"/}
NAME=${NAME/,/}
[[ $(qdbus org.kde.KWin /Effects org.kde.kwin.Effects.activeEffects | grep $ID) ]] && toggle || enable
exit 0
