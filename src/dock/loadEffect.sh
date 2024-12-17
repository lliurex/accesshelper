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

function unload
{
	if [[ $ID == "magnifier" ]] || [[ $ID == "zoom" ]]
	then
		qdbus org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.invokeShortcut "view_zoom_out"
	fi
	qdbus org.kde.KWin /Effects org.kde.kwin.Effects.toggleEffect $ID
	qdbus org.kde.KWin /Effects org.kde.kwin.Effects.unloadEffect $ID
}

function launchEffect
{
	echo "qdbus org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.invokeShortcut $NAME"
	qdbus org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.invokeShortcut "${NAME}"
}

function enable
{
	if [[ $(qdbus org.kde.KWin /Effects org.kde.kwin.Effects.isEffectLoaded $ID) == "false" ]]
	then
		load
		[[ $(qdbus org.kde.KWin /Effects org.kde.kwin.Effects.loadedEffects | grep $ID) ]] || toggle
		[[ $(qdbus org.kde.KWin /Effects org.kde.kwin.Effects.activeEffects | grep $ID) ]] || launchEffect
	else
		unload
	fi
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
CHK_MAGNIFIERS=$(grep \"exclusiveGroup\" $METADATA)
[ ${#CHK_MAGNIFIERS} -ne 0 ] && NAME="view_zoom_in"
[[ $(qdbus org.kde.KWin /Effects org.kde.kwin.Effects.activeEffects | grep $ID) ]] && toggle || enable
exit 0
