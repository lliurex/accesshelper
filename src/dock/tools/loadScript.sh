#!/bin/bash
# Copyright 2024 LliureX Team
#Licensed under GPL-3 license
#https://www.gnu.org/licenses/gpl-3.0.en.html

ALWAYS_ON="ocrwindow" #Whitespace separated scripts
METADATA=$1
TYPE=$(grep X-Plasma-API $METADATA)
TYPE=${TYPE/*: /}
TYPE=${TYPE//\"/}
TYPE=${TYPE/,/}
MAIN=$(grep X-Plasma-MainScript $METADATA)
MAIN=${MAIN/*: /}
MAIN=${MAIN//\"/}
MAIN=${MAIN/,/}
MAIN=${METADATA/metadata.json/contents\/${MAIN}}
ID=$(grep \"Id\" $METADATA)
ID=${ID/*: /}
ID=${ID//\"/}
ID=${ID/,/}
LOADED=0
UNLOAD="true"
while [[ $UNLOAD == "true" ]]
do
	sleep 0.1
	UNLOAD=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript $MAIN)
	if [[ $UNLOAD == "false" ]]
	then
		UNLOAD=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript $ID)
	fi
	[[ $UNLOAD == "true" ]] && LOADED=1
done
echo "Selected script $ID"
[[ $(echo $ALWAYS_ON | grep ${ID,,}) ]] && LOADED=0
[[ ${LOADED} -ne 0 ]] && ENABLED="false" || ENABLED="true"
echo "Script data: {LOADED} $LOADED {UNLOADED} $UNLOAD {ENABLED} $ENABLED"
OUT=$(kwriteconfig6 --file kwinrc --group Plugins --key ${ID}Enabled $ENABLED)
#Ensure script engine is on
qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.start
case $ID in
	"ocrwindow")
		qdbus org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.invokeShortcut "Toggle Window OCR"
		;;
	*)
		;;
esac
#qdbus org.kde.KWin /KWin org.kde.KWin.reconfigure
exit 0
