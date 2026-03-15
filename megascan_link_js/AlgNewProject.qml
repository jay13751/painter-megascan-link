import QtQuick 2.7
import Painter 1.0
import QtQuick.Controls 2.0
import QtQuick.Dialogs 1.2
import AlgWidgets 2.0
import QtQuick.Layouts 1.12
import "utility.js" as Util

AlgDialog {
    id: createProjectDialog
    title: "Mesh Assets found in the import data"
    visible: false
    width: 420
    height: 150
    maximumHeight: height
    maximumWidth: width
    minimumHeight: height
    minimumWidth: width

    property var importData: ({})

    signal importPressed(var importData)
    signal newProjectPressed(var importData)

    function openWithData(data) {
        createProjectDialog.importData = data
        createProjectDialog.open()
    }

    Rectangle {
        anchors.fill: parent
        color: createProjectDialog.color
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            AlgLabel {
                Layout.fillWidth: true
                text: "The incoming Megascans export contains one or more mesh assets. Create a new Painter project with a mesh, or only import textures into the current project?"
                wrapMode: Text.Wrap
            }
            Item { Layout.fillHeight: true }
            RowLayout {
                Item { Layout.fillWidth: true }
                AlgButton {
                    text: "Import"
                    onClicked: createProjectDialog.importPressed(createProjectDialog.importData)
                }
                AlgButton {
                    text: "New Project"
                    onClicked: createProjectDialog.newProjectPressed(createProjectDialog.importData)
                }
            }
        }
    }
}
