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
    
from ..manuWidget import rightButtonWidget as rightButtonWidget
from ..manuWidget import doubleSpinBoxWidget as doubleSpinBoxWidget

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI

def get_state_bufferCurve(graphEd):
    showBufferCurvesState = cmds.animCurveEditor(graphEd,q=True,showBufferCurves=True)
    return showBufferCurvesState
    
def set_state_bufferCurve(graphEd,state):
    if state == 2:
        state = 1
    cmds.animCurveEditor(graphEd,e=True,showBufferCurves=state)
    
def converge_buffer(option,value = 1.1):
    keyCount = cmds.keyframe(q = True, kc = True, sl = True)
    if keyCount == 0:
        return
        
    cmds.undoInfo(openChunk=True,chunkName = "converge_buffer")
        
    if option == "toward":
        scaleValue = 1/value
    elif option == "away":
        scaleValue = value
    else:
        cmds.undoInfo(closeChunk=True,chunkName = "converge_buffer")
        return
    selectedCurves = cmds.keyframe(q = True, n = True, sl = True)
    for crv in selectedCurves:
        timeArray = cmds.keyframe(crv, q = True, tc = True, sl = True)
        cmds.bufferCurve(swap = True)
        burrferValues = []
        for t in timeArray:
            burrferValues.append(cmds.keyframe(crv, time = (t,t), q = True, eval = True)[0])
        cmds.bufferCurve(swap = True)
        
        selectedValues = cmds.keyframe(crv, q = True, iv = True, sl = True)
        for i,slv in enumerate(selectedValues):
            cmds.scaleKey(crv, index = (slv,slv), vp = burrferValues[i], vs = scaleValue)
            
    cmds.undoInfo(closeChunk=True,chunkName = "converge_buffer")
    
class WheelButton(rightButtonWidget.RightClickButton):
    scrollWheel = Signal()
    def __init__(self,parent=None):
        super(WheelButton,self).__init__(parent)
        self.y = 0
        self.chunkChk = False
    
    def wheelEvent(self, e):
        if not self.chunkChk:
            cmds.undoInfo(openChunk=True,chunkName = 'wheelEvent')
            self.chunkChk = True
        self.y = float(e.angleDelta().y()/120)
        self.scrollWheel.emit()
        
    def closed_chunk(self):
        if self.chunkChk:
            cmds.undoInfo(closeChunk=True,chunkName = 'wheelEvent')
            self.chunkChk = False
        
    def leaveEvent(self, e):
        self.closed_chunk()
    
    
    def keyPressEvent(self, e):
        if e.type() == QEvent.KeyPress:
            key = e.key()
            mod = e.modifiers()
            if key == Qt.Key_Z and mod == Qt.ShiftModifier:
                self.closed_chunk()
                cmds.redo()
            elif key == Qt.Key_Z:
                self.closed_chunk()
                cmds.undo()
            else:
                return False
            return True
    
class KeysEditFromBufferUI(QMainWindow):
    def __init__(self,parent=None):
        super(KeysEditFromBufferUI,self).__init__(parent)
        self.setWindowFlags(Qt.Window|Qt.WindowCloseButtonHint)
            
        
        self.widget = KeysEditFromBufferWidget(self, layoutType = False )
        self.setCentralWidget(self.widget)
        title = self.widget.windowTitle()
        self.setWindowTitle(title)
    
    def closeEvent(self, e):
        try:
            self.widget.close()
        except:
            pass
            
class KeysEditFromBufferWidget(QWidget):
    def __init__(self,parent=None,panelname = "graphEditor1", layoutType = True):
        super(KeysEditFromBufferWidget,self).__init__(parent)
        
        self.setBaseSize(60,200)
        self.setWindowTitle("Keys Edit from Buffer")
        self.panelname = panelname
        
        self.initUI(layoutType)
        
    def initUI(self, layoutType):
        self.snapButton = QPushButton(self)
        self.swapButton = QPushButton(self)
        self.bufferButton = WheelButton(self)
        
        self.mdButton = QPushButton("^-1",self)
        self.spinBox = doubleSpinBoxWidget.DoubleSpinBox(self)
        self.spinBox.setRange(0.01,10)
        self.spinBox.setDecimals(2)
        self.spinBox.setSingleStep(0.05)
        self.spinBox.setValue(1.1)
        self.mdButton.setFixedSize(24,24)
        
        self.set_style_button()
        
        self.bufferCurveCheckBox = QCheckBox(self)
        self.label = QLabel('BC:')
        
        if layoutType:
            mainLayout = QVBoxLayout(self)
            subLayout_a = QHBoxLayout(self)
            subLayout_b = QHBoxLayout(self)
            self.spinBox.setFixedWidth(48)
        else:
            mainLayout = QHBoxLayout(self)
            subLayout_a = QVBoxLayout(self)
            subLayout_b = QVBoxLayout(self)
            self.spinBox.editArrows()
        
        
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        
        
        subLayout_a.setContentsMargins(0, 0, 0, 0)
        subLayout_a.setSpacing(4)
        
        subLayout_a.addWidget(self.label,alignment=(Qt.AlignHCenter))
        subLayout_a.addWidget(self.bufferCurveCheckBox,alignment=(Qt.AlignHCenter))
        subLayout_a.addWidget(self.snapButton,alignment=(Qt.AlignHCenter))
        subLayout_a.addWidget(self.swapButton,alignment=(Qt.AlignHCenter))
        
        
        subLayout_b.setContentsMargins(0, 0, 0, 0)
        subLayout_b.setSpacing(0)
        subLayout_b.addWidget(self.mdButton, alignment=(Qt.AlignHCenter))
        subLayout_b.addWidget(self.spinBox, alignment=(Qt.AlignHCenter))
        subLayout_b.addSpacing(4)
        subLayout_b.addWidget(self.bufferButton, alignment=(Qt.AlignHCenter))
        
        
        mainLayout.addLayout(subLayout_a)
        mainLayout.setAlignment(subLayout_b, Qt.AlignRight)
        mainLayout.addLayout(subLayout_b)
        self.setLayout(mainLayout)
        
        
        self.snapButton.clicked.connect(self.snap_swap_cliced_callBack)
        self.swapButton.clicked.connect(self.snap_swap_cliced_callBack)
        
        self.mdButton.clicked.connect(self.inverseRatio)
        
        self.bufferButton.clicked.connect(self.away_cliced_callBack)
        self.bufferButton.rightClicked.connect(self.toward_cliced_callBack)
        self.bufferButton.scrollWheel.connect(self.scrollWheelCallBack)
        
        self.bufferCurveCheckBox.stateChanged.connect(self.bufferCurveCheckBox_changed_callBack)
        self.setFocus()
        
    def inverseRatio(self):
        self.spinBox.setValue(float(1/self.spinBox.value()))
        
    def set_style_button(self):
        self.snapButton.setFlat(True)
        self.snapButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.swapButton.setFlat(True)
        self.swapButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.bufferButton.setFlat(True)
        self.bufferButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        icon_path = os.path.join(os.path.dirname(__file__), r'..\icons') 
        
        bufferIcon = QIcon(icon_path + '\\customGraphEditor_buffer_Icon.png')
        priCycIcon = QIcon(':/bufferSnap.png')
        priCyOIcon = QIcon(':/bufferSwap.png')
        
        self.bufferButton.setIcon(bufferIcon)
        self.snapButton.setIcon(priCycIcon)
        self.swapButton.setIcon(priCyOIcon)
        
        iconSize = QSize(20,20)
        self.snapButton.setIconSize(iconSize)
        self.swapButton.setIconSize(iconSize)
        iconSize = QSize(24,24)
        self.bufferButton.setIconSize(iconSize)
        
        btnHSize = 24
        btnWSize = 24
        self.snapButton.setFixedSize(btnWSize,btnHSize)
        self.swapButton.setFixedSize(btnWSize,btnHSize)
        self.bufferButton.setFixedSize(btnWSize,btnHSize)
        
    def scrollWheelCallBack(self):
        sender = self.sender()
        sender.setFocus()
        ratio = 1.02
        if QApplication.queryKeyboardModifiers() == Qt.ControlModifier:
            ratio = 1.01
        elif QApplication.queryKeyboardModifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            ratio = 1.005
        elif QApplication.queryKeyboardModifiers() == Qt.ShiftModifier:
            ratio = 1.05
            
        if self.sender().y > 0:
            converge_buffer("away",ratio)
        else:
            converge_buffer("toward",ratio)
            
        
    def away_cliced_callBack(self):
        self.setFocus()
        converge_buffer("away",self.spinBox.value())
            
    def toward_cliced_callBack(self):
        self.setFocus()
        converge_buffer("toward",self.spinBox.value())
        
    def snap_swap_cliced_callBack(self):
        sender = self.sender()
        if sender == self.snapButton:
            bufferOption = '"snapshot"'
        elif sender == self.swapButton:
            bufferOption = '"swap"'
        
        cmd = 'doBuffer %s %sGraphEd'%(bufferOption,self.panelname)
        try:
            mel.eval(cmd)
        except:
            pass
            
    def bufferCurveCheckBox_changed_callBack(self,value):
        set_state_bufferCurve((self.panelname+"GraphEd"),value)
            
def main():
    mayaWindow = 'graphEditor1Window' #常にこのウィンドウより前にいます
    ptr = OpenMayaUI.MQtUtil.findWindow(mayaWindow)
    if ptr is not None:
        parent = wrapInstance(int(ptr),QWidget)
    else:
        cmds.error('Please open the GraphEditor')
    app = QApplication.instance()
    ui = KeysEditFromBufferUI(parent)
    ui.show()
    sys.exit()
    app.exec_()

if __name__ == "__main__":
    main()