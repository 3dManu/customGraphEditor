#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

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
	
def converge_buffer(option):
	keyCount = cmds.keyframe(q = True, kc = True, sl = True)
	if keyCount == 0:
		return
		
	cmds.undoInfo(openChunk=True,chunkName = "converge_buffer")
		
	if option == "toward":
		scaleValue = 0.9
	elif option == "away":
		scaleValue = 1/0.9
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
	
class KeysEditFromBufferUI(QMainWindow):
	def __init__(self,parent=None):
		super(KeysEditFromBufferUI,self).__init__(parent)
		self.setWindowFlags(Qt.Window)
		
		self.widget = KeysEditFromBufferWidget(self)
		self.setCentralWidget(self.widget)
		title = self.widget.windowTitle()
		self.setWindowTitle(title)
	
	def closeEvent(self, e):
		try:
			self.widget.close()
		except:
			pass
			
class KeysEditFromBufferWidget(QWidget):
	def __init__(self,parent=None,panelname = "graphEditor1"):
		super(KeysEditFromBufferWidget,self).__init__(parent)
		
		self.setFixedWidth(200)
		self.setWindowTitle("Keys Edit from Buffer")
		self.panelname = panelname
		
		self.initUI()
		
	def initUI(self):
		self.snapButton = QPushButton(self)
		self.swapButton = QPushButton(self)
		self.towardButton = QPushButton("Toward",self)
		self.awayButton = QPushButton("Away",self)
		
		self.set_style_button()
		
		self.bufferCurveCheckBox = QCheckBox(':Buffer Curves',self)
		
		vLayout = QVBoxLayout(self)
		vLayout.setSpacing(0)
		vLayout.setContentsMargins(0, 0, 0, 0)
		
		hLayout_A = QHBoxLayout(self)
		
		hLayout_C = QHBoxLayout(self)
		hLayout_C.setSpacing(8)
		hLayout_C.setContentsMargins(0, 0, 0, 0)
		
		hLayout_C.addWidget(self.snapButton,alignment=(Qt.AlignRight))
		hLayout_C.addWidget(self.swapButton,alignment=(Qt.AlignLeft))
		
		hLayout_A.addWidget(self.bufferCurveCheckBox,alignment=(Qt.AlignHCenter))
		hLayout_A.addLayout(hLayout_C,alignment=(Qt.AlignHCenter))
		
		hLayout_B = QHBoxLayout(self)
		hLayout_B.setSpacing(0)
		
		hLayout_B.addWidget(self.towardButton,alignment=(Qt.AlignHCenter))
		hLayout_B.addWidget(self.awayButton,alignment=(Qt.AlignHCenter))
		
		vLayout.addLayout(hLayout_A)
		vLayout.addLayout(hLayout_B)
		
		self.setLayout(vLayout)
		
		
		self.snapButton.clicked.connect(self.snap_swap_cliced_callBack)
		self.swapButton.clicked.connect(self.snap_swap_cliced_callBack)
		self.towardButton.clicked.connect(self.toward_away_cliced_callBack)
		self.awayButton.clicked.connect(self.toward_away_cliced_callBack)
		
		self.bufferCurveCheckBox.stateChanged.connect(self.bufferCurveCheckBox_changed_callBack)
		
		
	def set_style_button(self):
		self.snapButton.setFlat(True)
		self.snapButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}");
		self.swapButton.setFlat(True)
		self.swapButton.setStyleSheet("QPushButton:hover{background-color: #575757;border: none;}");
		
		
		priCycIcon = QIcon(':/bufferSnap.png')
		priCyOIcon = QIcon(':/bufferSwap.png')
		
		self.snapButton.setIcon(priCycIcon)
		self.swapButton.setIcon(priCyOIcon)
		
		iconSize = QSize(20,20)
		self.snapButton.setIconSize(iconSize)
		self.swapButton.setIconSize(iconSize)
		
		btnHSize = 24
		btnWSize = 40
		self.snapButton.setFixedSize(btnWSize,btnHSize)
		self.swapButton.setFixedSize(btnWSize,btnHSize)
		
		btnHSize = 96
		self.towardButton.setFixedWidth(btnHSize)
		self.awayButton.setFixedWidth(btnHSize)
		
	def toward_away_cliced_callBack(self):
		sender = self.sender()
		if sender == self.towardButton:
			converge_buffer("toward")
		elif sender == self.awayButton:
			converge_buffer("away")
		
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
	ptr = OpenMayaUI.MQtUtil.mainWindow()
	if ptr is not None:
		parent = wrapInstance(long(ptr),QWidget)
	else:
		cmds.error('Please open the GraphEditor')
	app = QApplication.instance()
	ui = KeysEditFromBufferUI(parent)
	ui.show()
	sys.exit()
	app.exec_()

if __name__ == "__main__":
	main()