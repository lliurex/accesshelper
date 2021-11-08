#!/usr/bin/env python3
import sys
import os
from PySide2.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfigScreen as appConfig
app=QApplication(["AccessHelper"])
config=appConfig("AccesHelper",{'app':app})
config.setRsrcPath("/usr/share/accesshelper/rsrc")
config.setIcon('accesshelper')
#config.setWiki('https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Repoman+%28Bionic%29.')
#config.setBanner('repoman_banner.png')
#config.setBackgroundImage('repoman_login.svg')
#config.setConfig(confDirs={'system':'/usr/share/accesshelper','user':'%s/.config'%os.environ['HOME']},confFile="accesHelper.conf")
config.setConfig(confDirs={'system':'/usr/share/accesshelper','user':os.path.join(os.environ['HOME'],"git/accesshelp")},confFile="accesshelper.json")
config.Show()
#config.setFixedSize(config.width(),config.height())
config.setFixedSize(800,600)

app.exec_()
