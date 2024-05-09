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
echo M $MAIN
echo I $ID
LOADED=0
UNLOAD="true"
while [[ $UNLOAD == "true" ]]
do
	sleep 0.1
	UNLOAD=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript $MAIN)
	echo "U $UNLOAD"
	if [[ $UNLOAD == "false" ]]
	then
		UNLOAD=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript $ID)
	fi
	echo "U $UNLOAD"
	[[ $UNLOAD == "true" ]] && LOADED=1
done
echo $LOADED
echo "ESTO PASA SIEMPRE"
[[ ${LOADED} -ne 0 ]] && exit
echo "ESTO SOLO DEBE PASAR AL ACTIVARSE"
OUT=$(kwriteconfig5 --file kwinrc --group Plugins --key ${ID}Enabled true)
echo "kwriteconfig5 --file kwinrc --group Plugins --key ${ID}Enabled true"
qdbus org.kde.KWin /KWin org.kde.KWin.reconfigure
exit 0
