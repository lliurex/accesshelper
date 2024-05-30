/*
    This script is part of the Lliurex Project 
    SPDX-FileCopyrightText: 2024 juanma1980 <juanma1980@gmail.com>
    SPDX-License-Identifier: GPL-3.0
*/
import QtQuick 2.0;
import QtQuick.Window 2.0;

Window {
    id: rgbfilter
	flags:Qt.FrameLessHint|Qt.WindowStaysOnTopHint|Qt.WindowSystemMenuHint| Qt.X11BypassWindowManagerHint | Qt.FramelessWindowHint| Qt.WindowTransparentForInput| Qt.TransparentForMouseEvents|Qt.OnScreenDisplay
    visible: false
    width: Screen.width
    height: Screen.height
	property bool outputOnly:true
	Rectangle {
		id:rect
		anchors.fill:parent
		color:rgbfilter.color
		visible:true
	}
    Component.onCompleted: {
        rgbfilter.show();
    }

}
