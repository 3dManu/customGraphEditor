#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
try:
	from PySide.QtCore import *
	from PySide.QtGui import *
	from shiboken import wrapInstance
except ImportError:
	try:
		from PySide2.QtCore import *
		from PySide2.QtGui import *
		from PySide2.QtWidgets import *
		from shiboken2 import wrapInstance
	except ImportError:
		# Failed import to PySide and PySide2.
		raise ImportError('No module named PySide and PySide2.')
import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI

def getSorceObj():
	curveName = cmds.keyframe(q=True,sl=True,name=True)
	obj = []
	if curveName is not None:
		for c in curveName:
			obj.extend(getConnectedObject(c))
		return list(set(obj))
	return None
	
def getConnectedObject(node):
    result = []
    
    dists = cmds.listConnections(node,s=False,d=True)
    targets = cmds.ls(dists, tr = True, shapes = True)
    if targets:
        return targets
    else:
        for dist in dists:
            result.extend(getConnectedObject(dist))
        return result
	
	
def selectObj():
	objNames = getSorceObj()
	if objNames is not None:
		cmds.select(objNames,r=True)
	
class sorveButtonUI(QMainWindow):
	def __init__(self,parent=None):
		super(sorveButtonUI,self).__init__(parent)
		self.setWindowFlags(Qt.Window)
		
		self.widget = sorceButtonWidget(self)
		self.setCentralWidget(self.widget)
		title = self.widget.windowTitle()
		self.setWindowTitle(title)
	
	def closeEvent(self, e):
		try:
			self.widget.close()
		except:
			pass
			
class sorceButtonWidget(QWidget):
	def __init__(self,parent=None):
		super(sorceButtonWidget,self).__init__(parent)
		
		self.setWindowTitle("Get Sorce Button")
		self.sorceButton = QPushButton(self)
		
		self.initUI()
		
	def initUI(self):
		vlay = QVBoxLayout(self)
		vlay.addWidget(self.sorceButton)
		vlay.setContentsMargins(0, 0, 0, 0)
		
		self.setLayout(vlay)
		
		self.sorceButton.setFixedWidth(180)
		self.sorceButton.clicked.connect(selectObj)
		
		self.scriptNo = []
		self.scriptNo.append(cmds.scriptJob(e=["SelectionChanged",self.changed_selection]))
		
		self.changed_selection()

	def closeEvent(self, e):
		if self.scriptNo:
			for no in self.scriptNo:
				cmds.scriptJob(k=no)
		
	def changed_selection(self):
		objNames = getSorceObj()
		if objNames is None or len(objNames) == 0:
			self.sorceButton.setText('')
		elif len(objNames) != 1:
			self.sorceButton.setText(objNames[0]+"...")
		else:
			self.sorceButton.setText(objNames[0])
			
def main():
	mayaWindow = 'graphEditor1Window' #常にこのウィンドウより前にいます
	ptr = OpenMayaUI.MQtUtil.findWindow(mayaWindow)
	if ptr is not None:
		parent = wrapInstance(long(ptr),QWidget)
	else:
		cmds.error('Please open the GraphEditor')
	app = QApplication.instance()
	ui = sorveButtonUI(parent)
	ui.show()
	sys.exit()
	app.exec_()

if __name__ == "__main__":
	main()