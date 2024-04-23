#!/bin/bash

ID=$1
ACTION=$2
UNLOAD=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript $ID)
while [[ $UNLOAD == "true" ]]
do
	sleep 0.1
	UNLOAD=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript $ID)
done
[[ ${#ACTION} -eq 0 ]] && exit
CONT=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript $ID)
echo "Launch $CONT"
if [[ $? -ne 0 ]]
then
	CONT=$(qdbus org.kde.KWin /Scripting org.kde.kwin.Scripting.loadDeclarativeScript $ID)
fi
#Twice because they gave me two
qdbus org.kde.KWin /KWin org.kde.KWin.reconfigure
sleep 1
qdbus org.kde.KWin /KWin org.kde.KWin.reconfigure
echo "DONE"
