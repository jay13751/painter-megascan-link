"""Module containing classes for the plugin dialogs."""

from __future__ import annotations

import importlib
import logging
import webbrowser

from . import config, log, sockets
from .qt_compat import QtCore, QtGui, QtWidgets
from .ui import error_dialog, icon, painterslider, settings_dialog

importlib.reload(settings_dialog)
importlib.reload(painterslider)
importlib.reload(error_dialog)

Qt = QtCore.Qt


class SettingsDialog(QtWidgets.QDialog, settings_dialog.Ui_Dialog):
    def __init__(self, socket: sockets.SocketThread, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self._socketRef = socket
        self.needRestart = False
        self._extendUi()
        self._loadSettings()
        self._wireSignals()

    def _extendUi(self):
        self.helpIcon.setPixmap(icon.getIconAsQPixmap("help_icon.png", 24))
        self.debugPayload = QtWidgets.QCheckBox("Log raw payloads", self.groupBox)
        self.ignoreOptional = QtWidgets.QCheckBox("Ignore missing optional fields", self.groupBox)
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.debugPayload)
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.ignoreOptional)

    def _loadSettings(self):
        self.portNumber.setText(config.ConfigSettings.getConfigSetting("Connection", "port"))
        self.portNumber.setValidator(QtGui.QIntValidator(self))
        self.timeoutNumber.setText(config.ConfigSettings.getConfigSetting("Connection", "timeout"))
        self.timeoutNumber.setValidator(QtGui.QIntValidator(0, 60, self))
        self.askforproj.setCheckState(Qt.CheckState.Unchecked if config.ConfigSettings.checkIfOptionIsSet("General", "askcreateproject") else Qt.CheckState.Checked)
        self.logtoconsole.setCheckState(Qt.CheckState.Checked if config.ConfigSettings.checkIfOptionIsSet("General", "outputConsole") else Qt.CheckState.Unchecked)
        self.selectafterimport.setCheckState(Qt.CheckState.Checked if config.ConfigSettings.checkIfOptionIsSet("General", "selectafterimport") else Qt.CheckState.Unchecked)
        self.debugPayload.setCheckState(Qt.CheckState.Checked if config.ConfigSettings.checkIfOptionIsSet("General", "debug_payload_logging") else Qt.CheckState.Unchecked)
        self.ignoreOptional.setCheckState(Qt.CheckState.Checked if config.ConfigSettings.checkIfOptionIsSet("General", "ignore_missing_optional_fields", "true") else Qt.CheckState.Unchecked)
        self._setControlsStateOfWidget(self.bakeParametersGroup, config.ConfigSettings.checkIfOptionIsSet("Bake", "enabled"))
        self.aliasingValue.setOptions(["None", "Subsampling 2x2", "Subsampling 4x4", "Subsampling 8x8"])
        self.aliasingValue.setSelectedByData(config.ConfigSettings.getConfigSetting("Bake", "antialiasing"))
        self.texSize.setOptions([["128", "[7,7]"], ["256", "[8,8]"], ["512", "[9,9]"], ["1024", "[10,10]"], ["2048", "[11,11]"], ["4096", "[12,12]"], ["8192", "[13,13]"]])
        self.enableBaking.setCheckState(Qt.CheckState.Checked if config.ConfigSettings.checkIfOptionIsSet("Bake", "enabled") else Qt.CheckState.Unchecked)
        self.texSize.setSelectedByData(config.ConfigSettings.getConfigSetting("Bake", "resolution"))
        self.maxRearDistanceSlider.setValue(float(config.ConfigSettings.getConfigSetting("Bake", "maxreardistance")))
        self.maxFrontalDistanceSlider.setValue(float(config.ConfigSettings.getConfigSetting("Bake", "maxfrontaldistance")))
        self.averageNormalsCheckBox.setCheckState(Qt.CheckState.Checked if config.ConfigSettings.checkIfOptionIsSet("Bake", "average") else Qt.CheckState.Unchecked)
        self.ignoreBackfaceCheckBox.setCheckState(Qt.CheckState.Checked if config.ConfigSettings.checkIfOptionIsSet("Bake", "ignorebackface") else Qt.CheckState.Unchecked)
        self.relativeToBoundingBoxCheckBox.setCheckState(Qt.CheckState.Checked if config.ConfigSettings.checkIfOptionIsSet("Bake", "relative") else Qt.CheckState.Unchecked)

    def _wireSignals(self):
        self.portNumber.textChanged.connect(self._setNeedRestart)
        self.timeoutNumber.textChanged.connect(self._setNeedRestart)
        self.saveBtn.pressed.connect(self._saveSettings)
        self.cancelBtn.pressed.connect(self.close)
        self.enableBaking.stateChanged.connect(self._enableBakeChanged)

    def _enableBakeChanged(self, value):
        self._setControlsStateOfWidget(self.bakeParametersGroup, bool(value))

    def _setControlsStateOfWidget(self, widget: QtCore.QObject, state: bool):
        for paramControl in widget.findChildren(QtWidgets.QWidget):
            paramControl.setDisabled(not state)

    def _setNeedRestart(self, *_args):
        self.needRestart = True
        log.LoggerLink.Log("Changed socket settings; restart required", logging.DEBUG)

    def _is_checked(self, checkbox: QtWidgets.QCheckBox) -> bool:
        return checkbox.checkState() == Qt.CheckState.Checked

    def _saveSettings(self):
        config.ConfigSettings.updateConfigSetting("Connection", "port", self.portNumber.text(), False)
        config.ConfigSettings.updateConfigSetting("Connection", "timeout", self.timeoutNumber.text(), False)
        config.ConfigSettings.updateConfigSetting("Connection", "source", "fab", False)
        config.ConfigSettings.updateConfigSetting("General", "outputConsole", self._is_checked(self.logtoconsole), False)
        config.ConfigSettings.updateConfigSetting("General", "askcreateproject", not self._is_checked(self.askforproj), False)
        config.ConfigSettings.updateConfigSetting("General", "selectafterimport", self._is_checked(self.selectafterimport), False)
        config.ConfigSettings.updateConfigSetting("General", "debug_payload_logging", self._is_checked(self.debugPayload), False)
        config.ConfigSettings.updateConfigSetting("General", "ignore_missing_optional_fields", self._is_checked(self.ignoreOptional), False)
        config.ConfigSettings.updateConfigSetting("Bake", "enabled", self._is_checked(self.enableBaking), False)
        config.ConfigSettings.updateConfigSetting("Bake", "relative", self._is_checked(self.relativeToBoundingBoxCheckBox), False)
        config.ConfigSettings.updateConfigSetting("Bake", "average", self._is_checked(self.averageNormalsCheckBox), False)
        config.ConfigSettings.updateConfigSetting("Bake", "ignorebackface", self._is_checked(self.ignoreBackfaceCheckBox), False)
        config.ConfigSettings.updateConfigSetting("Bake", "resolution", self.texSize.getValue(), False)
        config.ConfigSettings.updateConfigSetting("Bake", "maxfrontaldistance", self.maxFrontalDistanceSlider.getValue(), False)
        config.ConfigSettings.updateConfigSetting("Bake", "maxreardistance", self.maxRearDistanceSlider.getValue(), False)
        config.ConfigSettings.updateConfigSetting("Bake", "antialiasing", self.aliasingValue.getValue(), False)
        config.ConfigSettings.flush()
        if self.needRestart and self._socketRef:
            self._socketRef.restart()
        self.close()


class DependencyErrorDialog(QtWidgets.QDialog, error_dialog.Ui_Dialog):
    def __init__(self, parent, helpLink=None):
        super().__init__(parent=parent)
        self.helpLink = helpLink
        self.setupUi(self)
        self.descriptionLabel.setOpenExternalLinks(True)
        for btn in self.buttonBox.buttons():
            if btn.text() == "Help":
                btn.setFocus()
                btn.clicked.connect(self.openHelp)
            else:
                btn.clicked.connect(self.close)

    def close(self):
        dontShowAgainState = self.dontShowAgain.checkState() != Qt.CheckState.Checked
        config.ConfigSettings.updateConfigSetting("General", "showDependencyError", dontShowAgainState, False)
        config.ConfigSettings.flush()
        super().close()

    def show(self):
        if config.ConfigSettings.checkIfOptionIsSet("General", "showDependencyError", "True"):
            super().show()

    def openHelp(self):
        if self.helpLink:
            webbrowser.open(self.helpLink)
        else:
            self.close()
