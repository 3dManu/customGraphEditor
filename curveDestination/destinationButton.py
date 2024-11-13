#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

try:
    from shiboken2 import wrapInstance
except ImportError:
    from shiboken6 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI
from ..manuWidget import rightButtonWidget as rightButtonWidget

def getDestinationObj():
    curveName = cmds.keyframe(q=True,sl=True,name=True)
    obj = []
    if curveName:
        for cn in curveName:
            tmplist = get_connected_dest_nodes(cn,"transform",True,["message"],True)[0]
            if tmplist:
                obj.extend(tmplist)
        return list(set(obj))
    return None
    
def get_connected_dest_nodes(node, trgType,isFirst = True, extraAttrs = None, isException = True, passedNode = None):#Return is the First targets node
    result = []
    extraNode = []
    
    if extraAttrs is None:
        extraAttrs = []
    if passedNode is None:
        passedNode = []
        
    if extraAttrs:
        for extraAttr in extraAttrs:
            if cmds.objExists(node+"."+extraAttr):
                tempList = cmds.listConnections(node+"."+extraAttr,s=False,d=True)
                if tempList:
                    extraNode.extend(tempList)
        if isException: #Remove connection destination of specific attribute
            dest_list = cmds.listConnections(node,s=False,d=True)
            if dest_list:
                dest_list = list(set(dest_list) - set(extraNode))
        else:
            dest_list = extraNode
            
    else:
        dest_list = cmds.listConnections(node,s=False,d=True)
        
    if not dest_list:
        return None, False
    dest_list = list(set(dest_list))
    
    targets = []
    for dest in dest_list:
        if cmds.objectType(dest, isType = trgType):
            targets.append(dest)
        
    if targets:
        return targets, True
    elif dest_list:
        for dest in dest_list:
            if dest in passedNode:
                continue
            passedNode.append(dest)
            tmplist, isFind = get_connected_dest_nodes(dest,trgType,isFirst,extraAttrs,isException,passedNode)
            if isFirst and isFind:
                return tmplist, True
            if tmplist:
                result.extend(tmplist)
            else:
                continue
        return result, False
    else:
        return None, False
    
def selectObj():
    objNames = getDestinationObj()
    if objNames is not None:
        cmds.select(objNames,r=True)
def removeObj():
    objNames = getDestinationObj()
    if objNames is not None:
        cmds.select(objNames,d=True)
    
class destinationButtonUI(QMainWindow):
    def __init__(self,parent=None):
        super(destinationButtonUI,self).__init__(parent)
        self.setWindowFlags(Qt.Window|Qt.WindowCloseButtonHint)
        self.resize(40,120)
        
        self.widget = destinationButtonWidget(self, layoutType = False)
        self.setCentralWidget(self.widget)
        title = self.widget.windowTitle()
        self.setWindowTitle(title)
    
    def closeEvent(self, e):
        try:
            self.widget.close()
        except:
            pass
            
class destinationButtonWidget(QWidget):
    def __init__(self,parent=None, layoutType = True):
        super(destinationButtonWidget,self).__init__(parent)
        
        self.setWindowTitle("Get Destination Button")
        self.destinationButton = rightButtonWidget.RightClickButton(self)
        
        self.initUI(layoutType)
        
    def initUI(self, layoutType):
        vlay = QVBoxLayout(self)
        vlay.addWidget(self.destinationButton)
        vlay.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(vlay)
        
        if layoutType:
            self.destinationButton.setFixedWidth(54)
            self.destinationButton.setText("Dest Obj")
        else:
            self.destinationButton.setFixedHeight(54)
            self.destinationButton.setText("De")
        self.destinationButton.clicked.connect(selectObj)
        self.destinationButton.rightClicked.connect(removeObj)
        

            
def main():
    mayaWindow = 'graphEditor1Window' #常にこのウィンドウより前にいます
    ptr = OpenMayaUI.MQtUtil.findWindow(mayaWindow)
    if ptr is not None:
        parent = wrapInstance(int(ptr),QWidget)
    else:
        cmds.error('Please open the GraphEditor')
    app = QApplication.instance()
    ui = destinationButtonUI(parent)
    ui.show()
    sys.exit()
    app.exec_()

if __name__ == "__main__":
    main()
