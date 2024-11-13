# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
from maya import cmds, mel

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
from ..manuWidget import separatorWidget as separatorWidget

import maya.OpenMayaUI as omui
        
def getAnimatedAttrs(objs):
    animAttr = []
    for obj in objs:
        attrList = cmds.listAttr(obj,keyable = True)
        if not attrList:
            continue
        for attr in attrList:
            isAnim = cmds.listConnections("{0}.{1}".format(obj,attr),type = "animCurve",destination = False, source = True)
            isBlend = cmds.listConnections("{0}.{1}".format(obj,attr),type = "pairBlend",destination = False, source = True)
            if isAnim or isBlend:
                animAttr.append(attr)
    
    return animAttr
        
class FilterUI(QMainWindow):
    def __init__(self,parent=None):
        super(FilterUI,self).__init__(parent)
        self.setWindowFlags(Qt.Window|Qt.WindowCloseButtonHint)
        self.resize(40,120)
        
        widget = FilterWidget(layoutType = True)
        self.setCentralWidget(widget)
        title = widget.windowTitle()
        self.setWindowTitle(title)
    
    def closeEvent(self, e):
        try:
            self.widget.close()
        except:
            pass
        
class FilterWidget(QWidget):
    def __init__(self,parent=None,panelname = "graphEditor1", layoutType = True):
        super(FilterWidget,self).__init__(parent)
        self.setWindowTitle('GraphEditor Filter')
        
        self.panelname = panelname
        
        if layoutType: 
            mainLayout = QVBoxLayout()
            subLayout_a = QHBoxLayout()
            subLayout_b = QHBoxLayout()
            sepWidget = separatorWidget.QVLine
            partitionName = ":"
        else:
            mainLayout = QHBoxLayout()
            subLayout_a = QVBoxLayout()
            subLayout_b = QVBoxLayout()
            sepWidget = separatorWidget.QHLine
            partitionName = ":"
            
        mainLayout.addLayout(subLayout_a)
        mainLayout.addLayout(subLayout_b)
        self.setLayout(mainLayout)
        self.vecBtn = []
        self.attrBtn = []
        btnName = ["x","y","z"]
        btnColor = ["#ff0000","#00ff00","#0000ff"]
        separatorLabel = []
        for i in range(9):
            if i < 6:
                subLayout = subLayout_a
            else:
                subLayout = subLayout_b
                
            if i%3 == 0:
                separatorLabel.append(sepWidget())
                if i/3 == 0:
                    self.attrBtn.append(QPushButton("Tr"))
                    self.attrBtn[0].setCheckable(True)
                    self.attrBtn[0].setFixedWidth(24)
                    self.attrBtn[0].toggled.connect(self.toggleButtons)
                    subLayout.addWidget(self.attrBtn[0])
                elif i/3 == 1:
                    subLayout.addSpacing(2)
                    subLayout.addWidget(separatorLabel[-1])
                    subLayout.addSpacing(2)
                    self.attrBtn.append(QPushButton("Ro"))
                    self.attrBtn[1].setCheckable(True)
                    self.attrBtn[1].setFixedWidth(24)
                    self.attrBtn[1].toggled.connect(self.toggleButtons)
                    subLayout.addWidget(self.attrBtn[1])
                else:
                    self.attrBtn.append(QPushButton("Sc"))
                    self.attrBtn[2].setCheckable(True)
                    self.attrBtn[2].setFixedWidth(24)
                    self.attrBtn[2].toggled.connect(self.toggleButtons)
                    subLayout.addWidget(self.attrBtn[2])
                subLayout.addSpacing(5)
                    
            self.vecBtn.append(QPushButton(btnName[i%3]))
            self.vecBtn[i].setFixedWidth(22)
            self.vecBtn[i].setFixedHeight(22)
            self.vecBtn[i].setCheckable(True)
            self.vecBtn[i].setStyleSheet("QPushButton{color: %s;font-weight: bold;}"%btnColor[i%3])
            self.vecBtn[i].toggled.connect(self.setFilterCommand)
            
            subLayout.addWidget(self.vecBtn[i])
        
        subLayout_b.addSpacing(2)
        separatorLabel.append(sepWidget())
        subLayout_b.addWidget(separatorLabel[-1])
        subLayout_b.addSpacing(2)
        self.visBtn = QPushButton("v")
        self.visBtn.setFixedWidth(22)
        self.visBtn.setCheckable(True)
        self.visBtn.setStyleSheet("QPushButton{color: #cccccc;font-weight: bold;}")
        self.visBtn.toggled.connect(self.setFilterCommand)
        subLayout_b.addWidget(self.visBtn) 
        subLayout_b.addSpacing(5)
        
        #-------------------------------------#
        self.menu = QMenu(self)
        
        self.otherBtn = QPushButton("▼")
        self.otherBtn.setFixedWidth(22)
        self.otherBtn.setStyleSheet("QPushButton{color: #cccccc;font-weight: bold;}")
        self.otherBtn.clicked.connect(self.showCustomContextMenu)
        subLayout_b.addWidget(self.otherBtn)  
        subLayout_b.addSpacing(5)
        
        if layoutType: 
            self.resetBtn = QPushButton("Reset")
            self.resetBtn.setFixedWidth(46)
        else:
            self.resetBtn = QPushButton("Re")
            self.resetBtn.setFixedWidth(22)
        self.resetBtn.clicked.connect(self.clearFilter)
        subLayout_b.addWidget(self.resetBtn)  
        #-------------------------------------#
        
        subLayout_a.addStretch(0)
        subLayout_a.setSpacing(4)
        subLayout_a.setContentsMargins(0, 0, 0, 0)
        subLayout_b.addStretch(0)
        subLayout_b.setSpacing(4)
        subLayout_b.setContentsMargins(0, 0, 0, 0)
        mainLayout.setContentsMargins(0, 0, 0, 0)
    
    def clearFilter(self):
        """ this command clears for other attribute filters
        defaultAttr = ["translateX","translateY","translateZ","rotateX","rotateY","rotateZ","scaleX","scaleY","scaleZ","visibility"]
        filterUISelectAttributes = mel.eval('$gFilterUISelectedAttributes = $gFilterUISelectedAttributes')
        
        for attr in filterUISelectAttributes:
            mel.eval("filterUISelectAttributesCheckbox %s %s %sOutlineEd;"%(attr,0,self.panelname))
        """
        
        for b in self.vecBtn:
            b.blockSignals(True)
            b.setChecked(False)
        for b in self.attrBtn:
            b.setChecked(False)
        self.visBtn.blockSignals(True)
        self.visBtn.setChecked(False)
        
        mel.eval("filterUIClearFilter %sOutlineEd;"%(self.panelname))
        
        self.visBtn.blockSignals(False)
        for b in self.vecBtn:
            b.blockSignals(False)
            
        filterUISelectAttributes = mel.eval('clear $gFilterUISelectedAttributes')
    
    def showCustomContextMenu(self):
        filterUISelectAttributes = mel.eval('$gFilterUISelectedAttributes = $gFilterUISelectedAttributes')
        for w in self.menu.actions():
            if isinstance(w, QWidgetAction):
                w.defaultWidget().deleteLater()
                self.menu.removeAction(w)

        defaultAttr = ["translateX","translateY","translateZ","rotateX","rotateY","rotateZ","scaleX","scaleY","scaleZ","visibility"]
        selectObj = cmds.ls(sl=True)
        animAttr = getAnimatedAttrs(selectObj)
        diffAttr = list(set(animAttr) - set(defaultAttr))
        
        if diffAttr:
            for attr in diffAttr: 
                checkBox = QCheckBox(attr)
                if attr in filterUISelectAttributes:
                    checkBox.setChecked(True)
                widgetAction = QWidgetAction(self)
                widgetAction.setDefaultWidget(checkBox)
                self.menu.addAction(widgetAction)
                checkBox.stateChanged.connect(self.setFilterCommand)
        else:
            label = QLabel("== None ==")
            widgetAction = QWidgetAction(self)
            widgetAction.setDefaultWidget(label)
            self.menu.addAction(widgetAction)

        pos = self.otherBtn.mapToGlobal(self.otherBtn.rect().bottomLeft())
        self.menu.exec_(pos)
    
    def toggleButtons(self,chk):
        sender = self.sender()
        if sender == self.attrBtn[0]:
            self.vecBtn[0].setChecked(chk)
            self.vecBtn[1].setChecked(chk)
            self.vecBtn[2].setChecked(chk)
        elif sender == self.attrBtn[1]:
            self.vecBtn[3].setChecked(chk)
            self.vecBtn[4].setChecked(chk)
            self.vecBtn[5].setChecked(chk)
        elif sender == self.attrBtn[2]:
            self.vecBtn[6].setChecked(chk)
            self.vecBtn[7].setChecked(chk)
            self.vecBtn[8].setChecked(chk)
    
    def setFilterCommand(self,chk):
        sender = self.sender()
        attr = ""
        if sender == self.vecBtn[0]:
            attr = "translateX"
        elif sender == self.vecBtn[1]:
            attr = "translateY"
        elif sender == self.vecBtn[2]:
            attr = "translateZ"
        elif sender == self.vecBtn[3]:
            attr = "rotateX"
        elif sender == self.vecBtn[4]:
            attr = "rotateY"
        elif sender == self.vecBtn[5]:
            attr = "rotateZ"
        elif sender == self.vecBtn[6]:
            attr = "scaleX"
        elif sender == self.vecBtn[7]:
            attr = "scaleY"
        elif sender == self.vecBtn[8]:
            attr = "scaleZ"
        elif sender == self.visBtn:
            attr = "visibility"
        else:
            attr = sender.text() 
            
        mel.eval("filterUISelectAttributesCheckbox %s %s %sOutlineEd;"%(attr,int(chk),self.panelname))


def main():
    mayaWindow = 'graphEditor1Window' #常にこのウィンドウより前にいます
    ptr = omui.MQtUtil.findWindow(mayaWindow)
    if ptr is None:
        ptr = omui.MQtUtil.mainWindow()
    parent = wrapInstance(int(ptr),QWidget)
    app = QApplication.instance()
    ui = FilterUI(parent)
    ui.show()
    sys.exit()
    app.exec_()

if __name__ == "__main__":
    main()   