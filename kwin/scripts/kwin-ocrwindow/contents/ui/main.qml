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
			console.log("FINISHED");
			var cWindow=workspace.activeClient;
			restoreWindow(cWindow);
		}
		function exec(cmd) {
			//takeScreenshot.setArguments([workspace.activeClient.internalId]);
			prepareWindow();
			console.log("INIT");
			connectSource(cmd);
			console.log(cmd);
		}

		function prepareWindow()
		{
			console.log("INIT PREPARE");
			console.log(workspace.activeClient);
			var cWindow=workspace.activeClient;
			console.log("W selected");
			cWindow.fullScreen=true;
			console.log("END PREPARE");
		}

		function restoreWindow(cWindow)
		{
			console.log("END RESTORE");
			cWindow.fullScreen=false;
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
		KWin.registerShortcut("Toggle Window OCR", "Toggle Window OCR", "Ctrl+Meta+O", function() {  speaker.exec(cmd); }); 
		//speaker.exec(cmdWithArgs);
		console.log(workspace.activeClient.internalId)
		//takeScreenshot.setArguments([0,0]);
		//takeScreenshot.setArguments([workspace.activeClient.internalId]);
		//takeScreenshot.setArguments([0,0,100,100]);
		//takeScreenshot.call();
	}

}
