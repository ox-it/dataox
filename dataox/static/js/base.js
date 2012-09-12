var sparqlEndpointURL = "/sparql/";


function supportsCORS() {
  return ('withCredentials' in new XMLHttpRequest());
}

var timeSeriesMetadataQuery = "\
  PREFIX timeseries: <http://purl.org/NET/time-series/>\n\
  SELECT ?endpoint ?timeSeries ?seriesName ?summation ?sampling ?resolution ?samplingType WHERE {\n\
    {\n\
      SELECT ?timeSeries ?summation WHERE {\n\
        {\n\
          BIND (<TIMESERIES> as ?timeSeries) .\n\
          ?timeSeries a timeseries:TimeSeries .\n\
        } UNION {\n\
          <TIMESERIES> a timeseries:VirtualTimeSeries ;\n\
            ?summation ?timeSeries .\n\
          FILTER (?summation in (timeseries:include, timeseries:exclude)) .\n\
          ?timeSeries a timeseries:TimeSeries .\n\
        }\n\
      }\n\
    } .\n\
    ?timeSeries\n\
      timeseries:endpoint ?endpoint ;\n\
      timeseries:seriesName ?seriesName ;\n\
      timeseries:sampling ?sampling .\n\
    ?sampling a timeseries:Sampling ;\n\
      timeseries:samplingType ?samplingType ;\n\
      timeseries:resolution ?resolution .\n\
  }";

function getTimeSeriesMetaData(timeSeries, callback) {
  var query = timeSeriesMetadataQuery.replace(/TIMESERIES/g, timeSeries);
  $.get(sparqlEndpointURL, {
    query: query,
    format: 'srj',
  }, function (data) {
    var metadata = {series: {},
                    seriesByEndpoint: {},
                    endpointsReturned: 0,
                    timeSeriesCount: 0,
                    seriesData: {},
      				data: [],
      				samplings: {}};
    var samplings = {}

    for (var i in data.results.bindings) {
      var binding = data.results.bindings[i];

      var include = !(binding.summation &&
                      binding.summation.value == 'http://purl.org/NET/time-series/exclude');
      var timeSeriesData = {endpoint: binding.endpoint.value,
                            timeSeries: binding.timeSeries.value,
                            seriesName: binding.seriesName.value,
                            include: include};
      metadata.series[timeSeriesData.timeSeries] = timeSeriesData;
      if (!(timeSeriesData.endpoint in metadata.seriesByEndpoint))
        metadata.seriesByEndpoint[timeSeriesData.endpoint] = {};
      if (!(timeSeriesData.seriesName in metadata.seriesByEndpoint[timeSeriesData.endpoint]))
        metadata.timeSeriesCount += 1
      metadata.seriesByEndpoint[timeSeriesData.endpoint][timeSeriesData.seriesName] = timeSeriesData.timeSeries;
      
      if (!(binding.samplingType.value in samplings))
        samplings[binding.samplingType.value] = {};
      var s = samplings[binding.samplingType.value];
      if (!(binding.resolution.value in s))
        s[binding.resolution.value] = [];
      s[binding.resolution.value].push(binding.timeSeries.value);
    }
    
    for (var samplingType in samplings) {
      for (var resolution in samplings[samplingType]) {
        if (samplings[samplingType][resolution].length == metadata.series.length)
          metadata.samplings.push({samplingType: samplingType,
                                   resolution: resolution});
      }
    }

    callback(metadata);
  }, 'json'); 
}



function getTimeSeriesData(metadata, samplingType, resolution, startTime, endTime, callback) {
  for (var endpoint in metadata.seriesByEndpoint) {
    var seriesNames = [];
    for (var seriesName in metadata.seriesByEndpoint[endpoint])
      seriesNames.push(seriesName);
    var data = {series: seriesNames.join(','),
                type: samplingType,
                resolution: resolution,
                action: 'fetch'};
    if (startTime != null) data.startTime = startTime;
    if (endTime != null) data.endTime = endTime;
    var newCallback = function(data) { processTimeSeriesData(metadata, endpoint, data, callback); };
    if (supportsCORS()) {
      data.format = 'json';
      $.get(endpoint, data, newCallback, 'json');
    } else {
      data.format = 'js';
      $.ajax(endpoint, {data: data,
                        dataType: 'jsonp',
                        success: newCallback});
    }
  }
}

function processTimeSeriesData(metadata, endpoint, data, callback) {
  for (var seriesName in data.series) {
    var seriesData = data.series[seriesName].data;
    metadata.seriesData[metadata.seriesByEndpoint[endpoint][seriesName]] = seriesData;
    metadata.endpointsReturned += 1;
  }
  
  if (metadata.endpointsReturned != metadata.timeSeriesCount)
    return;
  metadata.endpointsReturned = 0;
  
  var data = [];
  var heads = [];
  for (var timeSeries in metadata.seriesData) {
    if (metadata.seriesData[timeSeries].length > 0)
      heads.push([timeSeries, metadata.seriesData[timeSeries].shift()]);
  }
    
  function sortFunc(a, b) {
    return a[1].ts - b[1].ts;
  }

  while (heads.length > 0) {
    heads.sort(sortFunc);
    var head = heads.shift();
    if (head[1].val != null) {
      if (data.length == 0 || head[1].ts != data[data.length-1][0])
        data.push([head[1].ts, 0]);
      if (metadata.series[head[0]].include)
        data[data.length-1][1] += head[1].val;
      else
        data[data.length-1][1] -= head[1].val;
    }
    if (metadata.seriesData[head[0]].length > 0)
      heads.push([head[0], metadata.seriesData[head[0]].shift()]);
  }
  
  callback(data);
}
  

function widgetOpenMeters(elementID, timeSeries) {
  getTimeSeriesMetaData(timeSeries, function(metadata) {
    var startTime = Math.floor((new Date()).getTime() / 1000 - 86400 * 60); // 60 days ago
    var element = $('#'+elementID);
    getTimeSeriesData(metadata, "average", 86400, startTime, null, function(data) {
      if (data.length == 0) {
        element.html("No recent readings available.").css('height', 'auto');
        return;
      }

      var options = {
        lines: { show: true, lineWidth: 1, fill: true, fillColor: '#B8CCD7' },
        points: { show: true, radius: 1 },
        xaxis: { mode: "time" },
        yaxis: { min: 0 },
        grid: { 
          show: true,
          clickable: true,
          hoverable: true 
        },
        colors: ["#006699", "#d18b2c", "#dba255"],
      };

      element.html("");
      $.plot(element, [data], options);
    });
  });
}

$(function() {
	$('input.search-submit').css('display', 'none');
	$('.search-form label').click(function () {
		$(this).hide();
		$('#search-query').focus();
	});
	if (!$('#search-query').val())
		$('.search-form label').show();
	$('#search-query').focus(function () {
		$('.search-form label').hide();
	}).blur(function () {
		if (!$(this).val())
		  $('.search-form label').show()
	})
});

$(function() {
	$('.autocomplete').each(function(i, e) {
		e = $(e);
		var h = $('<input type="hidden">').attr('name', e.attr('name'));
		e.attr('name', e.attr('name') + '-label').after(h);
		e.autocomplete({
			source: function(request, callback) {
				$.get(e.data('data-search-url') || window.searchURL, {
					q: request.term + '*',
					format: 'autocomplete',
					"type": e.attr('data-type')
				}, callback, 'json');
			},
			minLength: 2,
			select: function(event, ui) {
				e.val(ui.item.label);
				h.val(ui.item.value);
				return false;
			}
		});
	});
});