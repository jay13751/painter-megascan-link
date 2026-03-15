from ..qt_compat import QtCore, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(622, 275)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.titleLabel = QtWidgets.QLabel("Oops! Megascan Link cannot be started.", Dialog)
        self.titleLabel.setStyleSheet("QLabel { color: red; font-size: 24px; }")
        self.descriptionLabel = QtWidgets.QLabel(
            "The plugin could not initialize correctly. Use Help to open the installation guide, then restart Painter.",
            Dialog,
        )
        self.descriptionLabel.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.descriptionLabel.setWordWrap(True)
        self.dontShowAgain = QtWidgets.QCheckBox("Don't show again", Dialog)
        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Help,
            QtCore.Qt.Orientation.Horizontal,
            Dialog,
        )
        self.verticalLayout.addWidget(self.titleLabel)
        self.verticalLayout.addWidget(self.descriptionLabel)
        self.verticalLayout.addWidget(self.dontShowAgain)
        self.verticalLayout.addStretch(1)
        self.verticalLayout.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
