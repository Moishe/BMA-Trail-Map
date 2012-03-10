var polyByArea = [];
var selectedPolys = [];
var map;
var areas;
var trails = {};

function trailDataReceived(trailResponse) {
  var infoWindow = new google.maps.InfoWindow();
  var bounds = new google.maps.LatLngBounds();
  var boundsByArea = {};
  for (i = 0; i < trailResponse.length; i++) {
    var trail = trailResponse[i];
    if (trail.points) {
      if (!boundsByArea[trail.area]) {
        boundsByArea[trail.area] = new google.maps.LatLngBounds();
      }

      trails[trail.id] = trail;
      var points = [];
      for (var j = 0; j < trail.points.length; j++) {
        var p = new google.maps.LatLng(trail.points[j][0],
                                       trail.points[j][1]);
        points.push(p);
        bounds.extend(p);
        boundsByArea[trail.area].extend(p);
      }

      if (trail.condition == '1') {
        color = '#FF0000';
      } else if (trail.condition == '2') {
        color = '#FFA500';
      } else if (trail.condition == '3') {
        color = '#00FF00';
      } else {
        color = '#888888';
      }

      var poly = new google.maps.Polyline({
        path: points,
        strokeColor: color,
        strokeOpacity: 0.7,
        strokeWeight: 4
      });

      addInfoWindowHandlers(infoWindow, map, poly, color, trail);
      poly.setMap(map)
      
      if (polyByArea[trail.area]) {
        polyByArea[trail.area].push(poly);
      } else {
        polyByArea[trail.area] = [poly];
      }
    }
  }
  /*
  for (var area in boundsByArea) {
    var areaBounds = boundsByArea[area];
    var rect = new google.maps.Rectangle({
      bounds: areaBounds,
      fillColor: '#FFFF00',
      fillOpacity: 0.1,
      strokeColor: '#333333',
      strokeOpacity: 0.3,
      strokeWeight: 0.5,
    });
    rect.setMap(map);
    addClickListener(rect, areaBounds);
  }
  */

  map.fitBounds(bounds);
}

function addClickListener(rect, areaBounds) {
  google.maps.event.addListener(rect,
                                'click',
                                function(event) {
                                  map.fitBounds(areaBounds);
				  return true;
                                });
}

function trailConditionsReceived(conditions) {
  var i;
  for (i = 0; i < conditions.response.trails.length; i++) {
    trails[conditions.response.trails[i].trailId].conditionDetails = conditions.response.trails[i];
  }
}

function showInfoWindow(infoWindow, trail, poly, latLng) {  
  if (trail.conditionDetails && trail.conditionDetails.comment) {
    description = trail.conditionDetails.comment;
  } else {
    description = trail.description;
  }
  if (description.length > 256) {
    description = description.substring(0, 256);
    description += '...';
  }
  var div = $('<div/>', {class: 'infobox'});
  var desc = $('<div class="trail-desc"/></div>').appendTo(div);
  var header = $('<h1><a href="#">' + trail.name + '</a></h1>').appendTo(desc);
  header.click(function() {window.open(trail.url)});
  $('<div>' + description + '</div>').appendTo(desc);
  var stats = $('<div class="trail-stats"><h1>Trail Ratings</h1></div>').appendTo(div);
  $('<div>T: ' + trail.techRating + ' A: ' + trail.aerobicRating + ' C: ' + trail.coolRating + '</div>').appendTo(stats);
  $('<h1>Trail Length:</h1>').appendTo(stats);
  $('<div>' + trail.length + ' miles</div>').appendTo(stats);
  $('<h1>Elevation Gain:</h1>').appendTo(stats);
  $('<div>' + trail.elevationGain + ' ft.</div>').appendTo(stats);
  
    
  header.click(function() {window.open(trail.url)});
  
  infoWindow.setContent(div.get()[0]);

  infoWindow.setPosition(latLng);
  poly.setOptions({strokeColor: '#FFFF00'});
  infoWindow.open(map);
}

function addInfoWindowHandlers(infoWindow, map, poly, color, trail) {
  google.maps.event.addListener(infoWindow,
                                'closeclick',
                                function() {
                                  poly.setOptions({strokeColor: color});
                                });

  google.maps.event.addListener(poly,
                                'click',
                                function(event) {
                                  showInfoWindow(infoWindow, trail, poly, event.latLng);
                                });
}

function initializeMap(areaId, skip_cache) {
  var latlng = new google.maps.LatLng(40.0, -105.26);
  var myOptions = {
    zoom: 11,
    center: latlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  map = new google.maps.Map(document.getElementById("map_canvas"),
                            myOptions);

  // If we got map data in our initial payload, use it. Otherwise
  // make an ajax request to get it.
  trailData = $('#cached_trails').text();
  if (trailData) {
    trailDataReceived(JSON.parse(trailData));
  } else {
    // TODO (moishel): add a spinner or something to indicate trail data's loading.
    $.ajax({url: '/v1/regions/1/trails?jsonp=trailDataReceived&skip_cache=' + skip_cache});
  }

  $.ajax({url: '/v1/regions/1/conditions?jsonp=trailConditionsReceived'});
}

