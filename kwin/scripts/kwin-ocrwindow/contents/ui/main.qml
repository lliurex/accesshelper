// Version 2

import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.0
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kwin 3.0 as KWin
import org.kde.plasma.plasma5support as Plasma5support

Item {
    id: root
	property string wrkdir: Qt.resolvedUrl("./")
	property var cWindow:""
	property var cmd

	Plasma5support.DataSource {
		id: speaker
		engine: "executable"
		connectedSources: []
		onNewData: {
			var exitCode = speaker.data["exit code"]
			var exitStatus = speaker.data["exit status"]
			var stdout = speaker.data["stdout"]
			var stderr = speaker.data["stderr"]
			exited(exitCode, exitStatus, stdout, stderr)
			disconnectSource(speaker) // cmd finished
			restoreWindow(root.cWindow);
		}
		function exec(cmd) {
			//takeScreenshot.setArguments([workspace.activeClient.internalId]);
			toggleDock.call();
			console.log(cmd);
			root.cWindow=KWin.Workspace.activeWindow;
			console.log(cWindow);
			prepareWindow(cWindow);
			connectSource(cmd);
		}

		function prepareWindow(cWindow)
		{
			console.log("prepare "+cWindow);
			cWindow.fullScreen=true;
		}

		function restoreWindow(cWindow)
		{
			console.log(cWindow);
			cWindow.fullScreen=false;
			console.log("END");
			toggleDock.call();
		}
		signal exited(int exitCode, int exitStatus, string stdout, string stderr)
	}


    KWin.DBusCall {
        id: toggleDock
        //service: "org.kde.Spectacle"; path: "/"; method: "ActiveWindow";
        //service: "org.kde.KWin"; path: "/Screenshot"; method: "screenshotForWindow";
        service: "net.lliurex.accessibledock"; path: "/net/lliurex/accessibledock"; method: "toggle";
    }

    KWin.DBusCall {
        id: takeScreenshot
        //service: "org.kde.Spectacle"; path: "/"; method: "ActiveWindow";
        //service: "org.kde.KWin"; path: "/Screenshot"; method: "screenshotForWindow";
        service: "org.kde.KWin"; path: "/Screenshot"; method: "screenshotArea";
    }

	function updateConfig() {
		console.log("i");
	}

	KWin.ShortcutHandler {
		name: "Toggle Window OCR"
		text: "Toggle Window OCR"
		sequence: 'Meta+Ctrl+O'
		onActivated: speaker.exec(cmd)
	}

	Component.onCompleted: {
		root.cmd = wrkdir.replace("file://","")+'tts.py';
		//KWin.registerShortcut("Toggle Window OCR", "Toggle Window OCR", "Ctrl+Meta+O", function() {  speaker.exec(cmd); }); 
		//speaker.exec(cmdWithArgs);
		//takeScreenshot.setArguments([0,0]);
		//takeScreenshot.setArguments([workspace.activeClient.internalId]);
		//takeScreenshot.setArguments([0,0,100,100]);
		//takeScreenshot.call();
	}

}
