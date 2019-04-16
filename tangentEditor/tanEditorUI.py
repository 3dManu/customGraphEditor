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
import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
from . import editTangent
from ..manuWidget import boxSliderWidget as boxSliderWidget
reload(boxSliderWidget)
reload(editTangent)

class EditorUI(QMainWindow):
	def __init__(self,parent=None):
		super(EditorUI,self).__init__(parent)
		self.setWindowFlags(Qt.Window)
		self.resize(400,100)
		
		self.widget = EditorWidget(self)
		self.setCentralWidget(self.widget)
		title = self.widget.windowTitle()
		self.setWindowTitle(title)
	
	def closeEvent(self, e):
		try:
			self.widget.close()
		except:
			pass

class EditorWidget(QWidget):
	def __init__(self,parent=None):
		super(EditorWidget,self).__init__(parent)
		self.setWindowTitle('Curve Editor')
		self.initUI()

	def initUI(self):
		self.widget_t = TanSliderWidget(self)
		self.widget_w = WgtSliderWidget(self)
		layout = QVBoxLayout()
		layout.addWidget(self.widget_t)
		layout.addWidget(self.widget_w)
		self.setLayout(layout)
		
	def closeEvent(self, e):
		try:
			self.widget_t.close()
			self.widget_w.close()
		except:
			pass

class TanSliderWidget(QWidget):
	def __init__(self,parent=None):
		super(TanSliderWidget,self).__init__(parent)
		self.setWindowTitle('Tangent Editor')
		self.initUI()

	def initUI(self):
		self.boxSlider = boxSliderWidget.BoxSliderWidget(self,-90,90)
		self.boxSlider.funcValueChanged = self.changed_editor
		
		# maya上から値を拾っている
		if editTangent.check_animation():
			self.set_ui_value(1)
		else:
			self.boxSlider.slider.setValue(0)
			self.boxSlider.dspinBox.setValue(0)

		#　ラジオボタンとか
		self.radioIo_A = QRadioButton('both',self)
		self.radioIo_A.setChecked(True)
		self.radioIo_B = QRadioButton('in',self)
		self.radioIo_C = QRadioButton('out',self)
		self.radioIoGroup = QButtonGroup()
		self.radioIoGroup.addButton(self.radioIo_A,1)
		self.radioIoGroup.addButton(self.radioIo_B,2)
		self.radioIoGroup.addButton(self.radioIo_C,3)
		
		self.radioIo_A.setFixedWidth(50)
		self.radioIo_B.setFixedWidth(50)
		self.radioIo_C.setFixedWidth(50)

		self.tangentLlabel = QLabel('Tangent :',self)

		self.radioIoGroup.buttonClicked[int].connect(self.set_ui_value)

		# レイアウト決め
		self.vLayout = QVBoxLayout()

		self.hLayout_A = QHBoxLayout()
		self.hLayout_A.addWidget(self.tangentLlabel)
		self.hLayout_A.addWidget(self.radioIo_A)
		self.hLayout_A.addWidget(self.radioIo_B)
		self.hLayout_A.addWidget(self.radioIo_C)
		self.hLayout_A.addStretch()
		self.vLayout.addLayout(self.hLayout_A)

		self.hlayout_b = QHBoxLayout()
		self.hlayout_b.addWidget(self.boxSlider)
		self.vLayout.addLayout(self.hlayout_b)
		self.scriptNo = []
		self.scriptNo.append(cmds.scriptJob(e=["SelectionChanged",self.changed_selection]))
		self.scriptNo.append(cmds.scriptJob(e=["Redo",self.changed_selection]))
		self.scriptNo.append(cmds.scriptJob(e=["Undo",self.changed_selection]))
		self.vLayout.setContentsMargins(0, 0, 0, 0)
		self.vLayout.setSpacing(0)
		self.setLayout(self.vLayout)

	def closeEvent(self, e):
		if self.scriptNo:
			for no in self.scriptNo:
				cmds.scriptJob(k=no)
	
	def changed_editor(self):
		if editTangent.check_animation():
			editTangent.set_angle(self.radioIoGroup.checkedId(),self.boxSlider.dspinBox.value())
	
	def changed_selection(self):
		io = self.radioIoGroup.checkedId()
		self.set_ui_value(io)
		
	def set_ui_value(self,io):
		if editTangent.check_animation():
			self.boxSlider.blockSignals(True)
			self.boxSlider.slider.setValue(editTangent.get_angle(io) * 100)
			self.boxSlider.dspinBox.setValue(editTangent.get_angle(io))
			self.boxSlider.blockSignals(False)
		
class WgtSliderWidget(TanSliderWidget):
	def __init__(self,parent=None):
		super(WgtSliderWidget,self).__init__(parent)
		self.setWindowTitle('Weight Editor')

	def initUI(self):
		self.boxSlider = boxSliderWidget.BoxSliderWidget(self,0,100)
		self.boxSlider.funcValueChanged = self.changed_editor
		
		# maya上から値を拾っている
		if editTangent.check_animation():
			self.set_ui_value(1)
		else:
			self.boxSlider.slider.setValue(0)
			self.boxSlider.dspinBox.setValue(0)

		#　ラジオボタンとか
		self.radioIo_A = QRadioButton('both',self)
		self.radioIo_A.setChecked(True)
		self.radioIo_B = QRadioButton('in',self)
		self.radioIo_C = QRadioButton('out',self)
		self.radioIoGroup = QButtonGroup()
		self.radioIoGroup.addButton(self.radioIo_A,1)
		self.radioIoGroup.addButton(self.radioIo_B,2)
		self.radioIoGroup.addButton(self.radioIo_C,3)
		
		self.radioIo_A.setFixedWidth(50)
		self.radioIo_B.setFixedWidth(50)
		self.radioIo_C.setFixedWidth(50)

		self.weighLlabel = QLabel('Weight :',self)

		self.radioIoGroup.buttonClicked[int].connect(self.set_ui_value)

		self.checkBox = QCheckBox('Weight Tangent',self)
		self.set_weight_checkBox()
		self.checkBox.stateChanged.connect(editTangent.toggle_wieghtTangent)

		# レイアウト決め
		self.vLayout = QVBoxLayout()

		self.hLayout_A = QHBoxLayout()
		self.hLayout_A.addWidget(self.weighLlabel)
		self.hLayout_A.addWidget(self.radioIo_A)
		self.hLayout_A.addWidget(self.radioIo_B)
		self.hLayout_A.addWidget(self.radioIo_C)
		self.hLayout_A.addWidget(self.checkBox)
		self.hLayout_A.addStretch()
		self.vLayout.addLayout(self.hLayout_A)

		self.hlayout_b = QHBoxLayout()
		self.hlayout_b.addWidget(self.boxSlider)
		self.vLayout.addLayout(self.hlayout_b)
		self.scriptNo = []
		self.scriptNo.append(cmds.scriptJob(e=["SelectionChanged",self.changed_selection]))
		self.scriptNo.append(cmds.scriptJob(e=["Redo",self.changed_selection]))
		self.scriptNo.append(cmds.scriptJob(e=["Undo",self.changed_selection]))
		self.vLayout.setContentsMargins(0, 0, 0, 0)
		self.vLayout.setSpacing(0)
		self.setLayout(self.vLayout)
	
	def changed_editor(self):
		if editTangent.check_animation():
			editTangent.set_weight(self.radioIoGroup.checkedId(),self.boxSlider.dspinBox.value())
			
	def changed_selection(self):
		self.set_weight_checkBox()
		io = self.radioIoGroup.checkedId()
		self.set_ui_value(io)

	def set_weight_checkBox(self):
		self.checkBox.blockSignals(True)
		if editTangent.check_animation():
			self.checkBox.setChecked(editTangent.get_weightTangent())
		else:
			self.checkBox.setChecked(False)
		self.checkBox.blockSignals(False)
			
	def set_ui_value(self,io):
		if editTangent.check_animation():
			self.boxSlider.blockSignals(True)
			self.boxSlider.slider.setValue(editTangent.get_weight(io) * 100)
			self.boxSlider.dspinBox.setValue(editTangent.get_weight(io))
			self.boxSlider.blockSignals(False)


def main():
	mayaWindow = 'graphEditor1Window' #常にこのウィンドウより前にいます
	ptr = OpenMayaUI.MQtUtil.findWindow(mayaWindow)
	if ptr is not None:
		parent = wrapInstance(long(ptr),QWidget)
	else:
		cmds.error('Please open the GraphEditor')
	app = QApplication.instance()
	ui = EditorUI(parent)
	ui.show()
	sys.exit()
	app.exec_()

if __name__ == "__main__":
	main()
