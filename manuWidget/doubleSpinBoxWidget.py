try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

class DoubleSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super(DoubleSpinBox, self).__init__(parent)
    
    def valueFromText(self, text):
        ok = False
        ok = value = self.locale().toDouble(text)
        if ok:
            return value[0]
        else:
            return super(DoubleSpinBox, self).valueFromText(text)
    
    def validate(self, text, pos):
        ok = False
        ok = self.locale().toDouble(text)
        if ok:
            return QValidator.Acceptable
        else:
            return QValidator.Invalid
            
    def editArrows(self):
        self.setAlignment(Qt.AlignLeft)
        self.setFixedSize(24,42)
        self.setStyleSheet(
            """
            QDoubleSpinBox::down-button,QDoubleSpinBox::up-button {
                width: 24px;
                height: 12px;
            }
            
            QDoubleSpinBox::up-button {
                subcontrol-position: top center;
            }
            
            QDoubleSpinBox::down-button {
                subcontrol-position: bottom center;
            }
            """
        )