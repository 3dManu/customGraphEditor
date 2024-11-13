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

class ExampleWindow(QMainWindow):
    def __init__(self,parent=None,rowColumn = False):
        super(ExampleWindow,self).__init__(parent)
        self.setWindowFlags(Qt.Window|Qt.WindowCloseButtonHint)
        
        widget = CollapsibleLineWidget(parent,rowColumn)
        self.setCentralWidget(widget)
        title = widget.windowTitle()
        self.setWindowTitle(title)
        
        for i in range(5):
            widget.addWidget(QPushButton('Button %s' % i, widget))

class CollapsibleLineWidget(QWidget):
    def __init__(self, parent = None, rowColumn = False):
        super(CollapsibleLineWidget, self).__init__(parent)
        self.rowColumn = rowColumn
        
        self.__frame = QFrame()
        self.__frame.setLineWidth(2)
        self.__frame.setMidLineWidth(1)
        self.__frame.setFrameShadow(QFrame.Sunken)
        
        if self.rowColumn:#row
            self.__frame.setFrameShape(QFrame.VLine)
            self.__layout = QHBoxLayout()
            self.__layout.addWidget(self.__frame,alignment = (Qt.AlignLeft))
            self.__layout.setContentsMargins(4, 0, 0, 0)
        else:#column
            self.__frame.setFrameShape(QFrame.HLine)
            self.__layout = QVBoxLayout()
            self.__layout.addWidget(self.__frame,alignment = (Qt.AlignTop))
            self.__layout.setContentsMargins(0, 4, 0, 0)
        
        self.__layout.setSpacing(4)
        
        self.setLayout(self.__layout)
        
         
        self.__collapsed = False
    
    def addWidget(self, widget):
        self.__layout.addWidget(widget)
         
    def expandCollapseRect(self):
        if self.rowColumn:
            return QRect(0, 0, 8, self.height())
        else:
            return QRect(0, 0, self.width(), 8)
 
    def mouseReleaseEvent(self, event):
        if self.expandCollapseRect().contains(event.pos()):
            self.toggleCollapsed()
            event.accept()
        else:
            event.ignore()
     
    def toggleCollapsed(self):
        self.setCollapsed(not self.__collapsed)
        
    def getChildWidget(self):
        index = self.__layout.count()
        widgetList = []
        for i in range(index):
            w = self.__layout.itemAt(i).widget()
            if isinstance(w,QWidget):
                widgetList.append(w)
        return widgetList
        
    def isCollapsed(self):
        return self.__collapsed
         
    def setCollapsed(self, state=True):
        self.__collapsed = state
 
        if state:
            self.__frame.setFrameShadow(QFrame.Raised)
            if self.rowColumn:
                self.setMinimumWidth(16)
                self.setMaximumWidth(16)
                widgetList = self.getChildWidget()[1:]
                for w in widgetList:
                    w.setVisible(False)
            else:
                self.setMinimumHeight(16)
                self.setMaximumHeight(16)
                widgetList = self.getChildWidget()[1:]
                for w in widgetList:
                    w.setVisible(False)
        else:
            self.__frame.setFrameShadow(QFrame.Sunken)
            if self.rowColumn:
                self.setMinimumWidth(0)
                self.setMaximumWidth(1000000)
                widgetList = self.getChildWidget()[1:]
                for w in widgetList:
                    w.setVisible(True)
            else:
                self.setMinimumHeight(0)
                self.setMaximumHeight(1000000)
                widgetList = self.getChildWidget()[1:]
                for w in widgetList:
                    w.setVisible(True)
                
def main():
    app = QApplication.instance()
    ui = ExampleWindow(None,True)
    ui.show()
    sys.exit()
    app.exec_()

if __name__ == "__main__":
    main()   