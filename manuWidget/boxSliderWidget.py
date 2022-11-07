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
		
def openChunk_widget(name):
	cmds.undoInfo(openChunk=True,chunkName = name)
def closeChunk_widget(name):
	cmds.undoInfo(closeChunk=True,chunkName = name)
def undo_widget():
	cmds.undo()
def redo_widget():
	cmds.redo()

class BoxSliderWidget(QWidget):
	valueChanged = Signal(float)
	def __init__(self,parent=None,minRange=-1,maxRange=1,decimals=2,step=0.1):
		super(BoxSliderWidget,self).__init__(parent)
		self.minRange = minRange
		self.maxRange = maxRange
		self.decimals = decimals
		self.step = step
		self.slider = QSlider(Qt.Horizontal,self)
		self.dspinBox = QDoubleSpinBox(self)
		
		self.dspinBox.installEventFilter(self)
		self.slider.installEventFilter(self)
		self.slider.setMouseTracking(True)
		
		self.setFocusPolicy(Qt.StrongFocus)
		
		self.chunkChk = False
		self.funcValueChanged = None
		
		self.thread = None
		
		self.slider_ui()
		self.connect_to_slot()

	def slider_ui(self):
		
		self.sliderSetDefalut()
		self.dspinBox.setKeyboardTracking(False)
		
		self.slider.sliderReleased.connect(self.modeChkFunction)
		self.slider.sliderPressed.connect(self.modeChkFunction)
		
		self.hLayout = QHBoxLayout()
		self.hLayout.setContentsMargins(0, 0, 0, 0)
		
		self.hLayout.addWidget(self.dspinBox)
		self.hLayout.addWidget(self.slider)
		self.setLayout(self.hLayout)
		
	def modeChkFunction(self):
		if QApplication.queryKeyboardModifiers() == Qt.ControlModifier:
			self.sliderSetDetail(10)
		elif QApplication.queryKeyboardModifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
			self.sliderSetDetail(1)
		elif QApplication.queryKeyboardModifiers() == Qt.ShiftModifier:
			self.sliderSetDetail(100)
		else:
			self.sliderSetDefalut()
	
	def sliderSetDefalut(self):
		curValue = self.dspinBox.value()
		
		self.decimals = self.decimals
		self.sliderMinRange = self.minRange * (10**self.decimals)
		self.sliderMaxRange = self.maxRange * (10**self.decimals)
		self.slider.setRange(self.sliderMinRange,self.sliderMaxRange)
		self.dspinBox.setRange(self.minRange,self.maxRange)
		self.dspinBox.setDecimals(self.decimals)
		self.dspinBox.setSingleStep(self.step)
		
		self.slider.setStyleSheet("")
		
		self.dspinBox.setValue(curValue)
		self.slider.setValue(curValue*(10**self.decimals))
			
	
	def sliderSetDetail(self,detail=10):
		curValue = self.dspinBox.value()
		
		self.decimals = self.decimals
		
		editSpinMin = curValue-(self.step*detail)
		editSpinMax = curValue+(self.step*detail)
		
		if editSpinMin < self.minRange:
			editSpinMin = self.minRange
		if editSpinMax > self.maxRange:
			editSpinMax = self.maxRange
		
		editSliderMin = editSpinMin * (10**self.decimals)
		editSliderMax = editSpinMax * (10**self.decimals)
		
		self.dspinBox.setRange(editSpinMin,editSpinMax)
		self.slider.setRange(editSliderMin,editSliderMax)
		
		self.slider.setStyleSheet(
			"QSlider::groove:horizontal{"
				"border:3px groove #4d6b7e; height:8px; margin:2px 0;border-radius:3px;"
				"background:#2b2b2b;}"
			
			"QSlider::handle:horizontal {"
				"border:1px solid #5c5c5c; width:18px; margin:-2px 0;  border-radius:3px;"
				"background:#bdbdbd;}"
		)
		
		self.dspinBox.setValue(curValue)
		self.slider.setValue(curValue*(10**self.decimals))
			
	
	def connect_to_slot(self):
		self.slider.valueChanged[int].connect(self.valueChanged_callBack)
		self.dspinBox.valueChanged.connect(self.valueChanged_callBack)
		
		self.slider.sliderReleased.connect(self.closed_chunk)
		self.valueChanged.connect(self.edit_valueChange)

	def valueChanged_callBack(self,value):
		sender = self.sender()
		if sender == self.slider:
			self.dspinBox.blockSignals(True)
			self.dspinBox.setValue(value / float(10**self.decimals))
			self.dspinBox.blockSignals(False)
		elif sender == self.dspinBox:
			self.slider.blockSignals(True)
			self.slider.setValue(value * float(10**self.decimals))
			self.slider.blockSignals(False)
			
		self.valueChanged.emit(value)
	
	def edit_valueChange(self,value):
		if self.focusWidget() != self.dspinBox:
			self.dspinBox.setFocus()
		if not self.chunkChk:
			openChunk_widget('editBoxSlider')
			self.chunkChk = True
		self.valueChanged_threading(value)
		result = None
		if self.funcValueChanged is not None:
			result = self.funcValueChanged()
		
		return result
		
	def valueChanged_threading(self,value):
		if self.thread:
			self.thread.cancel()
			self.thread = None
		self.thread = threading.Timer(0.3,self.threading_process)
		self.thread.start()
	
	def threading_process(self):
		self.closed_chunk()
		self.thread = None
	
	def closed_chunk(self):
		self.dspinBox.clearFocus()
		if self.chunkChk:
			closeChunk_widget('editBoxSlider')
			self.chunkChk = False
	
	def focusOutEvent(self,event):
		self.closed_chunk()
		
	def eventFilter(self, obj, event):
		if event.type() == QEvent.KeyPress:
			key = event.key()
			mod = event.modifiers()
			if key == Qt.Key_Z and mod == Qt.ShiftModifier:
				self.closed_chunk()
				redo_widget()
			elif key == Qt.Key_Z:
				self.closed_chunk()
				undo_widget()
			else:
				return False
			return True
		
		elif event.type() == QEvent.MouseButtonPress:
			self.modeChkFunction()
			return False
			
		elif event.type() == QEvent.Enter:
			self.modeChkFunction()
			return True
			
		elif event.type() == QEvent.Leave:
			if not self.slider.isSliderDown():
				self.sliderSetDefalut()
			return True
				

		return False