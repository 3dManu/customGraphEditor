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
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI

from . import resource

def get_state_infinity(graphEd):
    infinityState = cmds.animCurveEditor(graphEd,q=True,di=True)
    return infinityState
    
def set_state_infinity(graphEd,state):
    if state == 2:
        state = 1
    cmds.animCurveEditor(graphEd,e=True,di=state)
    
class infinityEditorUI(QMainWindow):
    def __init__(self,parent=None):
        super(infinityEditorUI,self).__init__(parent)
        self.setWindowFlags(Qt.Window|Qt.WindowCloseButtonHint)
        
        self.widget = infinityEditorWidget(self,layoutType = False)
        self.setCentralWidget(self.widget)
        title = self.widget.windowTitle()
        self.setWindowTitle(title)
    
    def closeEvent(self, e):
        try:
            self.widget.close()
        except:
            pass
            
class infinityEditorWidget(QWidget):
    def __init__(self,parent=None,panelname = "graphEditor1", layoutType = True):
        super(infinityEditorWidget,self).__init__(parent)
        
        self.setWindowTitle("Edit Infinity Curve")
        self.panelname = panelname
        self.setBaseSize(60,130)
        
        self.initUI(layoutType)
        
    def initUI(self,layoutType):
        self.priCycButton = QPushButton(self)
        self.priCyOButton = QPushButton(self)
        self.priOscButton = QPushButton(self)
        self.priLinButton = QPushButton(self)
        self.priConButton = QPushButton(self)
        
        self.poiCycButton = QPushButton(self)
        self.poiCyOButton = QPushButton(self)
        self.poiOscButton = QPushButton(self)
        self.poiLinButton = QPushButton(self)
        self.poiConButton = QPushButton(self)
        
        self.set_style_button()
        
        self.infinityCheckBox = QCheckBox(self)
        self.infLabel = QLabel('inf:',self)
        self.infinityCheckBox.setFixedWidth(24)
        self.infLabel.setFixedWidth(24)
        
        if layoutType:
            mainLayout = QVBoxLayout(self)
            priLayout = QHBoxLayout(self)
            poiLayout = QHBoxLayout(self)
            priLayout.addWidget(self.infLabel,alignment = (Qt.AlignRight | Qt.AlignBottom))
            poiLayout.addWidget(self.infinityCheckBox,alignment = (Qt.AlignRight | Qt.AlignTop))
        else:
            mainLayout = QHBoxLayout(self)
            priLayout = QVBoxLayout(self)
            poiLayout = QVBoxLayout(self)
            priLayout.addWidget(self.infLabel,alignment = (Qt.AlignRight | Qt.AlignVCenter))
            poiLayout.addWidget(self.infinityCheckBox,alignment = (Qt.AlignRight | Qt.AlignVCenter))
        
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        
        priLayout.addWidget(self.priCycButton)
        priLayout.addWidget(self.priCyOButton)
        priLayout.addWidget(self.priOscButton)
        priLayout.addWidget(self.priLinButton)
        priLayout.addWidget(self.priConButton)
        priLayout.setSpacing(4)
        priLayout.setContentsMargins(0, 0, 0, 0)
        
        poiLayout.addWidget(self.poiCycButton)
        poiLayout.addWidget(self.poiCyOButton)
        poiLayout.addWidget(self.poiOscButton)
        poiLayout.addWidget(self.poiLinButton)
        poiLayout.addWidget(self.poiConButton)
        poiLayout.setSpacing(4)
        poiLayout.setContentsMargins(0, 0, 0, 0)
        
        
        mainLayout.addLayout(priLayout)
        mainLayout.addLayout(poiLayout)
        
        self.setLayout(mainLayout)
        
        self.priCycButton.clicked.connect(self.infinityBtn_click_callBack)
        self.priCyOButton.clicked.connect(self.infinityBtn_click_callBack)
        self.priOscButton.clicked.connect(self.infinityBtn_click_callBack)
        self.priLinButton.clicked.connect(self.infinityBtn_click_callBack)
        self.priConButton.clicked.connect(self.infinityBtn_click_callBack)
        
        self.poiCycButton.clicked.connect(self.infinityBtn_click_callBack)
        self.poiCyOButton.clicked.connect(self.infinityBtn_click_callBack)
        self.poiOscButton.clicked.connect(self.infinityBtn_click_callBack)
        self.poiLinButton.clicked.connect(self.infinityBtn_click_callBack)
        self.poiConButton.clicked.connect(self.infinityBtn_click_callBack)
        
        self.infinityCheckBox.stateChanged.connect(self.infinityCheckBox_changed_callBack)
        
    def set_style_button(self):
        self.priCycButton.setFlat(True)
        self.priCycButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}");
        self.priCyOButton.setFlat(True)
        self.priCyOButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}");
        self.priOscButton.setFlat(True)
        self.priOscButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}");
        self.priLinButton.setFlat(True)
        self.priLinButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}");
        self.priConButton.setFlat(True)
        self.priConButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}");
        
        self.poiCycButton.setFlat(True)
        self.poiCycButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}");
        self.poiCyOButton.setFlat(True)
        self.poiCyOButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}");
        self.poiOscButton.setFlat(True)
        self.poiOscButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}");
        self.poiLinButton.setFlat(True)
        self.poiLinButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}");
        self.poiConButton.setFlat(True)
        self.poiConButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}");
        
        
        priCycIcon = QIcon(':/preInfinityCycle.png')
        priCyOIcon = QIcon(':/preInfinityCycleOffset.png')
        priOscIcon = QIcon(':/customGraphEditor/icon/preOscillateCycle.png')
        priLinIcon = QIcon(':/customGraphEditor/icon/preLinearCycle.png')
        priConIcon = QIcon(':/customGraphEditor/icon/preConstantCycle.png')
        poiCycIcon = QIcon(':/postInfinityCycle.png')
        poiCyOIcon = QIcon(':/postInfinityCycleOffset.png')
        poiOscIcon = QIcon(':/customGraphEditor/icon/postOscillateCycle.png')
        poiLinIcon = QIcon(':/customGraphEditor/icon/postLinearCycle.png')
        poiConIcon = QIcon(':/customGraphEditor/icon/postConstantCycle.png')
        
        self.priCycButton.setIcon(priCycIcon)
        self.priCyOButton.setIcon(priCyOIcon)
        self.priOscButton.setIcon(priOscIcon)
        self.priLinButton.setIcon(priLinIcon)
        self.priConButton.setIcon(priConIcon)
        
        self.poiCycButton.setIcon(poiCycIcon)
        self.poiCyOButton.setIcon(poiCyOIcon)
        self.poiOscButton.setIcon(poiOscIcon)
        self.poiLinButton.setIcon(poiLinIcon)
        self.poiConButton.setIcon(poiConIcon)
        
        iconSize = QSize(20,20)
        
        self.priCycButton.setIconSize(iconSize)
        self.priCyOButton.setIconSize(iconSize)
        self.priOscButton.setIconSize(iconSize)
        self.priLinButton.setIconSize(iconSize)
        self.priConButton.setIconSize(iconSize)
        
        self.poiCycButton.setIconSize(iconSize)
        self.poiCyOButton.setIconSize(iconSize)
        self.poiOscButton.setIconSize(iconSize)
        self.poiLinButton.setIconSize(iconSize)
        self.poiConButton.setIconSize(iconSize)
        
        
        btnHSize = 22
        btnWSize = 22
        self.priCycButton.setFixedSize(btnHSize,btnWSize)
        self.priCyOButton.setFixedSize(btnHSize,btnWSize)
        self.priOscButton.setFixedSize(btnHSize,btnWSize)
        self.priLinButton.setFixedSize(btnHSize,btnWSize)
        self.priConButton.setFixedSize(btnHSize,btnWSize)
        
        self.poiCycButton.setFixedSize(btnHSize,btnWSize)
        self.poiCyOButton.setFixedSize(btnHSize,btnWSize)
        self.poiOscButton.setFixedSize(btnHSize,btnWSize)
        self.poiLinButton.setFixedSize(btnHSize,btnWSize)
        self.poiConButton.setFixedSize(btnHSize,btnWSize)
        
    def infinityBtn_click_callBack(self):
        sender = self.sender()
        if sender == self.priCycButton:
            cmdOption = '"-pri cycle" '
        elif sender == self.priCyOButton:
            cmdOption = '"-pri cycleRelative" '
        elif sender == self.priOscButton:
            cmdOption = '"-pri oscillate" '
        elif sender == self.priLinButton:
            cmdOption = '"-pri linear" '
        elif sender == self.priConButton:
            cmdOption = '"-pri constant" '
        elif sender == self.poiCycButton:
            cmdOption = '"-poi cycle" '
        elif sender == self.poiCyOButton:
            cmdOption = '"-poi cycleRelative" '
        elif sender == self.poiOscButton:
            cmdOption = '"-poi oscillate" '
        elif sender == self.poiLinButton:
            cmdOption = '"-poi linear" '
        elif sender == self.poiConButton:
            cmdOption = '"-poi constant" '
        
        option = ' "bufferCurve useSmoothness usePin"'    
        cmd = 'doSetInfinity ' + cmdOption + self.panelname + "GraphEd" + option
        try:
            mel.eval(cmd)
        except:
            pass
            
    def infinityCheckBox_changed_callBack(self,value):
        set_state_infinity((self.panelname+"GraphEd"),value)
            
def main():
    mayaWindow = 'graphEditor1Window' #常にこのウィンドウより前にいます
    ptr = OpenMayaUI.MQtUtil.findWindow(mayaWindow)
    if ptr is not None:
        parent = wrapInstance(long(ptr),QWidget)
    else:
        cmds.error('Please open the GraphEditor')
    app = QApplication.instance()
    ui = infinityEditorUI(parent)
    ui.show()
    sys.exit()
    app.exec_()

if __name__ == "__main__":
    main()