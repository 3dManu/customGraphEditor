# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
from maya import cmds, mel

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
		
class FilterUI(QMainWindow):
	def __init__(self,parent=None):
		super(FilterUI,self).__init__(parent)
		self.setWindowFlags(Qt.Window)
		self.resize(150,200)
		
		widget = FilterWidget()
		self.setCentralWidget(widget)
		title = widget.windowTitle()
		self.setWindowTitle(title)
	
	def closeEvent(self, e):
		try:
			self.widget.close()
		except:
			pass
		
class FilterWidget(QWidget):
	def __init__(self,parent=None,panelname = "graphEditor1"):
		super(FilterWidget,self).__init__(parent)
		self.setWindowTitle('Set Key')
		
		self.panelname = panelname
		
		hLayout_A = QHBoxLayout()
		hLayout_B = QHBoxLayout()
		hLayout_C = QHBoxLayout()
		vLayout = QVBoxLayout()
		vLayout.addLayout(hLayout_A)
		vLayout.addLayout(hLayout_B)
		vLayout.addLayout(hLayout_C)
		self.setLayout(vLayout)
		self.vecBtn = []
		self.attrBtn = []
		btnName = ["x","y","z"]
		btnColor = ["#ff0000","#00ff00","#0000ff"]
		labelName = ":"
		for i in range(9):
			if i%3 == 0:
				label = QLabel(labelName)
				if i/3 == 0:
					self.attrBtn.append(QPushButton("Trs"))
					self.attrBtn[0].setCheckable(True)
					self.attrBtn[0].setFixedWidth(40)
					self.attrBtn[0].toggled.connect(self.toggleButtons)
					hLayout_A.addStretch(0)
					hLayout_A.addWidget(self.attrBtn[0])
					hLayout_A.addSpacing(0)
					hLayout_A.addWidget(label)
					hLayout_A.addSpacing(0)
				elif i/3 == 1:
					self.attrBtn.append(QPushButton("Rot"))
					self.attrBtn[1].setCheckable(True)
					self.attrBtn[1].setFixedWidth(40)
					self.attrBtn[1].toggled.connect(self.toggleButtons)
					hLayout_B.addStretch(0)
					hLayout_B.addWidget(self.attrBtn[1])
					hLayout_B.addWidget(label)
				else:
					self.attrBtn.append(QPushButton("Scl"))
					self.attrBtn[2].setCheckable(True)
					self.attrBtn[2].setFixedWidth(40)
					self.attrBtn[2].toggled.connect(self.toggleButtons)
					hLayout_C.addStretch(0)
					hLayout_C.addWidget(self.attrBtn[2])
					hLayout_C.addWidget(label)
			self.vecBtn.append(QPushButton(btnName[i%3]))
			self.vecBtn[i].setFixedWidth(32)
			self.vecBtn[i].setCheckable(True)
			self.vecBtn[i].setStyleSheet("QPushButton{color: %s;font-weight: bold;}"%btnColor[i%3])
			self.vecBtn[i].toggled.connect(self.setFilterCommand)
			if i//3 == 0:
				hLayout_A.addWidget(self.vecBtn[i])
			elif i//3 == 1:
				hLayout_B.addWidget(self.vecBtn[i])
			else:
				hLayout_C.addWidget(self.vecBtn[i])
		
		hLayout_A.addStretch(0)
		hLayout_B.addStretch(0)
		hLayout_C.addStretch(0)
		
		vLayout.setContentsMargins(0, 0, 0, 0)
	
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
		else:
			attr = "scaleZ"
			
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