#!/usr/bin/python3
from . import libaccesshelper
from . import libhotkeys
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
	"CONFIG":_("Configuration"),
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
		self.refresh=True
		grpOptions=QGroupBox()
		layOption=QGridLayout()
		opt=QRadioButton(i18n.get("TYPEAPP"))
		opt.toggled.connect(lambda: self.updateScreen(opt))
		self.widgets.update({opt:"TYPEAPP"})
		layOption.addWidget(opt,0,0)
		opt1=QRadioButton(i18n.get("TYPECMD"))
		opt1.toggled.connect(lambda: self.updateScreen(opt1))
		#self.widgets.update({opt1:"TYPECMD"})
		#layOption.addWidget(opt1,0,1)
		opt2=QRadioButton(i18n.get("TYPEACT"))
		opt2.toggled.connect(lambda: self.updateScreen(opt2))
		#self.widgets.update({opt2:"TYPEACT"})
		#layOption.addWidget(opt2,0,1)
		grpOptions.setLayout(layOption)
		#self.box.addWidget(grpOptions,0,0,1,3)
		self.btnHk=libhotkeys.QHotkeyButton(i18n.get("BTNTXT"))
		self.btnHk.hotkeyAssigned.connect(self._testHotkey)
		self.box.addWidget(self.btnHk,1,0,3,1)
		self.inpSearch=QLineEdit()
		self.inpSearch.setPlaceholderText(_("Search"))
		self.inpSearch.textChanged.connect(self._searchList)
		self.box.addWidget(self.inpSearch,1,1,1,2)
		self.lstOptions=QListWidget()
		self.box.addWidget(self.lstOptions,2,1,1,2)
		self.lblCmd=QLabel(i18n.get("LBLCMD"))
		#self.box.addWidget(self.lblCmd,3,1,1,1)
		self.inpCmd=QLineEdit()
		self.inpCmd.setEnabled(False)
		self.lblCmd.setEnabled(False)
		#self.box.addWidget(self.inpCmd,3,2,1,1)
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
		self.btn_cancel.setText(i18n.get("CANCEL","Cancel"))
		self.btn_cancel.clicked.connect(self._exit)
		self.btn_cancel.setEnabled(True)
		#self.updateScreen()
	#def _load_screen

	def _searchList(self,*args):
		items=self.lstOptions.findItems(self.inpSearch.text(),Qt.MatchFlag.MatchContains)
		if items:
			self.lstOptions.scrollToItem(items[0])
			self.lstOptions.setCurrentItem(items[0])

	def _addHotkey(self,*args):
		pass

	def updateScreen(self,*args):
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
						self._loadActs()
		self.btn_cancel.setEnabled(True)
	#def _udpate_screen

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

	def _loadActs(self,*args):
		pass
	#def _loadActs

	def _updateConfig(self,name):
		pass

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
		f=open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
		self.stack.gotoStack(idx=4,parms="")

	def _exit(self):
		self.changes=False
		self.optionChanged=[]
		self.stack.gotoStack(idx=4,parms="")
