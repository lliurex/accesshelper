/**/

import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.12 as Kirigami
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kwin 3.0 as KWinComponents

Item {
    id: root
	property string wrkdir: Qt.resolvedUrl("./")

    Loader {
        id: frameLoader
    }
	PlasmaCore.DataSource {
		id: tracker
		engine: "executable"
		connectedSources: []
		onNewData: {
			var exitCode = data["exit code"];
			var exitStatus = data["exit status"];
			var stdout = data["stdout"];
			var stderr = data["stderr"];
			let arrayOut=stdout.trim().split("\n");
			var focusItem=arrayOut[Object.keys(arrayOut).length-1];
			console.log(focusItem);
			if (focusItem.length>0)
			{
				try {
					var jsonOut=eval("("+focusItem+")");
					console.log(jsonOut.x);
					moveFrame(jsonOut);
				} catch (err) {
					console.log("**");
					console.error(err);
				}
			}
			exited(exitCode, exitStatus, stdout, stderr)
			disconnectSource(sourceName) // cmd finished
		}

		function exec() {
			let cmd = wrkdir.replace("file://","")+'focusTracker.py';
			console.log(cmd);
			connectSource(cmd);
		}

		signal exited(int exitCode, int exitStatus, string stdout, string stderr)
	}

    property color borderColor: "yellow" 
    property int borderHeight: 14
    property bool show: true

    function readConfig(){
        borderColor= KWin.readConfig("BorderColor",Qt.rgba(0,0,1,0.1));
        borderHeight= KWin.readConfig("BorderHeight",2);
    }

    function updateConfig(){
		console.log("**** UPDATE ****")
    }

    function applyConfig(){
		readConfig();
       var focusFrame;
       readConfig();
       frameLoader.source = "frame.qml";
       focusFrame=frameLoader.item;
    }

    function moveFrame(coords){
       var focusFrame;
       if (!frameLoader.item) {
           applyConfig();
       }
       focusFrame=frameLoader.item;
	   borderHeight=borderHeight+5;
	   focusFrame.moveFrame(coords.x-borderHeight,coords.y-borderHeight,coords.w+borderHeight,coords.h+borderHeight*2);
    }


    Connections {
        target: KWinComponents.Options
        function onConfigChanged() { updateConfig(); }
    }

    Connections {
        target: KWinComponents.Options
        function onConfigChanged() { updateConfig(); }
    }

    KWinComponents.DBusCall {
        id: kwinReconfigure
        service: "org.kde.KWin"; path: "/KWin"; method: "reconfigure";
    }

	Component.onCompleted: {
		//KWin.registerShortcut("Toggle Window OCR", "Toggle Window OCR", "Ctrl+Meta+O", function() {  speaker.exec(cmd); }); 
		tracker.exec();
		console.log(workspace.activeClient.internalId)
		//takeScreenshot.setArguments([0,0]);
		//takeScreenshot.setArguments([workspace.activeClient.internalId]);
		//takeScreenshot.setArguments([0,0,100,100]);
		//takeScreenshot.call();
}
    }
