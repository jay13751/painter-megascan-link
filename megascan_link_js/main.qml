import QtQuick 2.7
import Painter 1.0
import QtWebSockets 1.0
import QtQuick.Controls 2.0
import AlgWidgets 2.0
import QtQuick.Layouts 1.12
import "utility.js" as Util

PainterPlugin {
    id: megascanlink

    property bool projectCreated: false
    property var settings: ({})
    property var meshAsset: ({})
    property var payload: ({ source: "fab", assets: [] })
    property var decision: ({ action: "process_payload", project_is_open: null })
    property var pendingMessage: null
    property var importQueue: []

    Component.onCompleted: {
        alg.log.info("Megascan Link JS shim loaded")
    }

    function assetComponents(asset) {
        return asset.components || asset.textures || []
    }

    function assetMeshes(asset) {
        return asset.meshList || asset.meshes || []
    }

    function importResources(assets) {
        alg.log.info("Importing Megascan assets into the current project")
        importQueue = []
        alg.log.info("Import batch contains {} assets".format((assets || []).length))
        assets.forEach(function (asset) {
            var textures = assetComponents(asset)
            alg.log.info("Importing asset {} ({}) with {} textures".format(asset.name, asset.id, textures.length))
            textures.forEach(function (bitmap) {
                if (bitmap.path) {
                    importQueue.push({
                        assetName: asset.name,
                        assetId: asset.id,
                        path: bitmap.path
                    })
                }
            })
        })
        if (importQueue.length === 0) {
            alg.log.warning("No compatible textures queued for import")
            return
        }
        alg.log.info("Queued {} texture imports".format(importQueue.length))
        resourceImportTimer.start()
    }

    function setUpAndBake(asset) {
        if (Object.keys(asset).length !== 0) {
            alg.log.info("Setting up baking parameters and performing texture bake")
            var bakingParams = alg.baking.commonBakingParameters()
            var bakeSettings = megascanlink.settings.Bake
            bakingParams.commonParameters.Output_Size = JSON.parse(bakeSettings.resolution)
            bakingParams.detailParameters.Average_Normals = Util.checkIfSettingsIsSet(bakeSettings.average)
            bakingParams.detailParameters.Ignore_Backface = Util.checkIfSettingsIsSet(bakeSettings.ignorebackface)
            bakingParams.detailParameters.Relative_to_Bounding_Box = Util.checkIfSettingsIsSet(bakeSettings.relative)
            bakingParams.detailParameters.Max_Rear_Distance = parseFloat(bakeSettings.maxreardistance)
            bakingParams.detailParameters.Max_Frontal_Distance = parseFloat(bakeSettings.maxfrontaldistance)
            bakingParams.detailParameters.Antialiasing = megascanlink.settings.Bake.antialiasing
            bakingParams.detailParameters.High_Definition_Meshes = Util.getHpMeshes(asset)
            alg.baking.setCommonBakingParameters(bakingParams)
            alg.baking.bake(alg.texturesets.getActiveTextureSet())
        }
    }

    function createProjectWithResources(asset, imports) {
        var err = false
        if (alg.project.isOpen()) {
            alg.log.info("Saving current project")
            try {
                alg.project.save("", alg.project.SaveMode.Full)
                alg.project.close()
            } catch (error) {
                alg.log.error("Failed to save current project before creating a new one")
                err = true
                saveError.open()
            }
        }
        if (!err) {
            var meshPath = Util.firstMeshPath(asset)
            if (!meshPath) {
                alg.log.warning("No mesh path found for asset {}".format(asset.name))
                return
            }
            alg.log.info("Creating project with mesh: {}".format(asset.name))
            var bitmaps = []
            ;assetComponents(asset).forEach(function (bitmap) {
                bitmaps.push(alg.fileIO.localFileToUrl(bitmap.path))
            })
            alg.project.create(alg.fileIO.localFileToUrl(meshPath), bitmaps)
            if (imports.length !== 0) {
                megascanlink.importResources(imports)
            }
            megascanlink.projectCreated = true
            megascanlink.meshAsset = asset
            alg.log.info("Project created successfully")
        }
    }

    function checkForMeshAssets(assets) {
        var meshes = []
        assets.forEach(function (asset) {
            if (assetMeshes(asset).length > 0 || asset.kind === "3d" || asset.kind === "3dplant" || asset.kind === "model" || asset.type === "3d" || asset.type === "3dplant") {
                meshes.push(asset)
            }
        })
        return { hasMeshes: meshes.length > 0, count: meshes.length, lastMesh: meshes.length > 0 ? meshes[meshes.length - 1] : {}, meshes: meshes, data: assets }
    }

    function handleDecision(meshCheck) {
        switch (megascanlink.decision.action) {
        case "import_resources":
            megascanlink.importResources(megascanlink.payload.assets)
            break
        case "prompt_project_creation":
            createProject.openWithData(meshCheck)
            break
        case "create_project_select_mesh":
            selectMesh.openWithAssets(meshCheck)
            break
        case "create_project":
            megascanlink.createProjectWithResources(meshCheck.lastMesh, Util.removeFromAssets(meshCheck.lastMesh, megascanlink.payload.assets))
            break
        case "warn_no_project":
            alg.log.warning("No project open and no 3D meshes found in the import data")
            break
        case "no_assets":
            alg.log.warning("Payload contained no supported assets")
            break
        default:
            fallbackHandle(meshCheck)
        }
    }

    function fallbackHandle(meshCheck) {
        if (meshCheck.hasMeshes && alg.project.isOpen() && Util.checkIfSettingsIsSet(megascanlink.settings.General.askcreateproject)) {
            createProject.openWithData(meshCheck)
        } else if (alg.project.isOpen()) {
            megascanlink.importResources(megascanlink.payload.assets)
        } else {
            if (meshCheck.hasMeshes) {
                if (meshCheck.count > 1) {
                    selectMesh.openWithAssets(meshCheck)
                } else {
                    megascanlink.createProjectWithResources(meshCheck.lastMesh, Util.removeFromAssets(meshCheck.lastMesh, megascanlink.payload.assets))
                }
            } else {
                alg.log.warning("No project open and no 3D meshes found in the import data")
            }
        }
    }

    onActiveTextureSetChanged: function(stackPath) {
        if (megascanlink.projectCreated === true) {
            megascanlink.projectCreated = false
            alg.log.info("Changing texture set [{}] resolution to {}".format(stackPath, 4096))
            alg.texturesets.setResolution(stackPath, [12, 12])
            if (Util.checkIfSettingsIsSet(megascanlink.settings.Bake.enabled)) {
                megascanlink.setUpAndBake(megascanlink.meshAsset)
            }
        }
    }

    WebSocketServer {
        listen: true
        port: 1212

        onClientConnected: {
            alg.log.info("Megascan Link Python connection established")
            webSocket.onTextMessageReceived.connect(function (message) {
                alg.log.info("Megascan Link JS received payload ({} chars)".format(message.length))
                megascanlink.pendingMessage = message
                processMessage.start()
            })
        }
    }

    Timer {
        id: processMessage
        interval: 0
        repeat: false
        onTriggered: {
            if (!megascanlink.pendingMessage) {
                return
            }
            var pythondata = JSON.parse(megascanlink.pendingMessage)
            megascanlink.pendingMessage = null
            megascanlink.payload = pythondata.payload || { source: "fab", assets: [] }
            megascanlink.settings = pythondata.settings || {}
            megascanlink.decision = pythondata.decision || { action: "process_payload", project_is_open: null }
            alg.log.info("Megascan Link handling action {} with {} assets".format(megascanlink.decision.action, (megascanlink.payload.assets || []).length))
            var meshCheck = checkForMeshAssets(megascanlink.payload.assets || [])
            alg.log.info("Mesh check result: {} mesh assets".format(meshCheck.count))
            handleDecision(meshCheck)
        }
    }

    Timer {
        id: resourceImportTimer
        interval: 0
        repeat: true
        property var urls: []

        onTriggered: {
            if (megascanlink.importQueue.length === 0) {
                stop()
                if (Util.checkIfSettingsIsSet(megascanlink.settings.General.selectafterimport) && urls.length > 0) {
                    alg.resources.selectResources(urls)
                }
                alg.log.info("Megascan resource import queue completed")
                urls = []
                return
            }

            var job = megascanlink.importQueue.shift()
            alg.log.info("Resolving usages for {}".format(job.path))
            try {
                var usages = alg.resources.allowedUsages(job.path)
                alg.log.info("Importing resource {}".format(job.path))
                var imported = alg.resources.importProjectResource(job.path, usages, "Megascan/{}({})".format(job.assetName, job.assetId))
                urls.push(imported)
                alg.log.info("Resource imported: {}".format(imported))
            } catch (error) {
                alg.log.error("Failed to import resource {}: {}".format(job.path, error))
            }
        }
    }

    AlgDialog {
        id: saveError
        title: "ERROR Could not save current project"
        defaultButtonText: "Ok"
        visible: false
        width: 400
        height: 100
        maximumHeight: height
        maximumWidth: width
        minimumHeight: height
        minimumWidth: width
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            AlgLabel {
                Layout.fillWidth: true
                text: "Could not save the project, please save or close the current project before trying to import Megascan assets"
                wrapMode: Text.Wrap
            }
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }

        onAccepted: saveError.close()
    }

    AlgSelectDialog {
        id: selectMesh

        onAccepted: {
            var meshAsset = assets.get(currentIndex).data
            megascanlink.createProjectWithResources(meshAsset, Util.removeFromAssets(meshAsset, importData.data))
        }
    }

    AlgNewProject {
        id: createProject

        onImportPressed: {
            megascanlink.importResources(importData.data)
            createProject.close()
        }

        onNewProjectPressed: {
            if (importData.count > 1) {
                selectMesh.openWithAssets(importData)
            } else {
                megascanlink.createProjectWithResources(importData.lastMesh, Util.removeFromAssets(importData.lastMesh, importData.data))
            }
            createProject.close()
        }
    }
}


