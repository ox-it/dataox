/* *******************************************************/
/*                                                       */
/* oxpointsMap.js - written by Janet McKnight, July 2009 */
/*                                                       */
/* *******************************************************/ 

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

var OxpointsMapCenter = new GLatLng(51.757191,-1.26219); // or calculate this based on points?

// default root directory for images - this can be overridden by the user

var OxpointsImageRoot = 'http://www.oucs.ox.ac.uk/oxpoints/images/typeicons/'; // include trailing slash

// default setting for photos (off). This can be overridden by the user
// by setting to 1.

var OxpointsShowPics = 0;

// default setting for homepage link (on). This can be overridden by the user
// by setting to 0.

var OxpointsShowHomepage = 1;

// default setting for Google Maps link (off). This can be overridden by the user
// by setting to 1.

var OxpointsShowGMapLink = 0;

// set up OSM map tiles and make it the default initial map type

var CustomGetTileUrl = function(a,b){

    return 'http://a.tile.openstreetmap.org/'+b+'/'+a.x+'/'+a.y+'.png';
    
}

var copyright = new GCopyright(1, new GLatLngBounds(new GLatLng(53.8136257,-3.0981445),
						    new GLatLng(53.8654855,-2.9663944) ),
			       17, "");

var copyrightCollection = new GCopyrightCollection('');
copyrightCollection.addCopyright(copyright);

var tilelayers = [new GTileLayer(copyrightCollection,1,17)];
tilelayers[0].getTileUrl = CustomGetTileUrl;
var osmmap = new GMapType(tilelayers, G_SATELLITE_MAP.getProjection(), "OSM");

var OxpointsInitialMapType = osmmap;

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
		OxpointsShowGMapLink = 1; gMapLinkText = oxpUserOptions.showGMapLink; 
	}
	else { OxpointsShowGMapLink = 0 }    
    }
    else { OxpointsShowGMapLink = 0 }    
}

/* ******************************** functions ****************************/

// showPlace function for sidebar items

var gMarkers = [];

function showPlace(s) {
    //    alert(gMarkers[s]);
    GEvent.trigger(gMarkers[s], "click");
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

    // while we've got a handle on the oxpoints URL, create the KML
    // equivalent and add it to the maps div (if this option is set)

    if (OxpointsShowGMapLink == 1)
    {
	var oxp_kml = oxp_url.replace(/\.js.*$/, ".kml");
	var mapDiv = document.getElementById("oxpoints-map");
	var gMapLink = document.createElement("a");
	gMapLink.setAttribute("href","http://maps.google.co.uk/?q="+oxp_kml+"&z="+OxpointsInitialZoom);
	gMapLink.innerHTML = gMapLinkText;
	var gMapLinkSpan = document.createElement("span");
	gMapLinkSpan.setAttribute("class","oxpoints-gmap-link");
	gMapLinkSpan.appendChild(gMapLink);
	mapDiv.parentNode.appendChild(gMapLinkSpan);
    }

}

// the main function, executed on callback

function oxpoints(json) {

    // initialise the map

    var map = new google.maps.Map2(document.getElementById("oxpoints-map"));

    map.setUIToDefault();
    map.setCenter(OxpointsMapCenter, OxpointsInitialZoom);

    map.addMapType(osmmap);

//    * G_NORMAL_MAP displays the default road map view
//    * G_SATELLITE_MAP displays Google Earth satellite images
//    * G_HYBRID_MAP displays a mixture of normal and satellite views
//    * G_DEFAULT_MAP_TYPES contains an array of the above three types, useful for iterative processing.
//    * G_PHYSICAL_MAP displays a physical map based on terrain information. 

    if (OxpointsInitialMapType == 'normal')
    {
	map.setMapType(G_NORMAL_MAP);
    }
    else if (OxpointsInitialMapType == 'terrain')
    {
	map.setMapType(G_PHYSICAL_MAP);
    }
    else if (OxpointsInitialMapType == 'satellite')
    {
	map.setMapType(G_SATELLITE_MAP);
    }
    else if (OxpointsInitialMapType == 'hybrid')
    {
	map.setMapType(G_HYBRID_MAP);
    }
    else
    {
	map.setMapType(osmmap);
    }

    // nameList = list of names of points, to be sorted alphabetically
    // nameID = associative array of name => ID - needed for sidebar

    var nameList = new Array;
    var nameID = new Array;
    var allPoints = new Array;
    var missingList = new Array;
    var bounds = new GLatLngBounds();
    
    // loop through Placemark to get points
    
    for (i = 0; i < json.length; i++)
    {
	if ( json[i] ) 
	{ 

	    // get all the relevant data out of the JSON
	    if ( json[i].geo_long && json[i].geo_lat )
   	    {

		var myid = json[i].uri;
		myid = myid.replace('http://oxpoints.oucs.ox.ac.uk/id/','');
		var myname = json[i].dc_title;
		if ( typeof myname == "undefined" ) { myname = '[No name]' }
		var mytype = json[i].type;
		if ( mytype.match(/#/) ) 
		    {
			// e.g. http://ns.ox.ac.uk/namespace/oxpoints/2009/02/owl#Site
			mytype = mytype.split('#')[1];
		    }
		else
		    {
			// e.g. http://xmlns.com/foaf/0.1/Group
			var mytypeSplit = mytype = mytype.split('/');
			mytype = mytypeSplit[mytypeSplit.length-1];
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
		var mylatlong = new GLatLng(mylat,mylng,13);
		bounds.extend(mylatlong);

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
		map.addOverlay(createMarker(mylatlong,myname,mydesc,myaddr,mytype,myid,myphoto,mylink));
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

    // Don't go any closer than OxpointsInitialZoom, but go further away if things wouldn't fit.
    map.setZoom(Math.min(OxpointsInitialZoom, map.getBoundsZoomLevel(bounds)));

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
	    listItem.innerHTML = '<a class="oxpSideLink" href="#map" onclick="showPlace(\'' + myid + '\')">' + myname + '</a>';
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
    var avLatLng = new GLatLng(avLat, avLng);

    return avLatLng;
}

// create a marker with the appropriate icon

function createMarker(point, name, desc, addr, type, id, photo, link) {

    var thisIcon = new GIcon();
    var thisImage = "";
    
    if (type != '') 
    {
	thisImage = OxpointsImageRoot + type + ".png";
    }
    else
    {
	thisImage = OxpointsImageRoot + "Default.png";
    }

    var photoLink = "";
    if (photo != '')
    {
	photoLink = '<p class="infoWindow_img"><img class="infoWindow_img" src="' + photo + '" alt="' + name + '" /></p>';
    }

    var homeLink = "";
    if (link != '')
    {
	homeLink = '<p class="infoWindow_link"><a href="' + link + '">' + link + '</a></p>';
    }

    // (note - need to standardise size/shadow/anchor so that this *does* 
    // work for all icons... or allow user-provided json config file as well)

    thisIcon.image = thisImage;
    thisIcon.iconSize = new GSize(16, 18);
    thisIcon.iconAnchor = new GPoint(8, 18);
    thisIcon.infoWindowAnchor = new GPoint(16, 0);

    markerOptions = { icon:thisIcon };

    var marker = new GMarker(point, markerOptions);

    GEvent.addListener(marker, "click", function() {

	    marker.openInfoWindowHtml('<p class="infoWindow_name"><strong>' + name + '</strong></p><p class="infoWindow_address">' + addr + '</p>' + desc + homeLink + photoLink, {maxWidth:275,autoScroll:true});
    });

    gMarkers[id] = marker;

    return (marker);

}
