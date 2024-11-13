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

def keys_editor_func(option,piv,ratio = 1.1):
    keyCount = cmds.keyframe(q=True, sl=True, kc=True)
    if keyCount == 0:
        return
    
    if option == "push":
        scaleValue = ratio
    elif option == "pull":
        scaleValue = 1/ratio
    elif option == "neg":
        scaleValue = -1
    elif option == "offset":
        pass
    elif option == "same":
        pass
    else:
        return
        
    selectedCurves = cmds.keyframe(q = True, n = True, sl = True)
    for crv in selectedCurves:
        timeArray = cmds.keyframe(crv, q = True, tc = True, sl = True)
        if piv == "left":
        
            idx = cmds.keyframe(crv, q=True, selected=True, indexValue=True)[0]
            if idx == 0:
                inf = cmds.getAttr(crv+".preInfinity")
                if inf == 0:# constant
                    keyValue = cmds.keyframe(crv,q=True,time=(timeArray[0],timeArray[0]),vc=True)[0]
                    pivValue = cmds.keyframe(crv,q=True,time=(timeArray[0],timeArray[0]),vc=True)[0]
                elif inf <= 3 :# cycle or linear
                    keyValue = cmds.keyframe(crv,q=True,time=(timeArray[0],timeArray[0]),vc=True)[0]
                    pivValue = cmds.keyframe(crv,q=True,vc=True)[-2]
                elif inf == 4:# cycle offset 
                    keyValue = cmds.keyframe(crv,q=True,time=(timeArray[0],timeArray[0]),vc=True)[0]
                    keyArray = cmds.keyframe(crv,q=True,vc=True)
                    pivValue = keyArray[0] - (keyArray[-1] - keyArray[-2])
                elif inf == 5:# oscillate
                    keyValue = cmds.keyframe(crv,q=True,time=(timeArray[0],timeArray[0]),vc=True)[0]
                    pivValue = cmds.keyframe(crv,q=True,vc=True)[1]
            else:
                pivTime = cmds.findKeyframe(crv,which="previous",time=(timeArray[0],timeArray[0]))
                keyValue = cmds.keyframe(crv,q=True,time=(timeArray[0],timeArray[0]),vc=True)[0]
                pivValue = cmds.keyframe(crv,q=True,time=(pivTime,pivTime),vc=True)[0]
                
        elif piv == "right":
        
            idx = cmds.keyframe(crv, q=True, selected=True, indexValue=True)[-1]
            if idx == cmds.keyframe(crv, q = True, keyframeCount = True) - 1:
                inf = cmds.getAttr(crv+".postInfinity")
                if inf == 0:# constant
                    keyValue = cmds.keyframe(crv,q=True,time=(timeArray[-1],timeArray[-1]),vc=True)[0]
                    pivValue = cmds.keyframe(crv,q=True,time=(timeArray[-1],timeArray[-1]),vc=True)[0]
                elif inf <= 3 :# cycle or linear
                    keyValue = cmds.keyframe(crv,q=True,time=(timeArray[-1],timeArray[-1]),vc=True)[0]
                    pivValue = cmds.keyframe(crv,q=True,vc=True)[1]
                elif inf == 4:# cycle offset 
                    keyValue = cmds.keyframe(crv,q=True,time=(timeArray[-1],timeArray[-1]),vc=True)[0]
                    keyArray = cmds.keyframe(crv,q=True,vc=True)
                    pivValue = keyArray[-1] - (keyArray[0] - keyArray[1])
                elif inf == 5:# oscillate
                    keyValue = cmds.keyframe(crv,q=True,time=(timeArray[-1],timeArray[-1]),vc=True)[0]
                    pivValue = cmds.keyframe(crv,q=True,vc=True)[-2]
            else:
                pivTime = cmds.findKeyframe(crv,which="next",time=(timeArray[-1],timeArray[-1]))
                keyValue = cmds.keyframe(crv,q=True,time=(timeArray[-1],timeArray[-1]),vc=True)[0]
                pivValue = cmds.keyframe(crv,q=True,time=(pivTime,pivTime),vc=True)[0]
                
        elif piv == "avg":
            keyValues = cmds.keyframe(crv,q=True,sl=True,vc=True)
            pivValue = (max(keyValues)+min(keyValues))/2
        elif piv == "def":
            keyValue = cmds.keyframe(crv,q=True,time=(timeArray[0],timeArray[0]),vc=True)[0]
            attrName = cmds.listConnections("{0}.output".format(crv),s=False,d=True,p=True)[0]
            pivValue = cmds.attributeQuery(attrName.split(".")[1],node = attrName.split(".")[0],listDefault=True)[0]
        elif piv == "first":
            pivValue = cmds.keyframe(crv,q=True,sl=True,vc=True)[0]
        elif piv == "last":
            pivValue = cmds.keyframe(crv,q=True,sl=True,vc=True)[-1]
        elif piv == "zero":
            keyValue = cmds.keyframe(crv,q=True,sl=True,vc=True)[0]
            pivValue = 0
        elif piv == "max":
            pivValue = max(cmds.keyframe(crv,q=True,sl=True,vc=True))
        elif piv == "min":
            pivValue = min(cmds.keyframe(crv,q=True,sl=True,vc=True))
        else:
            break
        
        
        selectedValues = cmds.keyframe(crv, q = True, iv = True, sl = True)
        if option == "offset":
            offsetValue = pivValue - keyValue
            for slv in selectedValues:
                cmds.keyframe(crv, relative = True, index = (slv,slv), vc = offsetValue)
        elif option == "same":
            for slv in selectedValues:
                cmds.keyframe(crv, absolute = True, index = (slv,slv), vc = pivValue)
        else:
            for slv in selectedValues:
                cmds.scaleKey(crv, index = (slv,slv), vp = pivValue, vs = scaleValue)
        
    
def swap_selectionCurves():
    cmds.undoInfo(openChunk=True,chunkName = "swap_selectionCurves")
    
    crvs = cmds.keyframe(q=True, selected=True, name=True)
    if crvs is None:
        cmds.warning("Please selected animCurves")
        return
    if len(crvs) != 2:
        cmds.warning("Please selected 2 animCurves")
        return
    connectInfo = []
    for crv in crvs:
        if cmds.referenceQuery(crv, isNodeReferenced = True):
            cmds.warning("cant edit from reference file.")
            return
            
        connectInfo.extend(cmds.listConnections(crv + ".output", connections = True, plugs = True))
        
    cmds.connectAttr(connectInfo[0], connectInfo[3], force = True)
    cmds.connectAttr(connectInfo[2], connectInfo[1], force = True)
    tmpName = []
    tmpName.append(cmds.rename(crvs[0],"%s_tmp"%crvs[0]))
    tmpName.append(cmds.rename(crvs[1],"%s_tmp"%crvs[1]))
    cmds.rename(tmpName[0],crvs[1])
    cmds.rename(tmpName[1],crvs[0])
    
    cmds.undoInfo(closeChunk=True,chunkName = "swap_selectionCurves")
    
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
            self.clearFocus()
        
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
            
    
    
class ScaleKeysEditorUI(QMainWindow):
    def __init__(self,parent=None):
        super(ScaleKeysEditorUI,self).__init__(parent)
        self.setWindowFlags(Qt.Window|Qt.WindowCloseButtonHint)
        
        self.widget = ScaleKeysEditorWidget(self, layoutType = True)
        self.setCentralWidget(self.widget)
        title = self.widget.windowTitle()
        self.setWindowTitle(title)
    
    def closeEvent(self, e):
        try:
            self.widget.close()
        except:
            pass
            
class ScaleKeysEditorWidget(QWidget):
    def __init__(self,parent=None,panelname = "graphEditor1", layoutType = True):
        super(ScaleKeysEditorWidget,self).__init__(parent)
        
        self.setBaseSize(60,240)
        self.setWindowTitle("Scale Keys Editor")
        self.panelname = panelname
        
        self.initUI(layoutType)
        
    def initUI(self, layoutType):
        self.leftAxisButton = WheelButton(self)
        self.rightAxisButton = WheelButton(self)
        self.maxAxisButton = WheelButton(self)
        self.minAxisButton = WheelButton(self)
        self.defalutButton = WheelButton(self)
        self.avgButton = WheelButton(self)
        self.offsetButton = rightButtonWidget.RightClickButton(self)
        self.negButton = rightButtonWidget.RightClickButton(self)
        self.reverseButton = rightButtonWidget.RightClickButton(self)
        self.sameButton = rightButtonWidget.RightClickButton(self)
        self.swapButton = QPushButton(self)
        self.mdButton = QPushButton("^-1",self)
        self.spinBox = doubleSpinBoxWidget.DoubleSpinBox(self)
        self.spinBox.setRange(0.01,10)
        self.spinBox.setDecimals(2)
        self.spinBox.setSingleStep(0.05)
        self.spinBox.setValue(1.1)
        self.mdButton.setFixedSize(24,24)
        
        self.set_style_button()
        
        if layoutType:
            mainLayout = QVBoxLayout(self)
            subLayout_a = QHBoxLayout(self)
            subLayout_b = QHBoxLayout(self)
            self.spinBox.setFixedWidth(64)
        else:
            mainLayout = QHBoxLayout(self)
            subLayout_a = QVBoxLayout(self)
            subLayout_b = QVBoxLayout(self)
            self.spinBox.editArrows()
        
        mainLayout.setSpacing(6)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        
        subLayout_a.addWidget(self.mdButton)
        subLayout_a.addSpacing(-4)
        subLayout_a.addWidget(self.spinBox)
        subLayout_a.addWidget(self.leftAxisButton)
        subLayout_a.addWidget(self.rightAxisButton)
        subLayout_a.addWidget(self.maxAxisButton)
        subLayout_a.addWidget(self.minAxisButton)
        
        subLayout_b.addWidget(self.defalutButton)
        subLayout_b.addWidget(self.avgButton)
        subLayout_b.addWidget(self.reverseButton)
        subLayout_b.addWidget(self.negButton)
        subLayout_b.addWidget(self.offsetButton)
        subLayout_b.addWidget(self.sameButton)
        subLayout_b.addWidget(self.swapButton)
        
        mainLayout.addLayout(subLayout_a)
        mainLayout.addLayout(subLayout_b)
        self.setLayout(mainLayout)
        
        self.leftAxisButton.clicked.connect(self.button_clicked_callBack)
        self.rightAxisButton.clicked.connect(self.button_clicked_callBack)
        self.maxAxisButton.clicked.connect(self.button_clicked_callBack)
        self.minAxisButton.clicked.connect(self.button_clicked_callBack)
        self.offsetButton.clicked.connect(self.button_clicked_callBack)
        self.avgButton.clicked.connect(self.button_clicked_callBack)
        self.negButton.clicked.connect(self.button_clicked_callBack)
        self.defalutButton.clicked.connect(self.button_clicked_callBack)
        self.reverseButton.clicked.connect(self.button_clicked_callBack)
        self.sameButton.clicked.connect(self.button_clicked_callBack)
        
        self.swapButton.clicked.connect(swap_selectionCurves)
        self.mdButton.clicked.connect(self.inverseRatio)
        
        self.leftAxisButton.rightClicked.connect(self.button_rightClicked_callBack)
        self.rightAxisButton.rightClicked.connect(self.button_rightClicked_callBack)
        self.maxAxisButton.rightClicked.connect(self.button_rightClicked_callBack)
        self.minAxisButton.rightClicked.connect(self.button_rightClicked_callBack)
        self.offsetButton.rightClicked.connect(self.button_rightClicked_callBack)
        self.avgButton.rightClicked.connect(self.button_rightClicked_callBack)
        self.negButton.rightClicked.connect(self.button_rightClicked_callBack)
        self.defalutButton.rightClicked.connect(self.button_rightClicked_callBack)
        self.reverseButton.rightClicked.connect(self.button_rightClicked_callBack)
        self.sameButton.rightClicked.connect(self.button_rightClicked_callBack)
        
        self.leftAxisButton.scrollWheel.connect(self.scrollWheelCallBack)
        self.rightAxisButton.scrollWheel.connect(self.scrollWheelCallBack)
        self.maxAxisButton.scrollWheel.connect(self.scrollWheelCallBack)
        self.minAxisButton.scrollWheel.connect(self.scrollWheelCallBack)
        self.defalutButton.scrollWheel.connect(self.scrollWheelCallBack)
        self.avgButton.scrollWheel.connect(self.scrollWheelCallBack)
        self.setFocus()
            
        
    def set_style_button(self):
        icon_path = os.path.join(os.path.dirname(__file__), r'..\icons') 
        
        leftAxisIcon = QIcon(icon_path + '\\customGraphEditor_leftAxis_Icon.png')
        rightAxisIcon = QIcon(icon_path + '\\customGraphEditor_rightAxis_Icon.png')
        maxAxisIcon = QIcon(icon_path + '\\customGraphEditor_maxAxis_Icon.png')
        minAxisIcon = QIcon(icon_path + '\\customGraphEditor_minAxis_Icon.png')
        defaultIcon = QIcon(icon_path + '\\customGraphEditor_default_Icon.png')
        reverseIcon = QIcon(icon_path + '\\customGraphEditor_reverse_Icon.png')
        negativeIcon = QIcon(icon_path + '\\customGraphEditor_negative_Icon.png')
        averageIcon = QIcon(icon_path + '\\customGraphEditor_average_Icon.png')
        offsetIcon = QIcon(icon_path + '\\customGraphEditor_offset_Icon.png')
        sameIcon = QIcon(icon_path + '\\customGraphEditor_same_Icon.png')
        swapIcon = QIcon(icon_path + '\\customGraphEditor_swap_Icon.png')
        
        self.leftAxisButton.setIcon(leftAxisIcon)
        self.rightAxisButton.setIcon(rightAxisIcon)
        self.maxAxisButton.setIcon(maxAxisIcon)
        self.minAxisButton.setIcon(minAxisIcon)
        self.defalutButton.setIcon(defaultIcon)
        self.reverseButton.setIcon(reverseIcon)
        self.negButton.setIcon(negativeIcon)
        self.avgButton.setIcon(averageIcon)
        self.offsetButton.setIcon(offsetIcon)
        self.sameButton.setIcon(sameIcon)
        self.swapButton.setIcon(swapIcon)
        
        self.leftAxisButton.setFlat(True)
        self.rightAxisButton.setFlat(True)
        self.maxAxisButton.setFlat(True)
        self.minAxisButton.setFlat(True)
        self.defalutButton.setFlat(True)
        self.reverseButton.setFlat(True)
        self.negButton.setFlat(True)
        self.avgButton.setFlat(True)
        self.offsetButton.setFlat(True)
        self.sameButton.setFlat(True)
        self.swapButton.setFlat(True)
        
        self.leftAxisButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.rightAxisButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.maxAxisButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.minAxisButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.defalutButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.reverseButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.negButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.avgButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.offsetButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.sameButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.swapButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        
        iconSize = QSize(24,24)
        
        self.leftAxisButton.setIconSize(iconSize)
        self.rightAxisButton.setIconSize(iconSize)
        self.maxAxisButton.setIconSize(iconSize)
        self.minAxisButton.setIconSize(iconSize)
        self.defalutButton.setIconSize(iconSize)
        self.reverseButton.setIconSize(iconSize)
        self.negButton.setIconSize(iconSize)
        self.avgButton.setIconSize(iconSize)
        self.offsetButton.setIconSize(iconSize)
        self.sameButton.setIconSize(iconSize)
        self.swapButton.setIconSize(iconSize)
    
        btnSize = 24
        self.leftAxisButton.setFixedSize(btnSize,btnSize)
        self.rightAxisButton.setFixedSize(btnSize,btnSize)
        self.maxAxisButton.setFixedSize(btnSize,btnSize)
        self.minAxisButton.setFixedSize(btnSize,btnSize)
        self.avgButton.setFixedSize(btnSize,btnSize)
        self.defalutButton.setFixedSize(btnSize,btnSize)
        self.reverseButton.setFixedSize(btnSize,btnSize)
        self.negButton.setFixedSize(btnSize,btnSize)
        self.offsetButton.setFixedSize(btnSize,btnSize)
        self.sameButton.setFixedSize(btnSize,btnSize)
        self.swapButton.setFixedSize(btnSize,btnSize)
    
    def inverseRatio(self):
        self.spinBox.setValue(float(1/self.spinBox.value()))
        
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
            if sender == self.leftAxisButton:
                option = "push"
                pivot = "left"
            elif sender == self.rightAxisButton:
                option = "push"
                pivot = "right"
            elif sender == self.maxAxisButton:
                option = "push"
                pivot = "max"
            elif sender == self.minAxisButton:
                option = "push"
                pivot = "min"
            elif sender == self.defalutButton:
                option = "push"
                pivot = "def"
            elif sender == self.avgButton:
                option = "push"
                pivot = "avg"
        else:
            if sender == self.leftAxisButton:
                option = "pull"
                pivot = "left"
            elif sender == self.rightAxisButton:
                option = "pull"
                pivot = "right"
            elif sender == self.maxAxisButton:
                option = "pull"
                pivot = "max"
            elif sender == self.minAxisButton:
                option = "pull"
                pivot = "min"
            elif sender == self.defalutButton:
                option = "pull"
                pivot = "def"
            elif sender == self.avgButton:
                option = "pull"
                pivot = "avg"
            
        keys_editor_func(option,pivot,ratio)
        
    def button_clicked_callBack(self):
        self.setFocus()
        sender = self.sender()
        ratio = None
        if sender == self.leftAxisButton:
            option = "push"
            pivot = "left"
            ratio = self.spinBox.value()
        elif sender == self.rightAxisButton:
            option = "push"
            pivot = "right"
            ratio = self.spinBox.value()
        elif sender == self.maxAxisButton:
            option = "push"
            pivot = "max"
            ratio = self.spinBox.value()
        elif sender == self.minAxisButton:
            option = "push"
            pivot = "min"
            ratio = self.spinBox.value()
        elif sender == self.defalutButton:
            option = "push"
            pivot = "def"
            ratio = self.spinBox.value()
        elif sender == self.offsetButton:
            option = "offset"
            pivot = "left"
        elif sender == self.avgButton:
            option = "push"
            pivot = "avg"
            ratio = self.spinBox.value()
        elif sender == self.reverseButton:
            option = "neg"
            pivot = "avg"
        elif sender == self.negButton:
            option = "neg"
            pivot = "left"
        elif sender == self.sameButton:
            option = "same"
            pivot = "first"
        else:
            return
            
        cmds.undoInfo(openChunk=True,chunkName = "click_func")
        keys_editor_func(option,pivot,ratio)
        cmds.undoInfo(closeChunk=True,chunkName = "click_func")
        
    def button_rightClicked_callBack(self):
        self.setFocus()
        sender = self.sender()
        ratio = None
        if sender == self.leftAxisButton:
            option = "pull"
            pivot = "left"
            ratio = self.spinBox.value()
        elif sender == self.rightAxisButton:
            option = "pull"
            pivot = "right"
            ratio = self.spinBox.value()
        elif sender == self.maxAxisButton:
            option = "pull"
            pivot = "max"
            ratio = self.spinBox.value()
        elif sender == self.minAxisButton:
            option = "pull"
            pivot = "min"
            ratio = self.spinBox.value()
        elif sender == self.defalutButton:
            option = "pull"
            pivot = "def"
            ratio = self.spinBox.value()
        elif sender == self.offsetButton:
            option = "offset"
            pivot = "right"
        elif sender == self.avgButton:
            option = "pull"
            pivot = "avg"
            ratio = self.spinBox.value()
        elif sender == self.reverseButton:
            option = "neg"
            pivot = "zero"
        elif sender == self.negButton:
            option = "neg"
            pivot = "right"
        elif sender == self.sameButton:
            option = "same"
            pivot = "last"
        else:
            return
            
        cmds.undoInfo(openChunk=True,chunkName = "rightClick_func")
        keys_editor_func(option,pivot,ratio)
        cmds.undoInfo(closeChunk=True,chunkName = "rightClick_func")
            
def main():
    mayaWindow = 'graphEditor1Window' #常にこのウィンドウより前にいます
    ptr = OpenMayaUI.MQtUtil.findWindow(mayaWindow)
    if ptr is not None:
        parent = wrapInstance(int(ptr),QWidget)
    else:
        cmds.error('Please open the GraphEditor')
    app = QApplication.instance()
    ui = ScaleKeysEditorUI(parent)
    ui.show()
    sys.exit()
    app.exec_()

if __name__ == "__main__":
    main()