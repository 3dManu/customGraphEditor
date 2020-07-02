#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI

def getSorceObj():
	curveName = cmds.keyframe(q=True,sl=True,name=True)
	obj = []
	if curveName:
		for c in curveName:
			tmplist = get_cnctFstTrgTypObj(c,["network","reference"],["message"],False)
			if tmplist:
				obj.extend(tmplist)
		return list(set(obj))
	return None
	
def get_cnctFstTrgTypObj(node,trgType,extraAttr = None,searchType = False,count = 0,dupNode = None):
	result = []
	extraNode = []
	count = count + 1
	if extraAttr is None:
		extraAttr = []
	if dupNode is None:
		dupNode = []
	
	if count > 50:############### countでループの判断　スクリプトがバグらない処理　これ以上ループが増える前提なら数を増やす
		return None
		
	if extraAttr:
		for ex in extraAttr:
			if cmds.objExists(node+"."+ex):
				tempList = cmds.listConnections(node+"."+ex,s=False,d=True)
				if tempList:
					extraNode.extend(tempList)
		if searchType:
			dests = extraNode
		else:
			dests = cmds.listConnections(node,s=False,d=True)
			dests = list(set(dests) - set(extraNode))
	else:
		dests = cmds.listConnections(node,s=False,d=True)
				
	targets = cmds.ls(dests, tr = True, shapes = True , type = trgType)
	if targets:
		return targets
	elif dests:
		for dest in dests:
			if dest in dupNode:
				continue
			dupNode.append(dest)
			tmplist = get_cnctFstTrgTypObj(dest,trgType,extraAttr,searchType,count,dupNode)
			if tmplist:
				result.extend(tmplist)
			else:
				continue
		return result
	else:
		return [node]
	
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
