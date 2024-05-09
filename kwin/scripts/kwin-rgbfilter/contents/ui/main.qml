/*
    This script is part of the Lliurex Project 
    SPDX-FileCopyrightText: 2024 Juanma1980 <juanma1980@gmail.com>
    SPDX-License-Identifier: GPL-3.0
*/

import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
import org.kde.kwin 2.0 as KWinComponents

Item {
    id: root

    Loader {
        id: mainItemLoader
    }

    property color bkgColor: "black"
    property int filterOpacity: 15
    property color rColor: "black"
    property bool show: true

    function reloadFilter(show=true){
        mainItemLoader.sourceComponent=undefined;
        mainItemLoader.source="";
        root.show=show
    }
    
    function readConfig(){
        bkgColor= KWin.readConfig("BackgroundColor",Qt.rgba(0,0,1,0.1));
        filterOpacity= KWin.readConfig("Opacity",20);
        rColor=Qt.rgba(bkgColor.r,bkgColor.g,bkgColor.b,filterOpacity/100);
    }

    function showFilter(){
       var rgbFilter;
       if (!mainItemLoader.item) {
           readConfig();
           mainItemLoader.source = "filter.qml";
           rgbFilter=mainItemLoader.item;
           rgbFilter.color=root.rColor;
       }
    }

    KWinComponents.DBusCall {
        id: kwinReconfigure
        service: "org.kde.KWin"; path: "/KWin"; method: "reconfigure";
    }


 Connections {
        target: options
        function onConfigChanged() { readConfig(); }
    }

    Component.onCompleted: {
		showFilter();
        KWin.registerShortcut("Toggle RGB Filter", "Toggle RGB Filter", "Ctrl+Meta+R", function() {  reloadFilter(!show); }); 
    }
}
