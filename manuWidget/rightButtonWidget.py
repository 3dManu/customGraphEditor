#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds as cmds
import threading

try:
	from PySide.QtCore import *
	from PySide.QtGui import *
except ImportError:
	try:
		from PySide2.QtCore import *
		from PySide2.QtGui import *
		from PySide2.QtWidgets import *
	except ImportError:
		raise ImportError('No module named PySide and PySide2.')

class RightClickButton(QPushButton):
	rightClicked = Signal()
	def mousePressEvent(self, e):
		if e.button() == Qt.RightButton:
			self.setStyleSheet("QPushButton{background-color:white;color:black;}")
		else:
			super(RightClickButton, self).mousePressEvent(e)
	def mouseReleaseEvent(self, e):
		if e.button() == Qt.RightButton:
			self.rightClicked.emit()	
			self.setStyleSheet("")
		else:
			super(RightClickButton, self).mouseReleaseEvent(e)