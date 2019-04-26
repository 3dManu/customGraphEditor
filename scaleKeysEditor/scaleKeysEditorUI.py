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
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI

def openChunk_widget(name):
	cmds.undoInfo(openChunk=True,chunkName = name)
def closeChunk_widget(name):
	cmds.undoInfo(closeChunk=True,chunkName = name)
def keys_editor_func(option,piv):
	keyCount = cmds.keyframe(q=True, sl=True, kc=True)
	if keyCount == 0:
		return
		
	cmds.undoInfo(openChunk=True,chunkName = "keys_editor_func")
	
	if option == "push":
		scaleValue = 1/0.9
	elif option == "pull":
		scaleValue = 0.9
	elif option == "neg":
		scaleValue = -1
	elif option == "offset":
		pass
	else:
		cmds.undoInfo(closeChunk=True,chunkName = "keys_editor_func")
		return
		
	selectedCurves = cmds.keyframe(q = True, n = True, sl = True)
	for crv in selectedCurves:
		timeArray = cmds.keyframe(crv, q = True, tc = True, sl = True)
		if piv == "left":
			pivTime = cmds.findKeyframe(crv,which="previous",time=(timeArray[0],timeArray[0]))
			keyValue = cmds.keyframe(crv,q=True,time=(timeArray[0],timeArray[0]),vc=True)[0]
			pivValue = cmds.keyframe(crv,q=True,time=(pivTime,pivTime),vc=True)[0]
		elif piv == "right":
			pivTime = cmds.findKeyframe(crv,which="next",time=(timeArray[-1],timeArray[-1]))
			keyValue = cmds.keyframe(crv,q=True,time=(timeArray[-1],timeArray[-1]),vc=True)[0]
			pivValue = cmds.keyframe(crv,q=True,time=(pivTime,pivTime),vc=True)[0]
		elif piv == "avg":
			keyValues = cmds.keyframe(crv,q=True,sl=True,vc=True)
			pivValue = (max(keyValues)+min(keyValues))/2
		else:
			break
		
		selectedValues = cmds.keyframe(crv, q = True, iv = True, sl = True)
		if option == "offset":
			offsetValue = pivValue - keyValue
			for slv in selectedValues:
				cmds.keyframe(crv, relative = True, index = (slv,slv), vc = offsetValue)
		else:
			for slv in selectedValues:
				cmds.scaleKey(crv, index = (slv,slv), vp = pivValue, vs = scaleValue)
		
	cmds.undoInfo(closeChunk=True,chunkName = "keys_editor_func")
	
class ScaleKeysEditorUI(QMainWindow):
	def __init__(self,parent=None):
		super(ScaleKeysEditorUI,self).__init__(parent)
		self.setWindowFlags(Qt.Window)
		
		self.widget = ScaleKeysEditorWidget(self)
		self.setCentralWidget(self.widget)
		title = self.widget.windowTitle()
		self.setWindowTitle(title)
	
	def closeEvent(self, e):
		try:
			self.widget.close()
		except:
			pass

class RightClickButton(QPushButton):
	rightClicked = Signal()
	def mouseReleaseEvent(self, e):
		if e.button() == Qt.RightButton:
			self.rightClicked.emit()
		else:
			super(RightClickButton, self).mouseReleaseEvent(e)
			
class ScaleKeysEditorWidget(QWidget):
	def __init__(self,parent=None,panelname = "graphEditor1"):
		super(ScaleKeysEditorWidget,self).__init__(parent)
		
		self.setFixedWidth(200)
		self.setWindowTitle("Scale Keys Editor")
		self.panelname = panelname
		
		self.initUI()
		
	def initUI(self):
		self.pushButton = RightClickButton("Push",self)
		self.pullButton = RightClickButton("Pull",self)
		self.offsetButton = RightClickButton("Offset",self)
		self.avgButton = RightClickButton("Average",self)
		self.negButton = RightClickButton("Negative",self)
		
		self.set_style_button()
		
		vLayout = QVBoxLayout(self)
		vLayout.setSpacing(0)
		vLayout.setContentsMargins(0, 0, 0, 0)
		
		hLayout_A = QHBoxLayout(self)
		
		hLayout_A.addWidget(self.pushButton,alignment=(Qt.AlignHCenter))
		hLayout_A.addWidget(self.pullButton,alignment=(Qt.AlignHCenter))
		hLayout_A.addWidget(self.offsetButton,alignment=(Qt.AlignHCenter))
		
		hLayout_B = QHBoxLayout(self)
		
		hLayout_B.addWidget(self.avgButton,alignment=(Qt.AlignHCenter))
		hLayout_B.addWidget(self.negButton,alignment=(Qt.AlignHCenter))
		
		vLayout.addLayout(hLayout_A)
		vLayout.addLayout(hLayout_B)
		
		self.setLayout(vLayout)
		
		self.pushButton.clicked.connect(self.button_cliced_callBack)
		self.pullButton.clicked.connect(self.button_cliced_callBack)
		self.offsetButton.clicked.connect(self.button_cliced_callBack)
		self.avgButton.clicked.connect(self.button_cliced_callBack)
		self.negButton.clicked.connect(self.button_cliced_callBack)
		
		self.pushButton.rightClicked.connect(self.button_rightCliced_callBack)
		self.pullButton.rightClicked.connect(self.button_rightCliced_callBack)
		self.offsetButton.rightClicked.connect(self.button_rightCliced_callBack)
		self.avgButton.rightClicked.connect(self.button_rightCliced_callBack)
		self.negButton.rightClicked.connect(self.button_rightCliced_callBack)
		
	def set_style_button(self):
		btnHSize = 62
		self.pushButton.setFixedWidth(btnHSize)
		self.pullButton.setFixedWidth(btnHSize)
		self.offsetButton.setFixedWidth(btnHSize)
		btnHSize = 96
		self.avgButton.setFixedWidth(btnHSize)
		self.negButton.setFixedWidth(btnHSize)
		
	def button_cliced_callBack(self):
		pivot = "left"
		sender = self.sender()
		if sender == self.pushButton:
			option = "push"
		elif sender == self.pullButton:
			option = "pull"
		elif sender == self.offsetButton:
			option = "offset"
		elif sender == self.avgButton:
			option = "neg"
			pivot = "avg"
		elif sender == self.negButton:
			option = "neg"
		keys_editor_func(option,pivot)
		
	def button_rightCliced_callBack(self):
		pivot = "right"
		sender = self.sender()
		if sender == self.pushButton:
			option = "push"
		elif sender == self.pullButton:
			option = "pull"
		elif sender == self.offsetButton:
			option = "offset"
		elif sender == self.avgButton:
			option = "neg"
			pivot = "avg"
		elif sender == self.negButton:
			option = "neg"
		keys_editor_func(option,pivot)
			
def main():
	mayaWindow = 'graphEditor1Window' #常にこのウィンドウより前にいます
	ptr = OpenMayaUI.MQtUtil.findWindow(mayaWindow)
	ptr = OpenMayaUI.MQtUtil.mainWindow()
	if ptr is not None:
		parent = wrapInstance(long(ptr),QWidget)
	else:
		cmds.error('Please open the GraphEditor')
	app = QApplication.instance()
	ui = ScaleKeysEditorUI(parent)
	ui.show()
	sys.exit()
	app.exec_()

if __name__ == "__main__":
	main()