var map = null;

window.onresize = function(event) {
	$('#container').height(window.innerHeight - $('header').height());
}

$(function() {
	window.onresize(null);
	map = new OpenLayers.Map("map", { controls: [] });
	map.addLayer(new OpenLayers.Layer.OSM());
	map.addControl(new OpenLayers.Control.Navigation());
	map.addControl(new OpenLayers.Control.KeyboardDefaults());
	map.addControl(new OpenLayers.Control.Attribution());

	  var lonLat = new OpenLayers.LonLat(-1.258, 51.752)
	    .transform(new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
	               map.getProjectionObject() // to Spherical Mercator Projection
	              );
	
	map.setCenter (lonLat, 13);
});