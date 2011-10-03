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
 
  var zoom=11;
 
  var markers = new OpenLayers.Layer.Markers( "Markers" );
  map.addLayer(markers);
 
  var size = new OpenLayers.Size(21,25);
  var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
  var icon = new OpenLayers.Icon('/site-media/marker.png', size, offset);
  markers.addMarker(new OpenLayers.Marker(lonLat), icon);
 
  map.setCenter (lonLat, zoom);
}

function widgetOpenMeters(elementID, series, include, exclude) {
  var seriesByEndpoint = {};
  var seriesDataRetrievedExpected = 0;
  for (var uri in series) {
    if (seriesByEndpoint[series[uri].endpoint] == undefined)
      seriesByEndpoint[series[uri].endpoint] = [];
    seriesByEndpoint[series[uri].endpoint].push(series[uri]);
    seriesDataRetrievedExpected += 1;
  }
  for (var i in include)
    series[include[i]].action = "include";
  for (var i in exclude)
    series[exclude[i]].action = "exclude";
  
  var seriesData = {};
  var seriesDataRetrievedCount = 0;

  for (var endpoint in seriesByEndpoint) {
    var endpointSeries = seriesByEndpoint[endpoint];

    var seriesNames = []; var seriesURIs = []
    for (var s in endpointSeries) {
      seriesNames.push(endpointSeries[s].seriesName);
      seriesURIs.push(endpointSeries[s].uri);
    }
    
    $.get(endpoint, {
      "format": 'json',
      "action": 'fetch',
      "series": seriesNames.join(","),
      "resolution": 86400,
      "type": 'average',
      "startTime": Math.floor((new Date()).getTime() / 1000 - 86400 * 60), // 60 days ago
    }, function(data) {
      for (var i in seriesNames) {
        seriesData[seriesURIs[i]] = data.series[seriesNames[i]].data;
        seriesDataRetrievedCount += 1;
      }
      if (seriesDataRetrievedExpected == seriesDataRetrievedCount)
        widgetOpenMetersData(elementID, series, seriesData, include, exclude);
    }, "json");
  }
}

function widgetOpenMetersData(elementID, series, seriesData, include, exclude) {
  var data = [];
  var heads = [];
  for (var seriesName in seriesData)
    heads.push([seriesName, seriesData[seriesName].shift()]);
    
  function sortFunc(a, b) {
    return a[1].ts - b[1].ts;
  }

  while (heads.length > 0) {
    heads.sort(sortFunc);
    var head = heads.shift();
    if (head[1].val != null) {
      if (data.length == 0 || head[1].ts != data[data.length-1][0])
        data.push([head[1].ts, 0]);
      if (series[head[0]].action == "include")
        data[data.length-1][1] += head[1].val;
      else if (series[head[0]].action == "exclude")
        data[data.length-1][1] -= head[1].val;
    }
    if (seriesData[head[0]].length > 0)
      heads.push([head[0], seriesData[head[0]].shift()]);
  }
  
  if (data.length == 0) {
    $('#'+elementID).html("No recent readings available.").css('height', 'auto');
    return;
  }

  var options = {
    lines: { show: true, lineWidth: 1, fill: true, fillColor: '#B8CCD7' },
    points: { show: true, radius: 1 },
    xaxis: { 
      mode: "time", // first coord has to be a _javascript timestamp_ ie epoch in milliseconds
/*    min: (new Date(yesterday)).getTime(),
      max: (new Date(today)).getTime() */
    },
    yaxis: {
      min: 0,
    },
    grid: { 
      show: true,
      clickable: true,
      hoverable: true 
    },
    colors: ["#006699", "#d18b2c", "#dba255"],
  };
    $('#'+elementID).html("");
    $.plot($('#'+elementID), [data], options);
  
}