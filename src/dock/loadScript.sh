#!/bin/bash

METADATA=$1
TYPE=$(grep X-Plasma-API $METADATA)
TYPE=${TYPE/*: /}
TYPE=${TYPE//\"/}
TYPE=${TYPE/,/}
ID=$(grep X-Plasma-MainScript $METADATA)
ID=${ID/*: /}
ID=${ID//\"/}
ID=${ID/,/}
ID=${METADATA/metadata.json/contents\/${ID}}
LOADED=0
UNLOAD=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript $ID)
while [[ $UNLOAD == "true" ]]
do
	sleep 0.1
	UNLOAD=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript $ID)
	LOADED=1
done
[[ ${LOADED} -ne 0 ]] && exit

if [[ $TYPE == "declarativescript" ]]
then
	CONT=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.loadDeclarativeScript $ID)
	echo "qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.loadDeclarativeScript $ID"
else
	CONT=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript $ID)
	echo "qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript $ID"
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
