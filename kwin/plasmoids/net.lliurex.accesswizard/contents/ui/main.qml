import QtQuick 2.15
import QtQuick.Layouts 1.15


import org.kde.plasma.plasmoid 2.0
import org.kde.kirigami 2.20 as Kirigami
import org.kde.plasma.components 3.0 as PlasmaComponents
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasma5support 2.0 as PlasmaSupport
import org.kde.plasma.extras 2.0 as PlasmaExtras
//import net.lliurex.accesswizard 1.0

// Item - the most basic plasmoid component, an empty container.
PlasmoidItem {

	id:main
	property string wrkdir: Qt.resolvedUrl("./")
	switchWidth: Kirigami.Units.gridUnit * 5
	switchHeight: Kirigami.Units.gridUnit * 5
	hideOnWindowDeactivate: true
	Plasmoid.icon: "accessibledock"
	toolTipMainText: i18n("Accessibility Helper")
	toolTipSubText: i18n("Quick launcher for accessibility")

	ListModel {
		id: launchersModel
	}

	PlasmaSupport.DataSource {
		id: launchers
		engine: "executable"
		connectedSources: []
		onNewData:  {
			var exitCode = data["exit code"];
			var exitStatus = data["exit status"];
			var stdout = data["stdout"];
			var stderr = data["stderr"];
			if ((stdout.trim()!="") && (stdout[0]==="{"))
			{
				processData(stdout);
			}
			onSourceDisconnected:{
				reload();
			}
			exited(exitCode, exitStatus, stdout, stderr);
			disconnectSource(sourceName); // cmd finished
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

	//preferredRepresentation: Plasmoid.fullRepresentation
   
	fullRepresentation: PlasmaComponents.Page {
		implicitWidth: Kirigami.Units.gridUnit * 12
		implicitHeight: Kirigami.Units.gridUnit * 6

		PlasmaExtras.PlaceholderMessage {
			//anchors.centerIn: parent
			anchors.bottom: parent.bottom
			width: parent.width - (Kirigami.Units.gridUnit * 4)
			iconName: Plasmoid.icon
			text:main.toolTipSubText
		}
		ColumnLayout {
			width: parent.width 
			height: parent.height - (Kirigami.Units.gridUnit * 2)
			ListView {
				Layout.fillWidth: true
				Layout.fillHeight: true
				Layout.margins:Kirigami.Units.gridUnit/2
				spacing:Kirigami.Units.gridUnit/20
				model: launchersModel
				delegate: launcherDelegate
			}


		}
	}
	Component {
		id: launcherDelegate
		PlasmaComponents.Button {
			Layout.margins:Kirigami.Units.gridUnit/2
			height:Kirigami.Units.gridUnit*2
			width: parent? parent.width:Kirigami.Units.gridUnit*10
		   	text: model.name 
			icon.name:model.icon
			onClicked:{Plasmoid.expanded=false;launchers.exec(model.exec)}
		}
	}
	Component.onCompleted: {
		//root.removeAction("configure");
		reload();
		//root.setAction("configureDock", i18n("Configure Dock"),"Configure Dock")
		//root.setAction("accessWizard", i18n("Access Wizard"),"Access Wizard")
	}

    Plasmoid.contextualActions: [
        PlasmaCore.Action {
            text: i18nc(i18n("Configure Dock"), i18n("Configure Dock"))
            icon.name: "list-edit"
            onTriggered: configureDock()
        },
        PlasmaCore.Action {
            text: i18nc(i18n("Access Wizard"), i18n("Access Wizard"))
            icon.name: "list-edit"
            onTriggered: accessWizard()
        }
    ]


	function reload() {
		var cmd = wrkdir.replace("file://","")+'dockinfo.py';
		launchers.exec(cmd);

	}

	function accessWizard() {
		launchers.exec("/usr/share/accesswizard/accesswizard.py")
	}
	function configureDock() {
		launchers.exec("/usr/share/accesswizard/dock/accessdock-config.py")
	}

 }	
