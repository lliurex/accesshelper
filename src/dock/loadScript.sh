#!/bin/bash
# Copyright 2024 LliureX Team
#Licensed under GPL-3 license
#https://www.gnu.org/licenses/gpl-3.0.en.html

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
[[ ${LOADED} -ne 0 ]] && ENABLED="false" || ENABLED="true"
OUT=$(kwriteconfig5 --file kwinrc --group Plugins --key ${ID}Enabled $ENABLED)
qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.start
echo $ID
	if [[ $ID == "ocrwindow" ]]
	then
		qdbus org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.invokeShortcut "Toggle Window OCR"
	fi
#qdbus org.kde.KWin /KWin org.kde.KWin.reconfigure
exit 0
