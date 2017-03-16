/* **************************************************************/
/*                                                              */
/* oxpointsMap_v3.js - written by Janet McKnight, February 2013 */
/* based on oxpointsMap.js (for API v2), July 2009              */
/*                                                              */
/* **************************************************************/ 

var protocol;

if (window.location.protocol.match('^https?')) {
    protocol = window.location.protocol;
} else {
    protocol = 'http:';
}

/* ******************************** user options ****************************/

// values are shown as [default|other]
//
// oxpUserOptions { 
//      imageRootDir : ['http://www.oucs.ox.ac.uk/oxpoints/images/typeicons/'|URL],
//      initialZoom : [13|num],
//      initialMapType : ['OSM'|(normal|satellite|hybrid|terrain)],
//      showPics : [0|1],
//      showHomepage : [1|0] 
//      showGMapLink : [text]
//      };

/* ******************************** infoWindow styles ****************************/

// .infoWindow_name
// .infoWindow_address
// .infoWindow_link
// .infoWindow_img_span 
// .infoWindow_img

/* ******************************** other styles ****************************/

// span.oxpoints-gmap-link 
// ul#oxpoints-maplist
// li a.oxpSideLink

/* ******************************** global setup ****************************/

// default centre of map & initial zoom level - these can be overridden by the user

var OxpointsInitialZoom = 13;

var OxpointsMapCenter = [51.757191,-1.26219]; // or calculate this based on points?

var OxpointsInitialMapType;

// default root directory for images - this can be overridden by the user

var OxpointsImageRoot = protocol + '//www.oucs.ox.ac.uk/oxpoints/images/typeicons/'; // include trailing slash

// default setting for photos (off). This can be overridden by the user
// by setting to 1.

var OxpointsShowPics = 0;

// default setting for homepage link (on). This can be overridden by the user
// by setting to 0.

var OxpointsShowHomepage = 1;

// default setting for Google Maps link (off). This can be overridden by the user
// by setting to 1.

var OxpointsShowGMapLink = 0;

var gMarkers = [];

var hashPart = window.location.hash;
var openPin = hashPart.replace(/^#/, "");

/* ******************************** functions ****************************/

// load Google Maps API when page fully loaded

function oxpLoadMapsAPI() {
    var script = document.createElement("script");
    script.type = "text/javascript";
    script.src = protocol + "//maps.googleapis.com/maps/api/js?key=AIzaSyA73Cm5Y6MgAQ1ge6sAl6Yw0fuz1uzN-XQ&sensor=false&callback=initialize";
    document.body.appendChild(script);

}

// showPlace function for sidebar items

function showPlace(s) {
    //    alert(gMarkers[s]);
    google.maps.event.trigger(gMarkers[s], "click");
}


// put the URL for JS (JSON wrapped in callback) in a <script> tag in the <head> 

function getOxpoints(oxp_url) {

    //    alert(oxp_url);
    var scriptTag;
    var tagId = "oxpscript";
    var head = document.getElementsByTagName("head")[0];
    if (scriptTag = document.getElementById(tagId)) { head.removeChild(scriptTag); }
    scriptTag = document.createElement("script");
    scriptTag.setAttribute("type","text/javascript");
    scriptTag.setAttribute("src",oxp_url);
    scriptTag.setAttribute("id",tagId);
    head.appendChild(scriptTag); 

    if (scriptTag != document.getElementById(tagId))
    {
    	if( document.createElement && document.childNodes ) {
    	    document.write('<script type="text\/javascript" src="' + oxp_url + '"><\/script>');
    	}
    }

    //    set user options
    if ( typeof oxpUserOptions != "undefined" )
    {
	if ( oxpUserOptions.imageRootDir )  { OxpointsImageRoot = oxpUserOptions.imageRootDir; }
	if ( oxpUserOptions.initialZoom )   { OxpointsInitialZoom = oxpUserOptions.initialZoom; }
	if ( oxpUserOptions.initialMapType ) { OxpointsInitialMapType = oxpUserOptions.initialMapType; }
	if ( oxpUserOptions.showPics ) { OxpointsShowPics = oxpUserOptions.showPics; }
	if ( oxpUserOptions.showHomepage == 0 ) { OxpointsShowHomepage = oxpUserOptions.showHomepage; }
	if ( oxpUserOptions.showGMapLink ) 
	{ 
	    if ( oxpUserOptions.showGMapLink.match(/./) )
	    { 
		OxpointsShowGMapLink = 1; 
		gMapLinkText = oxpUserOptions.showGMapLink; 
	    }
	    else { OxpointsShowGMapLink = 0 }    
	}
	else { OxpointsShowGMapLink = 0 }    
    }

    // while we've got a handle on the oxpoints URL, create the KML
    // equivalent and add it to the maps div (if this option is set)

    if (OxpointsShowGMapLink == 1)
    {
	var oxp_kml = oxp_url.replace(/\.js.*$/, ".kml");
	var mapDiv = document.getElementById("oxpoints-map");
	var gMapLink = document.createElement("a");
	gMapLink.setAttribute("href",protocol + "//maps.google.co.uk/?q="+oxp_kml+"&z="+OxpointsInitialZoom);
	gMapLink.innerHTML = gMapLinkText;
	var gMapLinkSpan = document.createElement("span");
	gMapLinkSpan.setAttribute("class","oxpoints-gmap-link");
	gMapLinkSpan.appendChild(gMapLink);
	mapDiv.parentNode.appendChild(gMapLinkSpan);
    }

}

// the main function, executed on callback

function oxpoints(json) {

    // initialise the map, set up OSM map tiles & make it the default initial map type

    // add dummy OSM mapType

    var mapTypeIds = [];
    for(var type in google.maps.MapTypeId) {
        mapTypeIds.push(google.maps.MapTypeId[type]);
    }
    mapTypeIds.push("OSM");

    // set up the main map & infoWindow
    
    var mapOptions = {
	center: new google.maps.LatLng(OxpointsMapCenter[0],OxpointsMapCenter[1]),
	zoom: OxpointsInitialZoom,
	mapTypeId: "OSM",
	mapTypeControlOptions: { 
	    mapTypeIds: mapTypeIds
	}
    }

    var map = new google.maps.Map(document.getElementById("oxpoints-map"),mapOptions);
    //    var infoWindow = new google.maps.InfoWindow({maxWidth:275, autoScroll:true});
    var infoWindow = new google.maps.InfoWindow({autoScroll:true});

    // set the map to OSM tiles
 
    map.mapTypes.set("OSM", new google.maps.ImageMapType({
	
	getTileUrl: function(coord,zoom){

	    return protocol + '//static.data.ox.ac.uk/osm-tiles/' + zoom + '/' + coord.x + '/' + coord.y + '.png';
	
	},
	tileSize: new google.maps.Size(256,256),
	name: "OSM",
	maxZoom: 18
    }));

//    * ROADMAP displays the default road map view
//    * SATELLITE displays Google Earth satellite images
//    * HYBRID displays a mixture of normal and satellite views
//    * TERRAIN displays a physical map based on terrain information. 

// override from user options -- otherwise OSM will be set up as default

    if (OxpointsInitialMapType == 'normal')
    {
	map.mapTypeId = google.maps.MapTypeId.ROADMAP;
    }
    else if (OxpointsInitialMapType == 'terrain')
    {
	map.mapTypeId = google.maps.MapTypeId.TERRAIN;
    }
    else if (OxpointsInitialMapType == 'satellite')
    {
	map.mapTypeId = google.maps.MapTypeId.SATELLITE;
    }
    else if (OxpointsInitialMapType == 'hybrid')
    {
	map.mapTypeId = google.maps.MapTypeId.HYBRID;
    }

    // nameList = list of names of points, to be sorted alphabetically
    // nameID = associative array of name => ID - needed for sidebar

    var nameList = new Array;
    var nameID = new Array;
    var allPoints = new Array;
    var missingList = new Array;
    
    // loop through Placemark to get points
    
    for (i = 0; i < json.length; i++)
    {
	if ( json[i] ) 
	{ 

	    // get all the relevant data out of the JSON
	    if ( json[i].geo_long && json[i].geo_lat )
   	    {

		var myid = json[i].uri;
		myid = myid.replace(protocol + '//oxpoints.oucs.ox.ac.uk/id/','');
		var myname = json[i].dc_title;
		if ( typeof myname == "undefined" ) { myname = '[No name]' }
		var mytype;
		// either take the hash part or whatever's after the last slash in the URL
		if ( json[i].type.match('#') )
		{
		    mytype = json[i].type.split('#')[1];
		}
		else
		{
		    var type_arr = json[i].type.split('/');
		    mytype = type_arr[type_arr.length-1];
		}

		var mydesc = json[i].dc_description;
		if ( typeof mydesc == "undefined" ) { mydesc = '' }
		var myvcard = json[i].vCard_adr;
		var myaddr = '';

		if ( typeof myvcard != "undefined" )
		{
		    if ( myvcard['vCard_street-address'] )
		    {
			myaddr = myvcard['vCard_street-address'] + "\n";
		    }
		    if ( myvcard['vCard_postal-code'] )
		    {
			myaddr = myaddr + myvcard['vCard_postal-code'];
		    }
		}

		var mylng = json[i].geo_long;
		var mylat = json[i].geo_lat;
		var mylatlong = new google.maps.LatLng(mylat,mylng,13);

		var myphoto = '';
		if (OxpointsShowPics == 1 && json[i].foaf_depiction)
		{
		    myphoto = json[i].foaf_depiction[0].uri;
		}

		var mylink = '';
		if (OxpointsShowHomepage == 1 && json[i].foaf_homepage)
		{
		    mylink = json[i].foaf_homepage;
		}
		
		// add the point to the map!
		var marker = createMarker(mylatlong,myname,mydesc,myaddr,mytype,myid,myphoto,mylink,map,infoWindow);
		//    alert(mylatlong + " " + myname + " " + mydesc + " " + mytype);
		
		// and add it to the points array
		allPoints[allPoints.length] = mylatlong;
		
		// and add it to the sidebar arrays
		var next = nameList.length;
		nameList[next] = myname;
		nameID[myname] = myid;
	    }

	}

    }

    // alert(gMarkers.length);

    var averagePoint = getCenter(allPoints);
    map.setCenter(averagePoint);

    if ( /^\d+$/.test(openPin) && openPin in gMarkers ) { showPlace(openPin); }

    // if there's a sidebar element, populate it with a list of clickable links for each marker

    var sideBar = document.getElementById("oxpoints-sidebar");
    
    if ( sideBar )
    {
	var mapList = document.createElement("ul");
	mapList.setAttribute("id","oxpoints-maplist");

	nameList.sort();
	
	for (i = 0; i < nameList.length; i++)
	{
	    var myname = nameList[i];
	    var myid = nameID[myname];
	    var listItem = document.createElement("li");
	    listItem.innerHTML = '<a class="oxpSideLink" href="#' + myid + '" onclick="showPlace(\'' + myid + '\')">' + myname + '</a>';
	    mapList.appendChild(listItem);
	}

	sideBar.appendChild(mapList);
	
    }

}

function getCenter(points) {

    var allLat = 0;
    var allLng = 0;

    for (i = 0; i < points.length; i++)
    {
	var myLatLng = points[i];
	var myLat = myLatLng.lat();
	var myLng = myLatLng.lng();

	allLat += myLat;
	allLng += myLng;

    }

    var avLat = allLat / points.length;
    var avLng = allLng / points.length;
    var avLatLng = new google.maps.LatLng(avLat, avLng);

    return avLatLng;
}

// create a marker with the appropriate icon

function createMarker(point, name, desc, addr, type, id, photo, link, map, infow) {

    var thisImage;
    var photoLink;
    var homeLink;
    
    if (type != '') 
    {
	thisImage = OxpointsImageRoot + type + ".png";
    }
    else
    {
	thisImage = OxpointsImageRoot + "Default.png";
    }

    if (photo != '')
    {
	photoLink = '<p class="infoWindow_img"><img class="infoWindow_img" src="' + photo + '" alt="' + name + '" /></p>';
    }
    else 
    {
	photoLink = '';
    }

    if (link != '')
    {
	homeLink = '<p class="infoWindow_link"><a href="' + link + '">' + link + '</a></p>';
    }
    else 
    {
	homeLink = '';
    }

    // (note - need to standardise size/shadow/anchor so that this *does* 
    // work for all icons... or allow user-provided json config file as well)

    /* actually... we need to not resize the marker icons at all, & let users 
       have huge icons if they want, but supply sensible defaults. This resizing
       is a temporary fix while Google updates its cache. 

       NB: http://stackoverflow.com/questions/7842730/change-marker-size-in-google-maps-v3
    */

    var markerImage = new google.maps.MarkerImage(thisImage,
						  null,
						  null,
						  null,
						  new google.maps.Size(20,20));

    //    markerOptions = { icon: thisImage, map: map, position: point };
    markerOptions = { icon: markerImage, map: map, position: point };

    var marker = new google.maps.Marker(markerOptions);
    var windowContent = '<p class="infoWindow_name"><strong>' + name + '</strong></p><p class="infoWindow_address">' + addr + '</p>' + desc + homeLink + photoLink;

    google.maps.event.addListener(marker, "click", function() {

	infow.setContent(windowContent);
	infow.open(map,marker);

    });

    gMarkers[id] = marker;

    return (marker);

}

