#!/usr/bin/python3
from . import libaccesshelper
from appconfig import appconfigControls
import os
from PySide2.QtWidgets import QLabel, QPushButton,QGridLayout,QLineEdit,QRadioButton,QListWidget,QGroupBox,QCompleter,QListWidgetItem
from PySide2 import QtGui
from PySide2.QtCore import Qt
from app2menu import App2Menu
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext
QString=type("")

i18n={
	"HOTKEYS":_("Keyboard Shortcuts"),
	"ACCESSIBILITY":_("hotkeys options"),
	"CONFIG":_("Hotkeys"),
	"DESCRIPTION":_("Add hotkey"),
	"MENUDESCRIPTION":_("Add a hotkey for an application, command or action"),
	"TOOLTIP":_("Assign actions to keys"),
	"TYPEAPP":_("Application from system"),
	"TYPECMD":_("Command-line order"),
	"TYPEACT":_("Desktop action"),
	"LBLCMD":_("Command"),
	"BTNTXT":_("Assign"),
	"PRESSKEY":_("Press a key or key-combination for the shortcut"),
	"HKASSIGNED":_("already assigned to action")
	}

class addHotkey(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("addhotkeys load")
		self.menu=App2Menu.app2menu()
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('input-keyboard')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=19
		self.visible=False
		self.enabled=True
		self.changed=[]
#		self.level='user'
		self.plasmaConfig={}
		self.wrkFiles=["kglobalshortcutsrc"]
		self.optionChanged=[]
		self.accesshelper=libaccesshelper.accesshelper()
	#def __init__

	def _load_screen(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.widgets={}
		self.widgetsText={}
		grpOptions=QGroupBox()
		layOption=QGridLayout()
		opt=QRadioButton(i18n.get("TYPEAPP"))
		self.widgets.update({opt:"TYPEAPP"})
		layOption.addWidget(opt,0,0)
		opt1=QRadioButton(i18n.get("TYPECMD"))
		opt2=QRadioButton(i18n.get("TYPEACT"))
		grpOptions.setLayout(layOption)
		self.btnHk=appconfigControls.QHotkeyButton(i18n.get("BTNTXT"))
		self.btnHk.hotkeyAssigned.connect(self._testHotkey)
		self.box.addWidget(self.btnHk,1,0,3,1)
		self.inpSearch=QLineEdit()
		self.inpSearch.setPlaceholderText(_("Search"))
		self.inpSearch.textChanged.connect(self._searchList)
		self.box.addWidget(self.inpSearch,1,1,1,2)
		self.lstOptions=QListWidget()
		self.box.addWidget(self.lstOptions,2,1,1,2)
		self.lblCmd=QLabel(i18n.get("LBLCMD"))
		self.inpCmd=QLineEdit()
		self.inpCmd.setEnabled(False)
		self.lblCmd.setEnabled(False)
		opt.setChecked(True)
		self.lblPress=QLabel(i18n.get("PRESSKEY"))
		self.lblPress.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		css="""QLabel{background:white;color: black;border:1px solid red}"""
		self.lblPress.setStyleSheet(css)
		font=self.lblPress.font()
		font.setBold(True)
		self.lblPress.setFont(font)
		self.lblPress.setVisible(False)
		self.box.addWidget(self.lblPress,0,0,2,3)
		self.btn_cancel.clicked.connect(self._exit)
		self.btn_cancel.setEnabled(True)
		opt.toggled.connect(lambda: self.updateScreen(opt))
		opt1.toggled.connect(lambda: self.updateScreen(opt1))
		opt2.toggled.connect(lambda: self.updateScreen(opt2))
	#def _load_screen

	def _searchList(self,*args):
		items=self.lstOptions.findItems(self.inpSearch.text(),Qt.MatchFlag.MatchContains)
		if items:
			self.lstOptions.scrollToItem(items[0])
			self.lstOptions.setCurrentItem(items[0])
	#def _searchList

	def updateScreen(self,*args):
		self.btnHk.setText(i18n.get("BTNTXT"))
		if args:
			if isinstance(args[0],QRadioButton):
				if args[0].isChecked():
					desc=self.widgets.get(args[0])
					self.lstOptions.clear()
					if desc=="TYPEAPP":
						self.inpCmd.setEnabled(False)
						self.lblCmd.setEnabled(False)
						self._loadApps()
					elif desc=="TYPECMD":
						self.inpCmd.setEnabled(True)
						self.lblCmd.setEnabled(True)
					elif desc=="TYPEACT":
						self.inpCmd.setEnabled(False)
						self.lblCmd.setEnabled(False)
	#def _udpate_screen

	def setParms(self,*args):
		self.force_change=True
		if self.lstOptions.count()<=0:
			self.lstOptions.clear()
			self._loadApps()
		self.setChanged(False)
	#def setParms

	def _loadApps(self,*args):
		completer=QCompleter()
		completer.setCaseSensitivity(Qt.CaseInsensitive)
		model=QtGui.QStandardItemModel()
		#Load available desktops
		categories=self.menu.get_categories()
		categories.append("network")
		desktops={}
		self.desktopDict={}
		for category in categories:
			desktops=self.menu.get_apps_from_category(category)
			for desktop in desktops.keys():
				desktopInfo=self.menu.get_desktop_info(os.path.join(self.menu.desktoppath,desktop))
				if desktopInfo.get("NoDisplay",False):
					continue
				listWidget=QListWidgetItem()
				desktopLayout=QGridLayout()
				ficon=desktopInfo.get("Icon","shell")
				icon=QtGui.QIcon.fromTheme(ficon)
				#if not icon:
				#	continue
				name=desktopInfo.get("Name","shell")
				model.appendRow(QtGui.QStandardItem(name))
				comment=desktopInfo.get("Comment","shell")
				listWidget.setIcon(icon)
				listWidget.setText(name)
				if name not in self.desktopDict.keys():
					self.lstOptions.addItem(listWidget)
				self.desktopDict[name]={'icon':icon,'desktop':desktop}
		self.lstOptions.sortItems()
	#def _loadApps

	def _testHotkey(self,hotkey):
		if not hotkey.get("action","")=="":
			try:
				self.showMsg("{0} {1} {2}".format(hotkey.get("hotkey"),i18n.get("HKASSIGNED"),hotkey.get("action")))
			except:
				pass
			self.btnHk.revertHotkey()
		self.btn_ok.setEnabled(True)
		self.btn_cancel.setEnabled(True)
	#def _testHotkey

	def writeConfig(self):
		#functionHelper.setPlasmaConfig(self.plasmaConfig)
		self.refresh=True
		txt=self.btnHk.text()
		config=self.getConfig(self.level).get(self.level,{})
		hotkeys=config.get('hotkeys',{})
		name=self.lstOptions.currentItem().text()
		desktop=self.desktopDict.get(name,{}).get('desktop','')
		if desktop:
			desktopInfo=self.menu.get_desktop_info(os.path.join("/usr/share/applications/",desktop))
			comment=desktopInfo.get("Comment",desktop)
		launch='{0},,{1}'.format(txt,comment)
		hk={'[{0}]'.format(desktop):{'_k_friendly_name':name,'_launch':launch}}
		hotkeys.update(hk)
		self.accesshelper.setKdeConfigSetting(desktop,"_k_friendly_name",name,self.wrkFiles[0])
		self.accesshelper.setKdeConfigSetting(desktop,"_launch",launch,self.wrkFiles[0])
		self.saveChanges("hotkeys",hotkeys)
		self.optionChanged=[]
		self._writeFileChanges(hotkeys)
		self._exit()
	#def writeConfig

	def _exit(self):
		self.changes=False
		self.optionChanged=[]
		self.stack.gotoStack(idx=4,parms="1")
	#def _exit

	def _writeFileChanges(self,hotkeys):
		#hotkeys=self.config.get('hotkeys',{})
		with open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'a') as f:
			f.write("<b>{}</b>\n".format(i18n.get("CONFIG")))
			for kfile,sections in self.plasmaConfig.items():
				for section,settings in sections.items():
					for setting in settings:
						arrayDesc=setting[1].split(",")
						f.write("{0}->{1}\n".format(arrayDesc[-1],setting[1]))
			for key,launchable in hotkeys.items():
				hotkey=launchable['_launch'].split(",")
				f.write("{0}->{1}\n".format(launchable['_k_friendly_name'],hotkey[0]))

	#def _writeFileChanges(self):
