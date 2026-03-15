"""Qt compatibility helpers for Painter plugin runtimes.

Painter 10.1+ ships with Qt6 / PySide6. The fallback import keeps local tooling
usable when only PySide2 is available outside Painter.
"""

from __future__ import annotations

QT_RUNTIME = "unknown"

try:
    import PySide6 as PySide
    from PySide6 import QtCore, QtGui, QtWidgets

    QT_RUNTIME = "PySide6"
except ImportError:  # pragma: no cover - fallback for older local environments
    import PySide2 as PySide
    from PySide2 import QtCore, QtGui, QtWidgets

    QT_RUNTIME = "PySide2"

__all__ = ["PySide", "QtCore", "QtGui", "QtWidgets", "QT_RUNTIME"]