function widgetMap(elementID, longitude, latitude) {
  map = new OpenLayers.Map(elementID, { controls: [] });
  map.addLayer(new OpenLayers.Layer.OSM());
  map.addControl(new OpenLayers.Control.Navigation());
  map.addControl(new OpenLayers.Control.KeyboardDefaults());
  map.addControl(new OpenLayers.Control.Attribution("D"));
 
  var lonLat = new OpenLayers.LonLat(longitude, latitude)
    .transform(new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
               map.getProjectionObject() // to Spherical Mercator Projection
              );
 
  var zoom=7;
 
  var markers = new OpenLayers.Layer.Markers( "Markers" );
  map.addLayer(markers);
 
  markers.addMarker(new OpenLayers.Marker(lonLat));
 
  map.setCenter (lonLat, zoom);
}