#!/bin/bash

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
echo $LOADED
[[ ${LOADED} -ne 0 ]] && exit

OUT=$(kwriteconfig5 --file kwinrc --group Plugins --key ${ID}Enabled true)
echo $OUT
qdbus org.kde.KWin /KWin org.kde.KWin.reconfigure
exit 0

if [[ $TYPE == "declarativescript" ]]
then
	CONT=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.loadDeclarativeScript $MAIN)
	echo "qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.loadDeclarativeScript $MAIN"
else
	CONT=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript $MAIN)
	echo "qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript $MAIN"
fi
echo "Launch $CONT"
if [[ $? -ne 0 ]]
then
	echo "ERROR"
fi
qdbus org.kde.KWin /$CONT run
#Twice because they gave me two
#qdbus org.kde.KWin /KWin org.kde.KWin.reconfigure
#sleep 1
#qdbus org.kde.KWin /KWin org.kde.KWin.reconfigure
echo "DONE"
