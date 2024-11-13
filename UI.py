#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os,sys
from maya import cmds, mel
from maya import OpenMayaUI as omui
import json

from .tangentEditor import tanEditorUI
from .keysEditFromBuffer import keysEditFromBufferUI
from .scaleKeysEditor import scaleKeysEditorUI
from .filterGraphEditor import filterGEUI
from .curveDestination import destinationButton
from .infinityCurveEditor import infinityEditorUI
from .otherTools import otherButton

from .manuWidget import collapsibleLineWidget as collapsibleLineWidget
from .manuWidget import separatorWidget as separatorWidget

try:
    from PySide6 import QtCore,QtGui,QtWidgets
except ImportError:
    from PySide2 import QtCore,QtGui,QtWidgets
        
cmds.optionVar(iv=["customGraphEditorVis",0])
class AddToolWidget(QtWidgets.QWidget):
    def __init__(self,parent,panelname,rowColumn,*args,**kwargs):
        super(AddToolWidget,self).__init__(parent)
        self.panelname = panelname
        self.rowColumn = rowColumn
        self.settingDir = os.path.dirname(__file__)+"\settings"
        self.fileName = "uiSetting.json"
        self.initUI()
        
    def initUI(self):
        isRow = True
        if self.rowColumn == "row":
            isRow = True
        else:
            isRow = False
        self.uiList = [ infinityEditorUI.infinityEditorWidget(self,self.panelname,layoutType = isRow),
                        filterGEUI.FilterWidget(self,self.panelname,layoutType = isRow),
                        tanEditorUI.EditorWidget(self,layoutType = isRow),
                        scaleKeysEditorUI.ScaleKeysEditorWidget(self,layoutType = isRow),
                        destinationButton.destinationButtonWidget(self,layoutType = isRow),
                        otherButton.OtherButtonWidget(self,self.panelname,layoutType = isRow),
                        keysEditFromBufferUI.KeysEditFromBufferWidget(self,self.panelname,layoutType = isRow)]
        
        mainLay = QtWidgets.QHBoxLayout()
        if self.rowColumn == "row":
            self.setFixedHeight(64)
            subLay_a = QtWidgets.QVBoxLayout()
            align_a = QtCore.Qt.AlignTop
            align_b = QtCore.Qt.AlignBottom
            
        else:
            self.setFixedWidth(160)
            subLay_a = QtWidgets.QHBoxLayout()
            align_a = QtCore.Qt.AlignLeft
            align_b = QtCore.Qt.AlignRight
            
        subLay_a.addWidget(self.uiList[4],alignment = align_b)
        subLay_a.addWidget(self.uiList[5],alignment = align_a)
        
        self.collapsible_a = collapsibleLineWidget.CollapsibleLineWidget(self,isRow)
        self.collapsible_b = collapsibleLineWidget.CollapsibleLineWidget(self,isRow)
        self.collapsible_c = collapsibleLineWidget.CollapsibleLineWidget(self,isRow)
        self.collapsible_d = collapsibleLineWidget.CollapsibleLineWidget(self,isRow)
        self.collapsible_e = collapsibleLineWidget.CollapsibleLineWidget(self,isRow)
        self.collapsible_f = collapsibleLineWidget.CollapsibleLineWidget(self,isRow)
        
        self.collapsible_a.setObjectName("collapsible_a")
        self.collapsible_b.setObjectName("collapsible_b")
        self.collapsible_c.setObjectName("collapsible_c")
        self.collapsible_d.setObjectName("collapsible_d")
        self.collapsible_e.setObjectName("collapsible_e")
        self.collapsible_f.setObjectName("collapsible_f")
            
        subLay_a.setContentsMargins(0, 0, 0, 0)
        containWidget_a = QtWidgets.QWidget()
        containWidget_a.setLayout(subLay_a)
        
        self.collapsible_a.addWidget(self.uiList[0])
        self.collapsible_b.addWidget(self.uiList[1])
        self.collapsible_c.addWidget(self.uiList[2])
        self.collapsible_d.addWidget(self.uiList[3])
        self.collapsible_e.addWidget(containWidget_a)
        self.collapsible_f.addWidget(self.uiList[6])
        
        if self.rowColumn == "row":
            mainLay.addWidget(self.collapsible_a, alignment = (QtCore.Qt.AlignLeft))
            mainLay.addWidget(self.collapsible_b, alignment = (QtCore.Qt.AlignLeft))
            mainLay.addWidget(self.collapsible_c)
            mainLay.setAlignment(QtCore.Qt.AlignLeft)
            mainLay.addWidget(self.collapsible_d, alignment = (QtCore.Qt.AlignLeft))
            mainLay.addWidget(self.collapsible_e, alignment = (QtCore.Qt.AlignLeft))
            mainLay.addWidget(self.collapsible_f, alignment = (QtCore.Qt.AlignLeft))
        else:
            adjustLay_a = QtWidgets.QVBoxLayout()
            adjustLay_b = QtWidgets.QVBoxLayout()
            
            adjustLay_a.addWidget(self.collapsible_a, alignment = (QtCore.Qt.AlignTop))
            adjustLay_a.addWidget(self.collapsible_f, alignment = (QtCore.Qt.AlignTop))
            adjustLay_a.addWidget(self.collapsible_c)
            adjustLay_a.setAlignment(QtCore.Qt.AlignTop)
            
            adjustLay_b.addWidget(self.collapsible_b, alignment = (QtCore.Qt.AlignTop))
            adjustLay_b.addWidget(self.collapsible_d)
            adjustLay_b.addWidget(self.collapsible_e, alignment = (QtCore.Qt.AlignBottom))
            adjustLay_b.addStretch()
            mainLay.addLayout(adjustLay_b)
            mainLay.addWidget(separatorWidget.QVLine())
            mainLay.addLayout(adjustLay_a)
            mainLay.addStretch()
            
        
        mainLay.setSpacing(0)
        mainLay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLay)
        
        self.loadSettings()
            
        
    def closeEvent(self, event):
        self.saveSettings()
        try:
            for ui in self.uiList:
                ui.close()
        except:
            pass
            
    def loadSettings(self):
        if os.path.isfile(self.settingDir + "\\" + self.fileName):
            with open(self.settingDir + "\\" + self.fileName, "r") as f:
                settings = json.load(f)
            self.collapsible_a.setCollapsed(settings.get(self.collapsible_a.objectName()).get("isCollapsed"))
            self.collapsible_b.setCollapsed(settings.get(self.collapsible_b.objectName()).get("isCollapsed"))
            self.collapsible_c.setCollapsed(settings.get(self.collapsible_c.objectName()).get("isCollapsed"))
            self.collapsible_d.setCollapsed(settings.get(self.collapsible_d.objectName()).get("isCollapsed"))
    
    def saveSettings(self):
        settings = dict()
        settings[self.collapsible_a.objectName()] = {"isCollapsed" : self.collapsible_a.isCollapsed()}
        settings[self.collapsible_b.objectName()] = {"isCollapsed" : self.collapsible_b.isCollapsed()}
        settings[self.collapsible_c.objectName()] = {"isCollapsed" : self.collapsible_c.isCollapsed()}
        settings[self.collapsible_d.objectName()] = {"isCollapsed" : self.collapsible_d.isCollapsed()}
        if not os.path.exists(self.settingDir):
            os.makedirs(self.settingDir)
        with open(self.settingDir + "\\" + self.fileName,"w") as f:
            json.dump(settings, f, ensure_ascii=False)
        
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
            self.setFixedWidth(120)
        
        vlay.addWidget(self.addTools)
        vlay.setContentsMargins(0, 0, 0, 0)
        vlay.setSpacing(0)
        widget.setLayout(vlay)
        vlay.setObjectName("customGraphEditor_layout")
        
        self.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(widget)
    
    def closeEvent(self, event):
        try:
            self.addTools.close()
        except:
            pass
    
def createPaneLayout(parent = None,panelname=None, configuration = None,*args):
    paneName = panelname + "CustomPane"
    if cmds.paneLayout(paneName,exists =True):
        cmds.deleteUI(paneName)
    cmds.paneLayout(paneName,parent = parent)
    cmds.paneLayout(paneName,e = True,configuration = configuration)#仮
    return paneName

def createCustomWidgets(graphWindowName,panelname,rowColumn):
    global customGraphEditorWidget
    
    customGraphEditorWidget = DockMainWindow(panelname = panelname,rowColumn = rowColumn)
    customGraphEditorWidget.show()
    
    storedControl = omui.MQtUtil.findControl(customGraphEditorWidget.objectName())
    return storedControl
    
def createGraphEditorPanel(parent = None, panelname = None):
    if cmds.scriptedPanel(panelname, exists=True):
        cmds.deleteUI(panelname)
        if cmds.workspaceControl(panelname + "Window", exists = True):
            cmds.deleteUI(panelname + "Window")
    if cmds.scriptedPanel(panelname, exists=True):#なぜか2回削除を行わないとgraphEditor1が消えない
        cmds.deleteUI(panelname)
    return cmds.scriptedPanel(panelname,parent = parent,type="graphEditor", label = "Graph Editor")
    
def creatWorkspaceControl(graphWindowName, panelname):
    layout = cmds.optionVar(q = "customGraphEditorLayout")
    
    cmds.workspaceControl(graphWindowName,e=True,cc="from customGraphEditor import UI;UI.closeAddWindow()")
    
    rowColumn = "row"
    if layout in ["top","bottom","float"]:
        configuration = "horizontal2"
        rowColumn = "row"
    else:
        configuration = "vertical2"
        rowColumn = "column"
    
    paneName = createPaneLayout(graphWindowName, panelname ,configuration)
    geLayout = omui.MQtUtil.findLayout(paneName)
    
    storedControl = createCustomWidgets(graphWindowName, panelname, rowColumn)
    
    if layout in ["bottom","right"]:
        createGraphEditorPanel(paneName, panelname)
        omui.MQtUtil.addWidgetToMayaLayout(int(storedControl),int(geLayout))
    elif layout in ["top","left"]:
        omui.MQtUtil.addWidgetToMayaLayout(int(storedControl),int(geLayout))
        createGraphEditorPanel(paneName, panelname)
    else:
        omui.MQtUtil.addWidgetToMayaLayout(int(storedControl),int(geLayout))
    
    print ("PanelName  : %s"%(panelname))
    print ("WindowName : %s"%(graphWindowName))
    print ("Layout     : %s"%(layout))

def closeAddWindow(*args):
    global customGraphEditorWidget
    graphWindowName = "customGraphEditorWindow"
    panelname = "graphEditor1"
    layout = cmds.optionVar(q = "customGraphEditorLayout")
    if layout != "float":
        cmds.deleteUI(panelname)
    cmds.deleteUI(graphWindowName)
    customGraphEditorWidget.close()
    print ("##Closed Tools Widget##")
        
def main(layout = None):
    global customGraphEditorWidget
    graphWindowName = "customGraphEditorWindow"
    panelname = "graphEditor1"
    
    if layout is None:
        layout = cmds.optionVar(q = "customGraphEditorLayout")
    elif layout in ["top","bottom","left","right","float"]:
        cmds.optionVar(sv = ["customGraphEditorLayout",layout])
    else:
        layout = "bottom"
    
    if cmds.workspaceControl(graphWindowName,ex=True):
        print ("Restore Window")
        if 'customGraphEditorWidget' in globals():
            customGraphEditorWidget.close()
        creatWorkspaceControl(graphWindowName,panelname)
        cmds.workspaceControl(graphWindowName,e=True,restore=True)
        
    else:
        print ("New Window")
        if cmds.window(panelname+"Window",exists=True):
            cmds.deleteUI(panelname+"Window")
        update = cmds.workspaceControl(graphWindowName,label="Custom Graph Editor",retain=True,dup=False,uiScript = "from customGraphEditor import UI;UI.creatWorkspaceControl('%s','%s')"%(graphWindowName,panelname))
        cmds.workspaceControl(update,e=True,uiScript = "from customGraphEditor import UI;UI.creatWorkspaceControl('%s','%s')"%(graphWindowName,panelname))
