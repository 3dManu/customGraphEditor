#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys,os

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

from maya import cmds, mel
import maya.OpenMayaUI as OpenMayaUI
from ..manuWidget import rightButtonWidget

    
class OtherButtonUI(QMainWindow):
    def __init__(self,parent=None):
        super(OtherButtonUI,self).__init__(parent)
        self.setWindowFlags(Qt.Window|Qt.WindowCloseButtonHint)
        self.resize(40,120)
        
        self.widget = OtherButtonWidget(self, layoutType = False)
        self.setCentralWidget(self.widget)
        title = self.widget.windowTitle()
        self.setWindowTitle(title)
    
    def closeEvent(self, e):
        try:
            self.widget.close()
        except:
            pass
            
class OtherButtonWidget(QWidget):
    def __init__(self,parent=None,panelname = "graphEditor1", layoutType = True):
        super(OtherButtonWidget,self).__init__(parent)
        
        self.setWindowTitle("Other Tools")
        self.panelname = panelname
        self.initUI(layoutType)
        
    def initUI(self, layoutType):
        self.muteButton = rightButtonWidget.RightClickButton(self)
        self.FallOffButton = QPushButton(self)
        
        if layoutType: 
            mainLayout = QHBoxLayout(self)
        else:
            mainLayout = QVBoxLayout(self)
            
        mainLayout.setSpacing(6)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.muteButton)
        mainLayout.addWidget(self.FallOffButton)
        
        self.setLayout(mainLayout)
        
        self.muteButton.setFixedSize(24,24)
        self.muteButton.clicked.connect(self.doMuteChannel)
        self.muteButton.rightClicked.connect(self.doUnMuteChannel)
        
        self.FallOffButton.setFixedSize(24,24)
        self.FallOffButton.setCheckable(True)
        self.FallOffButton.toggled.connect(self.toggleMoveKeyFallOff)
        
        self.set_style_button()
        
        
    def set_style_button(self):
        icon_path = os.path.join(os.path.dirname(__file__), r'..\icons') 
        
        muteIcon = QIcon(icon_path + '\\customGraphEditor_mute_Icon.png')
        falloffIcon = QIcon(icon_path + '\\customGraphEditor_falloff_Icon.png')
        
        self.muteButton.setIcon(muteIcon)
        self.FallOffButton.setIcon(falloffIcon)
        
        self.muteButton.setFlat(True)
        self.FallOffButton.setFlat(True)
        
        self.muteButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.FallOffButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        
        iconSize = QSize(24,24)
        
        self.muteButton.setIconSize(iconSize)
        self.FallOffButton.setIconSize(iconSize)
        
    def doMuteChannel(self):
        if cmds.keyframe(q=True,sl=True,name=True):
            mel.eval("doMuteChannel %sFromOutliner -true;"%(self.panelname))
            
    def doUnMuteChannel(self):
        if cmds.keyframe(q=True,sl=True,name=True):
            mel.eval("doMuteChannel %sFromOutliner -false;"%(self.panelname))
            
    def toggleMoveKeyFallOff(self,chk):
        if chk:
            cmds.moveKeyCtx("moveKeyContext",e=True,moveFunction = "linear")
            self.FallOffButton.setStyleSheet("QPushButton:pressed{background-color: black;}")
        else:
            cmds.moveKeyCtx("moveKeyContext",e=True,moveFunction = "constant")
            self.FallOffButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")

            
def main():
    mayaWindow = 'graphEditor1Window' #常にこのウィンドウより前にいます
    ptr = OpenMayaUI.MQtUtil.findWindow(mayaWindow)
    if ptr is not None:
        parent = wrapInstance(int(ptr),QWidget)
    else:
        cmds.error('Please open the GraphEditor')
    app = QApplication.instance()
    ui = OtherButtonUI(parent)
    ui.show()
    sys.exit()
    app.exec_()

if __name__ == "__main__":
    main()
