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

    Plasmoid.icon: "accesswizard"
    Plasmoid.toolTipMainText: "Accessibility Helper"
    Plasmoid.toolTipSubText: "Quick launcher for accessibility"

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
			if ((stdout.trim()!="") && (stdout[0]==="{")){
				console.log(stdout)
				stdout=stdout.replace(/\"/g,'###%%%')
				stdout=stdout.replace(/, \'/g,', "')
				stdout=stdout.replace(/\':/g,'":')
				stdout=stdout.replace(/{\'/g,'{"')
				stdout=stdout.replace(/###%%%/g,'')
				stdout=stdout.replace(/\'/g,'"')
				stdout=stdout.replace(/False/g,'\"False\"')
				stdout=stdout.replace(/True/g,'\"True\"')
				var jsonout={}
				try {
					jsonout=JSON.parse(stdout)
				} catch (e) {
					console.error("Err:" + e)
					return;
				}
				launchersModel.clear()
				var objkeys=Object.keys(jsonout)
				console.log(objkeys)
				objkeys.forEach(item=>{
					var objItem=jsonout[item]
					console.log(objItem["Name"])
					plasmoid.setAction(objItem["Exec"], i18n(objItem["Name"]),objItem["Name"])
					launchersModel.append({"name":objItem["Name"],"exec":objItem["Exec"],"icon":objItem["Icon"]})
					});
				launchersModel.append({"name":"Toggle dock","exec":"qdbus net.lliurex.accessibledock /net/lliurex/accessibledock net.lliurex.accessibledock.toggle","icon":"accesswizard"})
			}
			exited(exitCode, exitStatus, stdout, stderr)
			disconnectSource(sourceName) // cmd finished
		}

		function exec(cmd) {
			console.log("Exec: "+cmd)
			connectSource(cmd)
		}
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
            anchors.fill: parent
			ListView {
            	anchors.fill: parent
				model: launchersModel
				delegate: launcherDelegate
			}


		}
    }
	Component {
        id: launcherDelegate
        PlasmaComponents.Button {
			width: parent.width
           	text: model.name 
			icon.name:model.icon
			onClicked:{launchers.exec(model.exec)}
        }
    }
	Component.onCompleted: {
        plasmoid.removeAction("configure");
		var cmd = wrkdir.replace("file://","")+'dockinfo.py';
		launchers.exec(cmd);
	}

    function launchConfig() {
		console.log("l");
        //accessibiltyMenu.launch_llxup()
    }

 }	
