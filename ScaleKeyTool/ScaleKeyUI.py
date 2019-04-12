#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
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
import maya.OpenMayaUI as omui
from . import ScaleKeyWidget
reload(ScaleKeyWidget)

class ScaleKeyUI(QWidget):
	def __init__(self,parent=None):
		super(ScaleKeyUI,self).__init__(parent)
		self.resize(250,70)
		#self.setFixedSize(250,70)
		self.setWindowFlags(Qt.Widget)
		self.setWindowTitle('Keys Sacale Window')
		self.initUI()

	def initUI(self):
		self.dspinBox = QDoubleSpinBox()
		self.dspinBox.setDecimals(2)
		self.dspinBox.setSingleStep(0.1)
		self.dspinBox.setValue(1)
		self.dspinBox.setFixedWidth(50)
		self.dspinBox.setFixedHeight(30)
		#self.dspinBox.setButtonSymbols(QAbstractSpinBox.NoButtons)
		
		self.upBtn = QToolButton(self)
		self.upBtn.setArrowType(Qt.UpArrow)
		self.leftBtn = QToolButton(self)
		self.leftBtn.setArrowType(Qt.LeftArrow)
		self.rightBtn = QToolButton(self)
		self.rightBtn.setArrowType(Qt.RightArrow)
		self.downBtn = QToolButton(self)
		self.downBtn.setArrowType(Qt.DownArrow)
		
		btnw = 30
		btnh = 30
		
		self.upBtn.setFixedWidth(btnw)
		self.upBtn.setFixedHeight(btnh)
		self.leftBtn.setFixedWidth(btnw)
		self.leftBtn.setFixedHeight(btnh)
		self.rightBtn.setFixedWidth(btnw)
		self.rightBtn.setFixedHeight(btnh)
		self.downBtn.setFixedWidth(btnw)
		self.downBtn.setFixedHeight(btnh)
		
		self.upBtn.clicked.connect(self.scaleWidget_signal)
		self.leftBtn.clicked.connect(self.scaleWidget_signal)
		self.rightBtn.clicked.connect(self.scaleWidget_signal)
		self.downBtn.clicked.connect(self.scaleWidget_signal)
		
		
		self.timeDspinBox = QDoubleSpinBox()
		self.timeDspinBox.setDecimals(2)
		self.timeDspinBox.setSingleStep(1)
		self.timeDspinBox.setValue(0)
		self.timeDspinBox.setFixedWidth(60)
		self.timeDspinBox.setMaximum(99999999)
		self.timeDspinBox.setMinimum(-99999999)
		#self.timeDspinBox.setButtonSymbols(QAbstractSpinBox.NoButtons)
		
		self.valueDspinBox = QDoubleSpinBox()
		self.valueDspinBox.setDecimals(4)
		self.valueDspinBox.setSingleStep(0.1)
		self.valueDspinBox.setValue(0)
		self.valueDspinBox.setFixedWidth(60)
		self.valueDspinBox.setMaximum(99999999)
		self.valueDspinBox.setMinimum(-99999999)
		#self.valueDspinBox.setButtonSymbols(QAbstractSpinBox.NoButtons)
		
		self.timeLabel = QLabel("Time:",self)
		self.valueLabel = QLabel("Value:",self)
		
		self.getBtn = QPushButton("Get Pivot",self)
		self.getBtn.clicked.connect(self.get_pivotKey)
		
		self.avrBtn = QPushButton("Average Reverse",self)
		self.avrBtn.clicked.connect(self.scaleWidget_signal)
		
		# レイアウト決め
		self.vLayout_A = QVBoxLayout(self)
		
		self.hLayout_A = QHBoxLayout(self)
		
		self.vLayout_B = QVBoxLayout(self)
		self.vLayout_C = QVBoxLayout(self)
		
		self.hLayout_B = QHBoxLayout(self)
		self.hLayout_B.addWidget(self.upBtn)
		
		self.hLayout_C = QHBoxLayout(self)
		self.hLayout_C.setSpacing(7)
		self.hLayout_C.addWidget(self.leftBtn,alignment=(Qt.AlignVCenter | Qt.AlignRight))
		self.hLayout_C.setSpacing(0)
		self.hLayout_C.addWidget(self.dspinBox)
		self.hLayout_C.setSpacing(5)
		self.hLayout_C.addWidget(self.rightBtn,alignment=(Qt.AlignVCenter | Qt.AlignLeft))
		
		self.hLayout_D = QHBoxLayout(self)
		self.hLayout_D.addWidget(self.downBtn)
		
		self.hLayout_E = QHBoxLayout(self)
		self.hLayout_E.addWidget(self.timeLabel,alignment=(Qt.AlignVCenter | Qt.AlignRight))
		self.hLayout_E.addWidget(self.timeDspinBox)
		
		self.hLayout_F = QHBoxLayout(self)
		self.hLayout_F.addWidget(self.valueLabel,alignment=(Qt.AlignVCenter | Qt.AlignRight))
		self.hLayout_F.addWidget(self.valueDspinBox)
		
		self.hLayout_G = QHBoxLayout(self)
		self.hLayout_G.addWidget(self.getBtn)
		
		self.hLayout_H = QHBoxLayout(self)
		self.hLayout_H.addWidget(self.avrBtn)
		
		self.vLayout_B.addLayout(self.hLayout_B)
		self.vLayout_B.addLayout(self.hLayout_C)
		self.vLayout_B.addLayout(self.hLayout_D)
		
		self.vLayout_C.addLayout(self.hLayout_E)
		self.vLayout_C.addLayout(self.hLayout_F)
		self.vLayout_C.addLayout(self.hLayout_G)
		self.vLayout_C.addLayout(self.hLayout_H)
		
		self.hLayout_A.addLayout(self.vLayout_C)
		self.hLayout_A.addLayout(self.vLayout_B)
		
		self.vLayout_A.addLayout(self.hLayout_A)

		self.setLayout(self.vLayout_A)
	
	def scaleWidget_signal(self):
		sender = self.sender()
		value = self.dspinBox.value()
		pivTime = self.timeDspinBox.value()
		pivValue = self.valueDspinBox.value()
		if sender == self.upBtn:
			ScaleKeyWidget.scaleKeys("up",value,pivTime,pivValue)
		elif sender == self.downBtn:
			ScaleKeyWidget.scaleKeys("down",value,pivTime,pivValue)
		elif sender == self.leftBtn:
			ScaleKeyWidget.scaleKeys("left",value,pivTime,pivValue)
		elif sender == self.rightBtn:
			ScaleKeyWidget.scaleKeys("right",value,pivTime,pivValue)
		elif sender == self.avrBtn:
			ScaleKeyWidget.scaleKeys("avr",value,pivTime,pivValue)
		else:
			pass
	
	def get_pivotKey(self):
		time,value = ScaleKeyWidget.getKeyValue()
		self.timeDspinBox.setValue(time)
		self.valueDspinBox.setValue(value)
		
def main():
	mayaWindow = 'graphEditor1Window' #常にこのウィンドウより前にいます
	ptr = omui.MQtUtil.findWindow(mayaWindow)
	if ptr is None:
		ptr = omui.MQtUtil.mainWindow()
	parent = wrapInstance(long(ptr),QWidget)
	app = QApplication.instance()
	ui = ScaleKeyUI(parent)
	ui.show()
	sys.exit()
	app.exec_()

if __name__ == "__main__":
	main()	