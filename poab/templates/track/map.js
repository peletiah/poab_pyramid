<script type="text/javascript">
var lat = 40.9850008;
var lon = 29.0245040;
var zoom = 2;
var map, layer;

function init(){
map = new OpenLayers.Map('mapdiv', {
controls: [
    new OpenLayers.Control.Navigation({
        dragPanOptions: {
            enableKinetic: true
        }
    }),
    new OpenLayers.Control.Zoom(),
    new OpenLayers.Control.LayerSwitcher(),
    new OpenLayers.Control.KeyboardDefaults(),
    new OpenLayers.Control.ScaleLine({geodesic: false}),
    new OpenLayers.Control.MousePosition({
        displayProjection: new OpenLayers.Projection("EPSG:4326")})
]
});

// the SATELLITE layer has all 22 zoom level, so we add it first to
// become the internal base layer that determines the zoom levels of the
// map.
//var gsat = new OpenLayers.Layer.Google(
//    "Google Satellite",
//    {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22, visibility: false}
//);
//var gphy = new OpenLayers.Layer.Google(
//    "Google Physical",
//    {type: google.maps.MapTypeId.TERRAIN, visibility: false}
//);
//var gmap = new OpenLayers.Layer.Google(
//    "Google Streets", // the default
//    {numZoomLevels: 20, visibility: false}
//);
//var ghyb = new OpenLayers.Layer.Google(
//    "Google Hybrid",
//    {type: google.maps.MapTypeId.HYBRID, numZoomLevels: 22, visibility: false}
//);


var osm = new OpenLayers.Layer.OSM( "OSM" );

<%text>
var cycle = new OpenLayers.Layer.OSM("OpenCycleMap",
                                ["http://a.tile.opencyclemap.org/cycle/${z}/${x}/${y}.png",
                                 "http://b.tile.opencyclemap.org/cycle/${z}/${x}/${y}.png",
                                 "http://c.tile.opencyclemap.org/cycle/${z}/${x}/${y}.png"],
                                { displayOutsideMaxExtent: true,transitionEffect: 'resize'});

var landscape = new OpenLayers.Layer.OSM("Landscape",
                                 ["http://a.tile3.opencyclemap.org/landscape/${z}/${x}/${y}.png",
                                 "http://b.tile3.opencyclemap.org/landscape/${z}/${x}/${y}.png",
                                 "http://c.tile3.opencyclemap.org/landscape/${z}/${x}/${y}.png"],
                                 { displayOutsideMaxExtent: true, transitionEffect: 'resize'});
</%text>

var lineSelectStyle = new OpenLayers.Style({
                'strokeWidth' : 6,
                'strokeColor' : '#1E6B94',
                'strokeOpacity' : 0.7,
                'pointRadius': 8,
                'fillColor': 'red'
        });


var lineDefaultStyle = new OpenLayers.Style({
                'strokeWidth' : 4,
                'strokeColor' : 'red',
                'strokeOpacity' : 0.5,
                'cursor' : 'pointer',
                'pointRadius': 8,
                'fillColor': 'red'
        });

var styleMap = new OpenLayers.StyleMap({
                 'default': lineDefaultStyle,
                 'select': lineSelectStyle
                  });

var report = function(e) {
    OpenLayers.Console.log(e.type, e.feature.id);
};


var vector_layer = new OpenLayers.Layer.Vector("GeoJSON", {
            projection: new OpenLayers.Projection("EPSG:4326"),
            strategies: [new OpenLayers.Strategy.Fixed()],
            styleMap: styleMap,
            protocol: new OpenLayers.Protocol.Script({
                url: "${jsonlink | n}",
                format: new OpenLayers.Format.GeoJSON({
                    ignoreExtraDims: true
                }),
                callbackKey: "callback"
            }),
            eventListeners: {
                "featuresadded": function() {
                    console.log(this.features[0])
                    x=this.features[0].geometry.x
                    y=this.features[0].geometry.y
                    if (this.features[0].data.type == 'point') {
                        this.map.setCenter([x,y],6)
                    }
                    else {
                        this.map.zoomToExtent(this.getDataExtent())};
                },
                "featureselected": function(evt) {
                    var feature = evt.feature;
                    if (feature.popup) {
                        map.removePopup(feature.popup);
                        feature.popup.destroy();
                        feature.popup = null;}

                    var popup = new OpenLayers.Popup.FramedCloud("popup",
                    feature.geometry.getBounds().getCenterLonLat(),
                    null,
                    '<b>date:</b> '+feature.attributes.date+'<br>'+feature.attributes.distance+feature.attributes.timespan)
                    feature.popup = popup
                    map.addPopup(popup)
                },
               "featureunselected":function(evt){
                     var feature = evt.feature;
                     map.removePopup(feature.popup);
                     feature.popup.destroy();
                     feature.popup = null;
                }
            }
        });

vector_layer.events.register("featureselected", vector_layer);

var highlightControl = new OpenLayers.Control.SelectFeature(vector_layer, {
                            hover:true, 
                            highlightOnly: true,
                            selectStyle: {
                            'strokeColor' : '#278BC1',
                            'fillColor' : 'red',
                            'strokeWidth' : 6,
                            'strokeOpacity' : 0.5,
                            'pointRadius': 10}
                            });
map.addControl(highlightControl);
highlightControl.activate();

var selectControl = new OpenLayers.Control.SelectFeature(vector_layer,
                            {toggle:true});
map.addControl(selectControl);
selectControl.activate();



map.addLayers([osm,cycle,landscape,vector_layer]);

// Google.v3 uses EPSG:900913 as projection, so we have to
// transform our coordinates
map.setCenter(new OpenLayers.LonLat(lon, lat).transform(
    new OpenLayers.Projection("EPSG:4326"),
    map.getProjectionObject()
), zoom);


}
</script>
