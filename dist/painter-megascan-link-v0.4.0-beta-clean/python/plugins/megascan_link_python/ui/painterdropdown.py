from ..qt_compat import QtCore, QtGui, QtWidgets
from . import icon
import os


class PainterDropDown(QtWidgets.QPushButton):
    """Custom QPushButton widget that emulates the Painter dropdown look."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._currvalue = None
        self._menu = QtWidgets.QMenu(self)
        self._menu.setFixedWidth(self.width())
        self._menu.setStyleSheet("QMenu::item { max-height: 12px; margin: -2px; border: 3px solid #4d4d4d; padding-left:3px; }")
        self._menu.aboutToShow.connect(self._setMenuSize)
        self.setMenu(self._menu)
        self.clearFocus()
        self.setStyleSheet(
            """QPushButton {
                    background: #262626;
                    height: 12px;
                    border: 1px solid #4d4d4d;
                }
                QPushButton:hover {
                    background: #1a1a1a;
                }
                QPushButton::menu-indicator {
                    image: url(%s);
                    subcontrol-position: right center;
                    subcontrol-origin: padding;
                    left: -2px;
                }""" % (icon.getIcon("dropdown_icon.png").replace(os.sep, "/"))
        )

    def getValue(self):
        return self._currvalue

    def setSelectedByData(self, data):
        for action in self._menu.actions():
            if action.data() == data:
                action.trigger()

    def setSelectedByText(self, text):
        for action in self._menu.actions():
            if action.text() == text:
                action.trigger()

    def _onMenuActionTrigger(self):
        action = self.sender()
        self.setText(action.text())
        self._currvalue = action.data()

    def setOptions(self, options):
        self._menu.clear()
        for opt in options:
            if not isinstance(opt, (list, tuple)):
                opt = [opt, opt]
            action = QtGui.QAction(opt[0], parent=self)
            action.setData(opt[1])
            action.triggered.connect(self._onMenuActionTrigger)
            self._menu.addAction(action)

    def _setMenuSize(self):
        self._menu.setFixedWidth(self.width())
