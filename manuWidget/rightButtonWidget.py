#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

class RightClickButton(QPushButton):
    rightClicked = Signal()
    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.isF = self.isFlat()
            self.ss = self.styleSheet()
            self.setFlat(False)
            self.setStyleSheet("QPushButton{background-color:white;color:black;}")
        else:
            super(RightClickButton, self).mousePressEvent(e)
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.RightButton:
            self.rightClicked.emit()    
            self.setStyleSheet(self.ss)
            self.setFlat(self.isF)
        else:
            super(RightClickButton, self).mouseReleaseEvent(e)
        