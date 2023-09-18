// Create a map centered on Kenya
var map = L.map('map').setView([1.2921, 36.8219], 7);

// Add a base layer (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

// Your GeoJSON data
var geojsonData = {
    "type": "GeometryCollection",
    "geometries": [
        {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [35.6984915, 1.3122429],
                        [35.6979125, 1.3162657],
                        [35.6981733, 1.3224557],
                        [35.69074, 1.3502678],
                        [35.6890653, 1.3533233],
                        [35.6886806, 1.3565444],
                        [35.6911062, 1.3590569],
                        [35.6984915, 1.3122429]
                    ]
                ]
            ]
        }
    ]
};

// Create a GeoJSON layer and add it to the map with red fill color
L.geoJSON(geojsonData, {
    style: {
        fillColor: 'red', // Fill color
        fillOpacity: 0.6, // Fill opacity
        color: 'white', // Border color
        weight: 1, // Border weight
    },
}).addTo(map);
