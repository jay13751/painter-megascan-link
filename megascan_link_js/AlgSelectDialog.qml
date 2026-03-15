import QtQuick 2.7
import Painter 1.0
import QtQuick.Controls 2.0
import AlgWidgets 2.0
import QtQuick.Layouts 1.12
import "utility.js" as Util

AlgDialog {
    id: selectDialog
    title: "Select Megascan Asset Mesh for New Project"
    width: 420
    height: 300
    maximumHeight: height
    maximumWidth: width
    minimumHeight: height
    minimumWidth: width
    defaultButtonText: "Select"

    property var assets: assetList
    property var importData: ({})
    property int currentIndex: assetListView.currentIndex

    function addAssets(assetsIn) {
        assetList.clear()
        importData = assetsIn
        importData.meshes.forEach(function (asset) {
            assetList.append({ name: "{} (id:{})".format(asset.name, asset.id), image: asset.preview_image || "", data: asset })
        })
        if (assetList.count > 0) {
            assetListView.currentIndex = 0
        }
    }

    function openWithAssets(assetsIn) {
        selectDialog.addAssets(assetsIn)
        selectDialog.open()
    }

    ListView {
        id: assetListView
        parent: selectDialog.contentItem
        anchors.fill: parent
        anchors.margins: 10
        model: assetList
        header: headerList
        delegate: assetListDelegate
        focus: true
        highlight: Rectangle { color: "grey" }
        ScrollBar.vertical: AlgScrollBar {}
    }

    ListModel { id: assetList }

    Component {
        id: headerList
        Rectangle {
            width: parent.width
            height: 24
            color: selectDialog.color
            Rectangle {
                width: parent.width
                height: 18
                color: "#1f1f1f"
                AlgLabel {
                    anchors.fill: parent
                    anchors.margins: 2
                    text: "Select a 3D Megascan Asset:"
                }
            }
        }
    }

    Component {
        id: assetListDelegate
        Item {
            width: parent.width
            height: 72
            RowLayout {
                spacing: 4
                Image {
                    Layout.margins: 4
                    Layout.preferredWidth: 64
                    Layout.preferredHeight: 64
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                    source: image ? "file:/" + image : ""
                }
                AlgLabel {
                    text: name
                    Layout.leftMargin: 4
                }
            }
            MouseArea {
                anchors.fill: parent
                onClicked: { assetListView.currentIndex = index }
            }
        }
    }
}
