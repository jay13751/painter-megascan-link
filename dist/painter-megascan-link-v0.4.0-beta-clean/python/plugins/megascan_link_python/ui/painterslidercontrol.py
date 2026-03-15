from ..qt_compat import QtCore, QtGui, QtWidgets
from . import painterslider, painterlineedit


class PainterSliderControl(QtWidgets.QWidget):
    def __init__(self, parent):
        self.currvalue = 0.0
        super().__init__(parent=parent)
        self.slider = painterslider.PainterSlider(self)
        self.slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.lineEdit = painterlineedit.PainterLineEdit(parent=self)
        self.lineEdit.setValidator(QtGui.QDoubleValidator())
        self.lineEdit.setFixedWidth(50)
        self.lineEdit.setFixedHeight(16)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.addWidget(self.slider)
        hlayout.addWidget(self.lineEdit)
        self.setLayout(hlayout)
        self.lineEdit.textEdited.connect(self._linkEditValue)
        self.slider.sliderMoved.connect(self._linkSliderValue)

    def _linkSliderValue(self, value: int):
        self.currvalue = float('%.3f' % (max(float(value) / 100.0 + 0.01, 0.0)))
        self.lineEdit.setText(str(self.currvalue))

    def _linkEditValue(self, value: str):
        if value == "":
            value = 0.0
        self.currvalue = max(float(value), 0.0)
        self.slider.setValue(int(self.currvalue * 100.0))

    def setValue(self, value: float):
        self.currvalue = value
        self.lineEdit.setText(str(self.currvalue))
        self.slider.setValue(int(self.currvalue * 100.0))

    def getValue(self) -> float:
        return self.currvalue

    def setDisabled(self, state: bool):
        self.lineEdit.setDisabled(state)
        self.slider.setDisabled(state)
