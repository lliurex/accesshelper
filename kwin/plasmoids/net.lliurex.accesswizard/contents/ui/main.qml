import QtQuick 2.15
import QtQuick.Layouts 1.15

import org.kde.plasma.plasmoid 2.0
import org.kde.plasma.core 2.1 as PlasmaCore
import org.kde.plasma.components 3.0 as PlasmaComponents
import org.kde.plasma.extras 2.0 as PlasmaExtras
import org.kde.kwin 2.0 as KWinComponents
//import net.lliurex.accesswizard 1.0

// Item - the most basic plasmoid component, an empty container.
Item {

	id:main
	property string wrkdir: Qt.resolvedUrl("./")
	Plasmoid.switchWidth: PlasmaCore.Units.gridUnit * 5
	Plasmoid.switchHeight: PlasmaCore.Units.gridUnit * 5
	Plasmoid.hideOnWindowDeactivate: true
	Plasmoid.icon: "accesswizard"
	Plasmoid.toolTipMainText: i18n("Accessibility Helper")
	Plasmoid.toolTipSubText: i18n("Quick launcher for accessibility")

	ListModel {
		id: launchersModel
	}

	PlasmaCore.DataSource {
		id: launchers
		engine: "executable"
		connectedSources: []
		onNewData: {
			var exitCode = data["exit code"]
			var exitStatus = data["exit status"]
			var stdout = data["stdout"]
			var stderr = data["stderr"]
			if ((stdout.trim()!="") && (stdout[0]==="{"))
			{
				processData(stdout);
			}
			onSourceDisconnected:{
				reload();
			}
			exited(exitCode, exitStatus, stdout, stderr)
			disconnectSource(sourceName) // cmd finished
		} //OnNewData

		function processData(stdout) {
			stdout=sanitizeOutput(stdout)
			var jsonout={}
			try {
				jsonout=JSON.parse(stdout)
			} catch (e) {
				console.error("Err:" + e)
				return;
			}
			launchersModel.clear()
			var objkeys=Object.keys(jsonout)
			objkeys.forEach(item=>{
				var objItem=jsonout[item]
				launchersModel.append({"name":objItem["Name"],
					"exec":objItem["Exec"],
					"icon":objItem["Icon"]})
				});
			var bus="net.lliurex.accessibility.Dock";
			launchersModel.append({"name": i18n("Toggle dock"),
				"exec":"qdbus "+bus+" /"+bus.replace(/\./g,"/")+" "+bus+".toggle",
				"icon":"accesswizard"})
		} //processData

		function sanitizeOutput(stdout) {
			//1st " as character sequence
			stdout=stdout.replace(/\"/g,'###%%%');
			//2nd keys must be between "
			stdout=stdout.replace(/, \'/g,', "');
			stdout=stdout.replace(/\':/g,'":');
			stdout=stdout.replace(/{\'/g,'{"');
			//3rd remove sequence (could be done at 1st)
			stdout=stdout.replace(/###%%%/g,'');
			//4th all apostrophes to "
			stdout=stdout.replace(/\'/g,'"');
			//5th bool values
			stdout=stdout.replace(/False/g,'\"False\"');
			stdout=stdout.replace(/True/g,'\"True\"');
			return(stdout);
		} // sanitizeOutput

		function exec(cmd) {
			console.log("Exec: "+cmd)
			connectSource(cmd)
		} //exec
		signal exited(int exitCode, int exitStatus, string stdout, string stderr)
	}

	Plasmoid.preferredRepresentation: Plasmoid.fullRepresentation
   
	Plasmoid.fullRepresentation: PlasmaComponents.Page {
		implicitWidth: PlasmaCore.Units.gridUnit * 12
		implicitHeight: PlasmaCore.Units.gridUnit * 6

		PlasmaExtras.PlaceholderMessage {
			//anchors.centerIn: parent
			anchors.bottom: parent.bottom
			width: parent.width - (PlasmaCore.Units.gridUnit * 4)
			iconName: Plasmoid.icon
			text:Plasmoid.toolTipSubText
		}
		ColumnLayout {
			width: parent.width 
			height: parent.height - (PlasmaCore.Units.gridUnit * 2)
			ListView {
				Layout.fillWidth: true
				Layout.fillHeight: true
				Layout.margins:PlasmaCore.Units.gridUnit/2
				spacing:PlasmaCore.Units.gridUnit/20
				model: launchersModel
				delegate: launcherDelegate
			}


		}
	}
	Component {
		id: launcherDelegate
		PlasmaComponents.Button {
			Layout.margins:PlasmaCore.Units.gridUnit/2
			height:PlasmaCore.Units.gridUnit*2
			width: parent? parent.width:PlasmaCore.Units.gridUnit*10
		   	text: model.name 
			icon.name:model.icon
			onClicked:{Plasmoid.expanded=false;launchers.exec(model.exec)}
		}
	}
	Component.onCompleted: {
		plasmoid.removeAction("configure");
		reload();
		plasmoid.setAction("configureDock", i18n("Configure Dock"),"Configure Dock")
		plasmoid.setAction("accessWizard", i18n("Access Wizard"),"Access Wizard")
	}

	function reload() {
		var cmd = wrkdir.replace("file://","")+'dockinfo.py';
		launchers.exec(cmd);

	}

	function action_accessWizard() {
		launchers.exec("/usr/share/accesswizard/accesswizard.py")
	}
	function action_configureDock() {
		launchers.exec("/usr/share/accesswizard/dock/accessdock-config.py")
	}

 }	
