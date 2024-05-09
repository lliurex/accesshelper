/*
    This script is part of the Lliurex Project 
    SPDX-FileCopyrightText: 2024 juanma1980 <juanma1980@gmail.com>
    SPDX-License-Identifier: GPL-3.0
*/
import QtQuick 2.0;
import QtQuick.Window 2.0;
import org.kde.plasma.core 2.0 as PlasmaCore;
import org.kde.kwin 2.0;

PlasmaCore.Dialog {
    id: rgbfilter
    location: PlasmaCore.Types.Floating
    visible: true
    flags: Qt.BypassWindowManagerHint | Qt.FramelessWindowHint | Qt.WindowTransparentForInput
    width: Screen.width
    height: Screen.height
    outputOnly: true
    Component.onCompleted: {
        rgbfilter.show();
        KWin.registerWindow(rgbfilter);
    }

}
