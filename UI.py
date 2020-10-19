import os,sys
from maya import cmds, mel
from maya import OpenMayaUI as omui
from PySide2 import QtCore,QtGui,QtWidgets

from .tangentEditor import tanEditorUI
from .keysEditFromBuffer import keysEditFromBufferUI
from .scaleKeysEditor import scaleKeysEditorUI
from .filterGraphEditor import filterGEUI
from .selectionCurveSorce import sorceButton
from .infinityCurveEditor import infinityEditorUI
		
cmds.optionVar(iv=["customGraphEditorVis",0])
class AddToolWidget(QtWidgets.QWidget):
	def __init__(self,parent,panelname,rowColumn,*args,**kwargs):
		super(AddToolWidget,self).__init__(parent)
		self.panelname = panelname
		self.rowColumn = rowColumn
		self.initUI()
		
	def initUI(self):
		self.uiList = [	infinityEditorUI.infinityEditorWidget(self,self.panelname),
						filterGEUI.FilterWidget(self,self.panelname),
						sorceButton.sorceButtonWidget(self),
						tanEditorUI.EditorWidget(self),
						scaleKeysEditorUI.ScaleKeysEditorWidget(self),
						keysEditFromBufferUI.KeysEditFromBufferWidget(self,self.panelname)]
		self.uiList[1].setFixedSize(180,100)
		
		vlay_a = QtWidgets.QVBoxLayout()
		vlay_a.addWidget(self.uiList[1])
		vlay_a.addWidget(self.uiList[2])

		vlay_b = QtWidgets.QVBoxLayout()
		vlay_b.addWidget(self.uiList[4])
		vlay_b.addWidget(self.uiList[5])
		vlay_b.setSpacing(0)
		vlay_b.setContentsMargins(0, 0, 0, 0)
		
		if self.rowColumn == "row":
			self.setFixedHeight(150)
			mainLay = QtWidgets.QHBoxLayout()
			mainLay.addWidget(self.uiList[0])
			mainLay.addLayout(vlay_a)
			mainLay.addWidget(self.uiList[3])
			mainLay.addLayout(vlay_b)
		else:
			self.setFixedHeight(300)
			mainLay = QtWidgets.QVBoxLayout()
			hlay_a = QtWidgets.QHBoxLayout()
			hlay_a.addWidget(self.uiList[0])
			hlay_a.addLayout(vlay_a)
			hlay_a.addLayout(vlay_b)
			mainLay.addWidget(self.uiList[3])
			mainLay.addLayout(hlay_a)
		self.setLayout(mainLay)
			
		
	def closeEvent(self, event):
		try:
			for ui in self.uiList:
				ui.close()
		except:
			pass
		
class DockMainWindow(QtWidgets.QMainWindow):
	def __init__(self,parent = None, panelname = "graphEditor1",rowColumn="row", *args, **kwargs):
		super(DockMainWindow, self).__init__(parent=parent, *args, **kwargs)
		self.setWindowTitle("Custom Graph Editor")
		self.rowColumn = rowColumn
		
		self.panelname = panelname
		self.setObjectName("AddToolsDockWindow")
		
		self.initUI()
	
	def initUI(self):
		widget = QtWidgets.QWidget(self)
		vlay = QtWidgets.QVBoxLayout(self)
		self.addTools = AddToolWidget(self,self.panelname,self.rowColumn)
		if self.rowColumn == "row":
			self.setFixedHeight(self.addTools.maximumHeight())
		else:
			self.setMinimumHeight(self.addTools.maximumHeight())
			self.setFixedWidth(520)
		
		vlay.addWidget(self.addTools)
		vlay.setContentsMargins(0, 0, 0, 0)
		vlay.setSpacing(0)
		widget.setLayout(vlay)
		vlay.setObjectName("customGraphEditor_layout")
		
		self.setCentralWidget(widget)
	
	def closeEvent(self, event):
		try:
			self.addTools.close()
		except:
			pass
	
def changeRowColumn(parent = None,panelname=None,*args):
	paneName = panelname + "CustomPane"
	if cmds.paneLayout(paneName,exists =True):
		cmds.deleteUI(paneName)
	cmds.paneLayout(paneName,parent = parent)
	
	if cmds.optionVar(q = "customGraphEditorLayout") == "column":
		cmds.paneLayout(paneName,e = True,configuration = "vertical2")
	else:
		cmds.paneLayout(paneName,e = True,configuration = "horizontal2")
		
	if cmds.scriptedPanel(panelname, exists=True):
		cmds.deleteUI(panelname)
	cmds.scriptedPanel(panelname,parent = paneName,type="graphEditor")
	return paneName

def changeLayot(graphWindowName,panelname):
	global customGraphEditorWindow
	customGraphEditorWindow.close()
	
	if cmds.optionVar(q = "customGraphEditorLayout") == "column":
		cmds.optionVar(sv = ["customGraphEditorLayout","row"])
	else:
		cmds.optionVar(sv = ["customGraphEditorLayout","column"])
	addWidgetToMayaWindow(graphWindowName,panelname)
	
	
def addWidgetToMayaWindow(graphWindowName,panelname):
	global customGraphEditorWindow
	parentLayout = changeRowColumn(parent=graphWindowName,panelname = panelname)
	rowColumn = cmds.optionVar(q = "customGraphEditorLayout")
	
	customGraphEditorWindow = DockMainWindow(panelname = panelname,rowColumn = rowColumn)
	cmds.workspaceControl(graphWindowName,e=True,cc="from customGraphEditor import UI;UI.closeAddWindow()")
	customGraphEditorWindow.show()
	
	print "PanelName  : %s"%(panelname)
	print "WindowName : %s"%(graphWindowName)
	print "Layout     : %s"%(rowColumn)
	
	geLayout = omui.MQtUtil.findLayout(parentLayout)
	storedControl = omui.MQtUtil.findControl(customGraphEditorWindow.objectName())
	omui.MQtUtil.addWidgetToMayaLayout(long(storedControl),long(geLayout))

def closeAddWindow(*args):
	global customGraphEditorWindow
	graphWindowName = "customGraphEditorWindow"
	panelname = "graphEditor1"
	cmds.deleteUI(panelname)
	cmds.deleteUI(graphWindowName)
	customGraphEditorWindow.close()
	print "##Closed Tools Widget##"
		
def main():
	graphWindowName = "customGraphEditorWindow"
	panelname = "graphEditor1"
	
	if cmds.workspaceControl(graphWindowName,ex=True):
		print "Restore Window"
		if cmds.workspaceControl(graphWindowName,q=True,r=True):
			changeLayot(graphWindowName,panelname)
		cmds.workspaceControl(graphWindowName,e=True,restore=True)
		
	else:
		print "New Window"
		if cmds.window(panelname+"Window",exists=True):
			cmds.deleteUI(panelname+"Window")
		cmds.workspaceControl(graphWindowName,label="Custom Graph Editor",retain=True,dup=False,uiScript = "from customGraphEditor import UI;UI.addWidgetToMayaWindow('%s','%s')"%(graphWindowName,panelname))
		
