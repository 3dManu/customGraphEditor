#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys, os

try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

try:
    from shiboken2 import wrapInstance
except ImportError:
    from shiboken6 import wrapInstance

import json
import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
from . import editTangent
from ..manuWidget import boxSliderWidget as boxSliderWidget


class EditorUI(QMainWindow):
    def __init__(self, parent=None):
        super(EditorUI, self).__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.resize(400, 100)

        self.widget = EditorWidget(self, layoutType=False)
        self.setCentralWidget(self.widget)
        title = self.widget.windowTitle()
        self.setWindowTitle(title)

    def closeEvent(self, e):
        try:
            self.widget.close()
        except:
            pass


class EditorWidget(QWidget):
    def __init__(self, parent=None, layoutType=True):
        super(EditorWidget, self).__init__(parent)
        self.setWindowTitle('Curve Editor')
        self.settingDir = os.path.dirname(__file__) + "\settings"
        self.fileName = "uiSetting.json"
        self.visibleInfo = [True, False, False]
        self.initUI(layoutType)

    def initUI(self, layoutType=True):

        self.widget_s = StrSliderWidget(self, layoutType=layoutType)
        self.widget_s.setObjectName("StrSliderWidget")
        self.widget_t = TanSliderWidget(self, layoutType=layoutType)
        self.widget_t.setObjectName("TanSliderWidget")
        self.widget_w = WgtSliderWidget(self, layoutType=layoutType)
        self.widget_w.setObjectName("WgtSliderWidget")
        if layoutType:
            layout = QHBoxLayout()
            self.setFixedHeight(50)
        else:
            layout = QVBoxLayout()
            self.setFixedWidth(60)

        layout.addWidget(self.widget_s)
        layout.addWidget(self.widget_t)
        layout.addWidget(self.widget_w)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self.scriptNo = []
        self.scriptNo.append(cmds.scriptJob(e=["SelectionChanged", self.changed_selection]))
        self.scriptNo.append(cmds.scriptJob(e=["Redo", self.changed_selection]))
        self.scriptNo.append(cmds.scriptJob(e=["Undo", self.changed_selection]))

        self.widget_s.strainButton.clicked.connect(self.hideTangentWidget)
        self.widget_t.tangentButton.clicked.connect(self.hideTangentWidget)
        self.widget_w.weighButton.clicked.connect(self.hideTangentWidget)

        self.loadSettings()

    def closeEvent(self, e):
        self.saveSettings()
        if self.scriptNo:
            for no in self.scriptNo:
                cmds.scriptJob(k=no)
        try:
            self.widget_t.close()
            self.widget_w.close()
            self.widget_s.close()
        except:
            pass

    def loadSettings(self):
        if os.path.isfile(self.settingDir + "\\" + self.fileName):
            with open(self.settingDir + "\\" + self.fileName, "r") as f:
                settings = json.load(f)
            self.widget_s.setVisible(settings.get(self.widget_s.objectName()).get("isVisible"))
            self.widget_t.setVisible(settings.get(self.widget_t.objectName()).get("isVisible"))
            self.widget_w.setVisible(settings.get(self.widget_w.objectName()).get("isVisible"))
        else:
            self.widget_s.setVisible(True)
            self.widget_t.setVisible(False)
            self.widget_w.setVisible(False)

    def saveSettings(self):
        settings = dict()
        settings[self.widget_s.objectName()] = {"isVisible": self.visibleInfo[0]}
        settings[self.widget_t.objectName()] = {"isVisible": self.visibleInfo[1]}
        settings[self.widget_w.objectName()] = {"isVisible": self.visibleInfo[2]}
        if not os.path.exists(self.settingDir):
            os.makedirs(self.settingDir)
        with open(self.settingDir + "\\" + self.fileName, "w") as f:
            json.dump(settings, f, ensure_ascii=False)

    def changed_selection(self):
        self.widget_s.changed_selection()
        self.widget_t.changed_selection()
        self.widget_w.changed_selection()

    def hideTangentWidget(self):
        sender = self.sender()
        if sender == self.widget_t.tangentButton:
            self.widget_s.setVisible(False)
            self.widget_t.setVisible(False)
            self.widget_w.setVisible(True)
            self.visibleInfo = [False, False, True]
        elif sender == self.widget_s.strainButton:
            self.widget_s.setVisible(False)
            self.widget_t.setVisible(True)
            self.widget_w.setVisible(False)
            self.visibleInfo = [False, True, False]
        else:
            self.widget_s.setVisible(True)
            self.widget_t.setVisible(False)
            self.widget_w.setVisible(False)
            self.visibleInfo = [True, False, False]


class TanSliderWidget(QWidget):
    def __init__(self, parent=None, layoutType=True):
        super(TanSliderWidget, self).__init__(parent)
        self.setWindowTitle('Tangent Editor')
        self.initUI(layoutType)

    def initUI(self, layoutType):
        self.boxSlider = boxSliderWidget.BoxSliderWidget(self, -90, 90, layoutType=layoutType)
        self.boxSlider.funcValueChanged = self.changed_editor

        #　ラジオボタンとか
        self.radioIo_A = QRadioButton('B', self)
        self.radioIo_A.setChecked(True)
        self.radioIo_B = QRadioButton('I', self)
        self.radioIo_C = QRadioButton('O', self)
        self.radioIoGroup = QButtonGroup()
        self.radioIoGroup.addButton(self.radioIo_A, 1)
        self.radioIoGroup.addButton(self.radioIo_B, 2)
        self.radioIoGroup.addButton(self.radioIo_C, 3)

        # maya上から値を拾っている
        if editTangent.check_animation():
            self.set_ui_value(self.radioIo_A)
        else:
            self.boxSlider.slider.setValue(0)
            self.boxSlider.dspinBox.setValue(0)

        self.radioIo_A.setFixedWidth(28)
        self.radioIo_B.setFixedWidth(28)
        self.radioIo_C.setFixedWidth(28)

        self.tangentButton = QPushButton('Tangent', self)

        self.selButton = QPushButton(self)
        self.ioButton = QPushButton(self)

        self.selButton.clicked.connect(self.sender_command)
        self.ioButton.clicked.connect(self.sender_command)

        self.radioIoGroup.buttonClicked.connect(self.set_ui_value)

        # レイアウト決め
        if layoutType:
            self.mainLay = QVBoxLayout()
            self.subLay_a = QHBoxLayout()
            self.tangentButton.setFixedWidth(64)
            self.mainLay.setSpacing(4)
            self.boxSlider.dspinBox.setFixedWidth(64)
        else:
            self.mainLay = QHBoxLayout()
            self.subLay_a = QVBoxLayout()
            self.tangentButton.setText("T")
            self.tangentButton.setFixedWidth(24)
            self.mainLay.setSpacing(0)
            self.boxSlider.dspinBox.editArrows()

        self.subLay_a.addWidget(self.tangentButton)
        self.subLay_a.addSpacing(4)
        self.subLay_a.addWidget(self.radioIo_A)
        self.subLay_a.addWidget(self.radioIo_B)
        self.subLay_a.addWidget(self.radioIo_C)
        self.subLay_a.addSpacing(8)

        self.subLay_a.addWidget(self.selButton)
        self.subLay_a.addSpacing(4)
        self.subLay_a.addWidget(self.ioButton)
        self.subLay_a.addStretch()

        self.subLay_a.setContentsMargins(0, 0, 0, 0)

        self.mainLay.addLayout(self.subLay_a)

        self.mainLay.addWidget(self.boxSlider)

        self.mainLay.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLay)

        self.set_style_button()

    def sender_command(self):
        sender = self.sender()
        if sender == self.selButton:
            editTangent.set_angle_selected()
        elif sender == self.ioButton:
            editTangent.set_angle_io()

        self.changed_selection()

    def set_style_button(self):
        icon_path = os.path.join(os.path.dirname(__file__), r'..\icons')

        autoTanIcon = QIcon(icon_path + '\\customGraphEditor_autoTangent_Icon.png')
        ioTanIcon = QIcon(icon_path + '\\customGraphEditor_ioTangent_Icon.png')

        self.selButton.setIcon(autoTanIcon)
        self.ioButton.setIcon(ioTanIcon)

        self.selButton.setFlat(True)
        self.ioButton.setFlat(True)

        self.selButton.setStyleSheet(
            "QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.ioButton.setStyleSheet(
            "QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")

        iconSize = QSize(24, 24)

        self.selButton.setIconSize(iconSize)
        self.ioButton.setIconSize(iconSize)

        self.selButton.setFixedSize(iconSize)
        self.ioButton.setFixedSize(iconSize)

    def changed_editor(self):
        if editTangent.check_animation():
            editTangent.set_angle(self.radioIoGroup.checkedId(), self.boxSlider.dspinBox.value())

    def changed_selection(self):
        button = self.radioIoGroup.checkedButton()
        self.set_ui_value(button)

    def set_ui_value(self, button):
        button_id = self.radioIoGroup.id(button)
        if editTangent.check_animation():
            self.boxSlider.blockSignals(True)
            self.boxSlider.slider.setValue(editTangent.get_angle(button_id) * 100)
            self.boxSlider.dspinBox.setValue(editTangent.get_angle(button_id))
            self.boxSlider.blockSignals(False)
        else:
            self.boxSlider.blockSignals(True)
            self.boxSlider.slider.setValue(0)
            self.boxSlider.dspinBox.setValue(0)
            self.boxSlider.blockSignals(False)


class StrSliderWidget(QWidget):
    def __init__(self, parent=None, layoutType=True):
        super(StrSliderWidget, self).__init__(parent)
        self.setWindowTitle('Strain Editor')
        self.initUI(layoutType)

    def initUI(self, layoutType):
        self.boxSlider = boxSliderWidget.BoxSliderWidget(self, 0, 100, layoutType=layoutType)
        self.boxSlider.funcValueChanged = self.changed_editor

        #　ラジオボタンとか
        self.radioIo_A = QRadioButton('B', self)
        self.radioIo_A.setChecked(True)
        self.radioIo_B = QRadioButton('I', self)
        self.radioIo_C = QRadioButton('O', self)
        self.radioIoGroup = QButtonGroup()
        self.radioIoGroup.addButton(self.radioIo_A, 1)
        self.radioIoGroup.addButton(self.radioIo_B, 2)
        self.radioIoGroup.addButton(self.radioIo_C, 3)

        # maya上から値を拾っている
        if editTangent.check_animation():
            self.set_ui_value(self.radioIo_A)
        else:
            self.boxSlider.slider.setValue(0)
            self.boxSlider.dspinBox.setValue(0)

        self.radioIo_A.setFixedWidth(28)
        self.radioIo_B.setFixedWidth(28)
        self.radioIo_C.setFixedWidth(28)

        self.strainButton = QPushButton('Strain', self)

        self.selButton = QPushButton(self)
        self.ioButton = QPushButton(self)

        self.selButton.clicked.connect(self.sender_command)
        self.ioButton.clicked.connect(self.sender_command)

        self.radioIoGroup.buttonClicked.connect(self.set_ui_value)

        # レイアウト決め
        if layoutType:
            self.mainLay = QVBoxLayout()
            self.subLay_a = QHBoxLayout()
            self.strainButton.setFixedWidth(64)
            self.mainLay.setSpacing(4)
            self.boxSlider.dspinBox.setFixedWidth(64)
        else:
            self.mainLay = QHBoxLayout()
            self.subLay_a = QVBoxLayout()
            self.strainButton.setText("S")
            self.strainButton.setFixedWidth(24)
            self.mainLay.setSpacing(0)
            self.boxSlider.dspinBox.editArrows()

        self.subLay_a.addWidget(self.strainButton)
        self.subLay_a.addSpacing(4)
        self.subLay_a.addWidget(self.radioIo_A)
        self.subLay_a.addWidget(self.radioIo_B)
        self.subLay_a.addWidget(self.radioIo_C)
        self.subLay_a.addSpacing(8)

        self.subLay_a.addWidget(self.selButton)
        self.subLay_a.addSpacing(4)
        self.subLay_a.addWidget(self.ioButton)
        self.subLay_a.addStretch()

        self.subLay_a.setContentsMargins(0, 0, 0, 0)

        self.mainLay.addLayout(self.subLay_a)

        self.mainLay.addWidget(self.boxSlider)

        self.mainLay.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLay)

        self.set_style_button()

    def sender_command(self):
        sender = self.sender()
        if sender == self.selButton:
            editTangent.set_angle_selected()
        elif sender == self.ioButton:
            editTangent.set_angle_io()
        self.set_ui_value(None)

    def set_style_button(self):
        icon_path = os.path.join(os.path.dirname(__file__), r'..\icons')

        autoTanIcon = QIcon(icon_path + '\\customGraphEditor_autoTangent_Icon.png')
        ioTanIcon = QIcon(icon_path + '\\customGraphEditor_ioTangent_Icon.png')

        self.selButton.setIcon(autoTanIcon)
        self.ioButton.setIcon(ioTanIcon)

        self.selButton.setFlat(True)
        self.ioButton.setFlat(True)

        self.selButton.setStyleSheet(
            "QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")
        self.ioButton.setStyleSheet(
            "QPushButton:hover{background-color: #575757;border: none;}QPushButton:pressed{background-color: black;}")

        iconSize = QSize(24, 24)

        self.selButton.setIconSize(iconSize)
        self.ioButton.setIconSize(iconSize)

        self.selButton.setFixedSize(iconSize)
        self.ioButton.setFixedSize(iconSize)

    def changed_editor(self):
        if editTangent.check_animation():
            editTangent.set_angle_strain(self.radioIoGroup.checkedId(), self.boxSlider.dspinBox.value())

    def changed_selection(self):
        self.set_ui_value(self.radioIo_A)

    def set_ui_value(self, button):
        if button is not None:
            value = 0
        else:
            value = 49
            # value = math.sqrt((1.5 - 0.2)/0.0005) = 48.99
        self.boxSlider.blockSignals(True)
        self.boxSlider.slider.setValue(value)
        self.boxSlider.dspinBox.setValue(value)
        self.boxSlider.blockSignals(False)


class WgtSliderWidget(QWidget):
    def __init__(self, parent=None, layoutType=True):
        super(WgtSliderWidget, self).__init__(parent)
        self.setWindowTitle('Weight Editor')
        self.initUI(layoutType)

    def initUI(self, layoutType):
        self.boxSlider = boxSliderWidget.BoxSliderWidget(self, 0, 100, layoutType=layoutType)
        self.boxSlider.funcValueChanged = self.changed_editor

        # #　ラジオボタンとか
        self.radioIo_A = QRadioButton('B', self)
        self.radioIo_A.setChecked(True)
        self.radioIo_B = QRadioButton('I', self)
        self.radioIo_C = QRadioButton('O', self)
        self.radioIoGroup = QButtonGroup()
        self.radioIoGroup.addButton(self.radioIo_A, 1)
        self.radioIoGroup.addButton(self.radioIo_B, 2)
        self.radioIoGroup.addButton(self.radioIo_C, 3)

        # maya上から値を拾っている
        if editTangent.check_animation():
            self.set_ui_value(self.radioIo_A)
        else:
            self.boxSlider.slider.setValue(0)
            self.boxSlider.dspinBox.setValue(0)

        self.radioIo_A.setFixedWidth(28)
        self.radioIo_B.setFixedWidth(28)
        self.radioIo_C.setFixedWidth(28)

        self.weighButton = QPushButton('Weight', self)

        self.radioIoGroup.buttonClicked.connect(self.set_ui_value)

        self.checkBox = QCheckBox('W', self)
        self.set_weight_checkBox()
        self.checkBox.stateChanged.connect(editTangent.toggle_wieghtTangent)

        # レイアウト決め
        if layoutType:
            self.mainLay = QVBoxLayout()
            self.subLay_a = QHBoxLayout()
            self.weighButton.setFixedWidth(64)
            self.mainLay.setSpacing(4)
            self.boxSlider.dspinBox.setFixedWidth(64)
        else:
            self.mainLay = QHBoxLayout()
            self.subLay_a = QVBoxLayout()
            self.weighButton.setText("W")
            self.weighButton.setFixedWidth(24)
            self.mainLay.setSpacing(0)
            self.boxSlider.dspinBox.editArrows()

        self.subLay_a.addWidget(self.weighButton)
        self.subLay_a.addSpacing(4)
        self.subLay_a.addWidget(self.radioIo_A)
        self.subLay_a.addWidget(self.radioIo_B)
        self.subLay_a.addWidget(self.radioIo_C)
        self.subLay_a.addWidget(self.checkBox)
        self.subLay_a.addStretch()

        self.mainLay.addLayout(self.subLay_a)

        self.mainLay.addWidget(self.boxSlider)

        self.mainLay.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLay)

    def changed_editor(self):
        if editTangent.check_animation():
            editTangent.set_weight(self.radioIoGroup.checkedId(), self.boxSlider.dspinBox.value())

    def changed_selection(self):
        self.set_weight_checkBox()
        button = self.radioIoGroup.checkedButton()
        self.set_ui_value(button)

    def set_weight_checkBox(self):
        self.checkBox.blockSignals(True)
        if editTangent.check_animation():
            self.checkBox.setChecked(editTangent.get_weightTangent())
        else:
            self.checkBox.setChecked(False)
        self.checkBox.blockSignals(False)

    def set_ui_value(self, button):
        button_id = self.radioIoGroup.id(button)
        if editTangent.check_animation():
            self.boxSlider.blockSignals(True)
            self.boxSlider.slider.setValue(editTangent.get_weight(button_id) * 100)
            self.boxSlider.dspinBox.setValue(editTangent.get_weight(button_id))
            self.boxSlider.blockSignals(False)
        else:
            self.boxSlider.blockSignals(True)
            self.boxSlider.slider.setValue(0)
            self.boxSlider.dspinBox.setValue(0)
            self.boxSlider.blockSignals(False)


def main():
    mayaWindow = 'graphEditor1Window'  # 常にこのウィンドウより前にいます
    ptr = OpenMayaUI.MQtUtil.findWindow(mayaWindow)
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr is not None:
        parent = wrapInstance(int(ptr), QWidget)
    else:
        cmds.error('Please open the GraphEditor')
    app = QApplication.instance()
    ui = EditorUI(parent)
    ui.show()
    sys.exit()
    app.exec_()


if __name__ == "__main__":
    main()
