/*
    This script is part of the Lliurex Project 
    SPDX-FileCopyrightText: 2024 juanma1980 <juanma1980@gmail.com>
    SPDX-License-Identifier: GPL-3.0
*/
import QtQuick 2.0
import QtQuick.Window 2.0

Window {
		id: frame
		flags:Qt.FrameLessHint|Qt.WindowStaysOnTopHint|Qt.WindowSystemMenuHint| Qt.X11BypassWindowManagerHint | Qt.FramelessWindowHint| Qt.WindowTransparentForInput| Qt.TransparentForMouseEvents|Qt.OnScreenDisplay
		property bool outputOnly:true
		property int borderWidth: 10
		color:Qt.rgba(0,0,0,0)
		visible: false
		Rectangle {
			id:rect
			anchors.fill:parent
			color:frame.color
			border.width: frame.borderWidth
			visible:true
		}

		function moveFrame(x,y,w,h){
		   frame.y=y;
		   frame.x=x;
		   frame.width=w;
		   frame.height=h;
		   console.log("MOVING");


		} // Window
    Component.onCompleted: {
        frame.show();
    }
}
