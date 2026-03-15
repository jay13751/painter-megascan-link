"""Module containing classes for using and retrieving icon files."""

import os

from ..qt_compat import QtCore, QtGui


def getIcon(name: str) -> str:
    return os.path.join(os.path.abspath(os.path.split(__file__)[0]), name)


def getIconAsQPixmap(name: str, scale: int = None) -> QtGui.QPixmap:
    if scale:
        return QtGui.QPixmap(getIcon(name)).scaled(
            scale,
            scale,
            QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
    return QtGui.QPixmap(getIcon(name))
