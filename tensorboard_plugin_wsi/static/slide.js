var viewer = null;

function set_wsi(name, inp_mpp) {

    try {
        viewer.destroy();
    } catch (error) {
        console.error(error);
    }

    viewer = new OpenSeadragon({
        id: "view",
        tileSources: "tiles/".concat(name).concat("/"),
        prefixUrl: "static/images/",
        showNavigator: true,
        showRotationControl: true,
        animationTime: 0.5,
        blendTime: 0.1,
        constrainDuringPan: true,
        maxZoomPixelRatio: 2,
        minZoomLevel: 1,
        visibilityRatio: 1,
        zoomPerScroll: 2,
        timeout: 120000,
    });
    viewer.addHandler("open", function() {
        // To improve load times, ignore the lowest-resolution Deep Zoom
        // levels.  This is a hack: we can't configure the minLevel via
        // OpenSeadragon configuration options when the viewer is created
        // from DZI XML.
        viewer.source.minLevel = 8;
    });

    var mpp = parseFloat(inp_mpp);
    viewer.scalebar({
        pixelsPerMeter: mpp ? (1e6 / mpp) : 0,
        xOffset: 10,
        yOffset: 10,
        barThickness: 3,
        color: '#555555',
        fontColor: '#333333',
        backgroundColor: 'rgba(255, 255, 255, 0.5)',
    });
};
