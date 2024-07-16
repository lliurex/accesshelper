// Version 2

import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.0
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kwin 2.0 as KWinComponents

Item {
    id: root
	property string wrkdir: Qt.resolvedUrl("./")

	PlasmaCore.DataSource {
		id: speaker
		engine: "executable"
		connectedSources: []
		onNewData: {
			var exitCode = data["exit code"]
			var exitStatus = data["exit status"]
			var stdout = data["stdout"]
			var stderr = data["stderr"]
			exited(exitCode, exitStatus, stdout, stderr)
			disconnectSource(sourceName) // cmd finished
		}
		function exec(cmd) {
			//takeScreenshot.setArguments([workspace.activeClient.internalId]);
			connectSource(cmd);
			console.log(cmd);
		}
		signal exited(int exitCode, int exitStatus, string stdout, string stderr)
	}

    KWinComponents.DBusCall {
        id: takeScreenshot
        //service: "org.kde.Spectacle"; path: "/"; method: "ActiveWindow";
        //service: "org.kde.KWin"; path: "/Screenshot"; method: "screenshotForWindow";
        service: "org.kde.KWin"; path: "/Screenshot"; method: "screenshotArea";
    }

	function updateConfig() {
		console.log("i");
	}

    Connections {
        target: options
        function onConfigChanged() { updateConfig(); }
    }

	Component.onCompleted: {
		var cmd = wrkdir.replace("file://","")+'tts.py';
		var stretch=KWin.readConfig("Stretch",1);
		var pitch=KWin.readConfig("Pitch",2);
		var rate=KWin.readConfig("Rate",3);
		var voice=KWin.readConfig("Voice","kal");
		var cmdWithArgs=cmd+" "+stretch+" "+pitch+" "+rate+" "+voice;
		KWin.registerShortcut("Toggle Window OCR", "Toggle Window OCR", "Ctrl+Meta+O", function() {  speaker.exec(cmdWithArgs); }); 
		//speaker.exec(cmdWithArgs);
		console.log(workspace.activeClient.internalId)
		//takeScreenshot.setArguments([0,0]);
		//takeScreenshot.setArguments([workspace.activeClient.internalId]);
		//takeScreenshot.setArguments([0,0,100,100]);
		//takeScreenshot.call();
	}

}
