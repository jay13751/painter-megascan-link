String.prototype.format = function () {
    var i = 0, args = arguments;
    return this.replace(/{}/g, function () {
        return typeof args[i] !== 'undefined' ? args[i++] : '';
    });
};

function checkIfSettingsIsSet(setting) {
    var filterstrings = ['true', 'yes', 'y', 'ok', '1'];
    var regex = new RegExp(filterstrings.join('|'), 'i');
    return regex.test(setting);
}

function removeFromAssets(asset, assets) {
    return assets.filter(function (element) {
        return element.id !== asset.id;
    });
}

function getHpMeshes(asset) {
    var hpmeshes = asset.high_poly_meshes || [];
    var res = [];
    hpmeshes.forEach(function (mesh) {
        res.push(mesh.path);
    });
    return res;
}

function firstMeshPath(asset) {
    if (!asset.meshes || asset.meshes.length === 0) {
        return '';
    }
    return asset.meshes[0].path;
}
