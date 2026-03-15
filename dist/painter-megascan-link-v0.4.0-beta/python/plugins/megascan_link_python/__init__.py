try:
    import substance_painter.ui as sbsui
except Exception:  # pragma: no cover - unavailable outside Painter
    sbsui = None

from . import config, log
from .import_controller import ImportController


class Data(object):
    toolbar = None
    socket = None
    controller = None
    icon = None
    dialogs = None
    QtGui = None
    socket_type = None


def _ensure_ui_modules():
    if Data.dialogs is not None:
        return
    from .qt_compat import QtGui
    from . import dialogs
    from .ui import icon

    Data.dialogs = dialogs
    Data.icon = icon
    Data.QtGui = QtGui


def _ensure_socket_type():
    if Data.socket_type is None:
        from .socket_server import SocketServerThread

        Data.socket_type = SocketServerThread


def openSettingsDialog():
    if sbsui is None:
        return
    _ensure_ui_modules()
    mainWindow = sbsui.get_main_window()
    dialog = Data.dialogs.SettingsDialog(Data.socket, mainWindow)
    dialog.show()


def createToolBar():
    if sbsui is None:
        return
    _ensure_ui_modules()
    Data.toolbar = sbsui.add_toolbar("Megascan Link", "megascanlink")
    qicon = Data.QtGui.QIcon()
    qicon.addPixmap(Data.icon.getIconAsQPixmap("megascan_logo_idle.png"))
    qicon.addPixmap(Data.icon.getIconAsQPixmap("megascan_logo.png"), Data.QtGui.QIcon.Active)
    action = Data.toolbar.addAction(qicon, "Megascan Link Settings")
    action.triggered.connect(openSettingsDialog)


def start_plugin():
    log.LoggerLink.setLoggerName("megascanlink")
    config.ConfigSettings.setIniFilePath("settings")
    config.ConfigSettings.setUpInitialConfig()

    createToolBar()
    _ensure_socket_type()
    Data.controller = ImportController()
    Data.socket = Data.socket_type()
    Data.socket.onPayloadNormalized.connect(Data.controller.handle_payload)
    Data.socket.start()
    log.LoggerLink.Log("Megascan Link Python initialized")


def close_plugin():
    if Data.socket:
        Data.socket.close()
    if Data.toolbar and sbsui is not None:
        sbsui.delete_ui_element(Data.toolbar)
