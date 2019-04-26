import os
from maya import cmds
from maya import OpenMayaUI as omui
from maya.app.general import mayaMixin

from .tangentEditor import tanEditorUI
from .keysEditFromBuffer import keysEditFromBufferUI
from .scaleKeysEditor import scaleKeysEditorUI
from .filterGraphEditor import filterGEUI
from .selectionCurveSorce import sorceButton
from .infinityCurveEditor import infinityEditorUI
reload(infinityEditorUI)
reload(sorceButton)
reload(tanEditorUI)
reload(scaleKeysEditorUI)
reload(keysEditFromBufferUI)
reload(filterGEUI)

try:
	# Check import PySide
	from PySide.QtCore import *
	from PySide.QtDeclarative import *
	from PySide.QtGui import *
	from PySide.QtHelp import *
	from PySide.QtMultimedia import *
	from PySide.QtNetwork import *
	from PySide.QtOpenGL import *
	from PySide.QtScript import *
	from PySide.QtScriptTools import *
	from PySide.QtSql import *
	from PySide.QtSvg import *
	from PySide.QtTest import *
	from PySide.QtUiTools import *
	from PySide.QtWebKit import *
	from PySide.QtXml import *
	from PySide.QtXmlPatterns import *
	from PySide.phonon import *
	from shiboken import wrapInstance
except ImportError:
	try:
		# Check import PySide2
		from PySide2.QtCore import *
		from PySide2.QtGui import *
		from PySide2.QtHelp import *
		from PySide2.QtMultimedia import *
		from PySide2.QtNetwork import *
		from PySide2.QtPrintSupport import *
		from PySide2.QtQml import *
		from PySide2.QtQuick import *
		from PySide2.QtQuickWidgets import *
		from PySide2.QtScript import *
		from PySide2.QtSql import *
		from PySide2.QtSvg import *
		from PySide2.QtTest import *
		from PySide2.QtUiTools import *
		from PySide2.QtWebChannel import *
		from PySide2.QtWebKit import *
		from PySide2.QtWebKitWidgets import *
		from PySide2.QtWebSockets import *
		from PySide2.QtWidgets import *
		from PySide2.QtXml import *
		from PySide2.QtXmlPatterns import *
		from shiboken2 import wrapInstance
	except ImportError:
		# Failed import to PySide and PySide2.
		raise ImportError('No module named PySide and PySide2.')
		
class AddToolWidget(QWidget):
	def __init__(self,parent,panelname,*args,**kwargs):
		super(AddToolWidget,self).__init__(parent)
		self.panelname = panelname
		self.setFixedHeight(150)
		self.initUI()
		
	def initUI(self):
		self.uiList = [	infinityEditorUI.infinityEditorWidget(self,self.panelname),
						filterGEUI.FilterWidget(self,self.panelname),
						sorceButton.sorceButtonWidget(self),
						tanEditorUI.EditorWidget(self),
						scaleKeysEditorUI.ScaleKeysEditorWidget(self),
						keysEditFromBufferUI.KeysEditFromBufferWidget(self,self.panelname)]
		self.uiList[1].setFixedSize(180,100)
		
		vlay_a = QVBoxLayout()
		vlay_a.addWidget(self.uiList[1])
		vlay_a.addWidget(self.uiList[2])

		vlay_b = QVBoxLayout()
		vlay_b.addWidget(self.uiList[4])
		vlay_b.addWidget(self.uiList[5])
		vlay_b.setSpacing(0)
		vlay_b.setContentsMargins(0, 0, 0, 0)
		
		hlay = QHBoxLayout()
		
		hlay.addWidget(self.uiList[0])
		hlay.addLayout(vlay_a)
		hlay.addWidget(self.uiList[3])
		hlay.addLayout(vlay_b)
		
		
		self.setLayout(hlay)
		
	def closeEvent(self, e):
		try:
			for ui in self.uiList:
				ui.close()
		except:
			pass
		
class GraphEditor(QWidget):
	def __init__(self,parent,panelname, *args, **kwargs):
		super(GraphEditor, self).__init__(parent)
		
		self.panelname = panelname
		self.paneName = "GE_ui_paneLayout"
		cmds.setParent('MayaWindow')
		
		if cmds.paneLayout(self.paneName,ex=True):###This paneLayout is required for findPanelPopupParent.mel###
			cmds.deleteUI(self.paneName)
		paneLayout = cmds.paneLayout(self.paneName, configuration = "single" )
			
		if cmds.scriptedPanel(self.panelname,ex=True):
			cmds.deleteUI(self.panelname)
		graphEditor = cmds.scriptedPanel(self.panelname,type='graphEditor',unParent=True)
		
		cmds.scriptedPanel(self.panelname,e=True,parent=paneLayout )
		ptr = omui.MQtUtil.findControl(paneLayout)
		widget = wrapInstance(long(ptr), QWidget)
		
		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(widget)
		
	def closeEvent(self, e):
		if cmds.paneLayout(self.paneName,ex=True):
			cmds.deleteUI(self.paneName)
		if cmds.scriptedPanel(self.panelname,ex=True):
			cmds.deleteUI(self.panelname)
		
class MainWindow(QMainWindow):
	settingFilename = "graphEditorWindow.ini"
	def __init__(self, *args, **kwargs):
		ptr = omui.MQtUtil.mainWindow()
		parent = wrapInstance(long(ptr),QWidget)
		super(MainWindow, self).__init__(parent)
		
		self.setWindowTitle("Custom Graph Editor")
		filename = os.path.join(os.path.dirname(__file__),"uisetting",self.settingFilename)
		self.__settings = QSettings(filename, QSettings.IniFormat)
		self.__settings.setIniCodec('utf-8')
		
		self.initUI()
	
	def initUI(self):
		panelname = "graphEditor1"
		widget = QWidget(self)
		vlay = QVBoxLayout(self)
		self.graphEditor = GraphEditor(self,panelname)
		self.addTools = AddToolWidget(self,panelname)
		
		vlay.addWidget(self.graphEditor)
		vlay.addWidget(self.addTools)
		vlay.setContentsMargins(0, 0, 0, 0)
		vlay.setSpacing(0)
		widget.setLayout(vlay)
		
		self.setCentralWidget(widget)
		
		
	def restore(self):
		self.restoreGeometry(self.__settings.value('geometry'))

	def show(self):
		self.restore()
		super(MainWindow, self).show()
	
	def closeEvent(self, e):
		global customGraphEditor
		try:
			self.addTools.close()
		except:
			pass
		try:
			self.graphEditor.close()
		except:
			pass
		self.__settings.setValue('geometry', self.saveGeometry())
		customGraphEditor = None
		super(self.__class__, self).closeEvent(e)
	
def main():
	global customGraphEditor
	try:
		customGraphEditor.close()
	except:
		pass
	customGraphEditor = MainWindow()
	customGraphEditor.show()