// Version 2

import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.0
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kwin 2.0 as KWinComponents

Item {
    id: root
	property string wrkdir: Qt.resolvedUrl("./")
	property var cWindow:""

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
			restoreWindow(cWindow);
		}
		function exec(cmd) {
			//takeScreenshot.setArguments([workspace.activeClient.internalId]);
			toggleDock.call();
			cWindow=workspace.activeClient;
			prepareWindow();
			connectSource(cmd);
		}

		function prepareWindow()
		{
			console.log(cWindow);
			cWindow.fullScreen=true;
		}

		function restoreWindow(cWindow)
		{
			console.log(cWindow)
			cWindow.fullScreen=false;
			toggleDock.call();
		}
		signal exited(int exitCode, int exitStatus, string stdout, string stderr)
	}


    KWinComponents.DBusCall {
        id: toggleDock
        //service: "org.kde.Spectacle"; path: "/"; method: "ActiveWindow";
        //service: "org.kde.KWin"; path: "/Screenshot"; method: "screenshotForWindow";
        service: "net.lliurex.accessibledock"; path: "/net/lliurex/accessibledock"; method: "toggle";
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
