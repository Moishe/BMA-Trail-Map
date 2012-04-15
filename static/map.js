var polyByArea = [];
var selectedPolys = [];
var map;
var areas;
var trails = {};
var conditions = {};
var infoWindow = new google.maps.InfoWindow();
var prevPoly;
var prevColor;
var trail_canvas_buffer = 0;

function trailDataReceived(trailResponse) {
  try {
  var bounds = new google.maps.LatLngBounds();
  var boundsByArea = {};
  for (i = 0; i < trailResponse.length; i++) {
    var trail = trailResponse[i];
    if (trail.points) {
      if (!boundsByArea[trail.area]) {
        boundsByArea[trail.area] = new google.maps.LatLngBounds();
      }

      trails[trail.id] = trail;

      var poly = drawTrailPoints(trail,
                                 {
                                   strokeColor: '#000000',
                                   strokeOpacity: 1,
                                   strokeWeight: 0.5,
                                   zIndex: 99
                                 }, bounds);
      poly.setMap(map);

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
  } catch (e) {
    console.log(e.message);
  }
  $.ajax({url: '/v1/regions/1/conditions?jsonp=trailConditionsReceived'});
}

function addClickListener(rect, areaBounds) {
  google.maps.event.addListener(rect,
                                'click',
                                function(event) {
                                  map.fitBounds(areaBounds);
				                          return true;
                                });
}

function drawTrailPoints(trail, options, optBounds) {
  var points = [];
  for (var j = 0; j < trail.points.length; j++) {
    var p = new google.maps.LatLng(trail.points[j][0],
                                   trail.points[j][1]);
    points.push(p);
    if (optBounds) {
      optBounds.extend(p);
    }
  }

  options.path = points;
  var poly = new google.maps.Polyline(options);

  poly.setMap(map);

  return poly;
}

function trailConditionsReceived(receivedConditions) {
  try{
    var i;
    for (i = 0; i < receivedConditions.response.conditions.length; i++) {
      condition = receivedConditions.response.conditions[i];
      trailId = condition.trailId;
      if (!conditions[trailId] ||
	        (parseInt(conditions[trailId].updatedAt) <
	         parseInt(condition.updatedAt))) {
        conditions[trailId] = condition;

        var trail = trails[trailId];
        if (trail) {
          var date = new Date(parseInt(condition.updatedAt) * 1000);
          var today = new Date();
          var diff = today.getTime() - date.getTime();
          var days = Math.floor(diff / (1000 * 60 * 60 * 24));

          if (condition.conditionId == '1') {
            color = '#FF0000';
          } else if (condition.conditionId == '2') {
            color = '#FFA500';
          } else if (condition.conditionId == '3') {
            color = '#00FF00';
          } else {
            color = '#888888';
          }

          poly = drawTrailPoints(trail,
                          {
                            strokeColor: color,
                            strokeOpacity: 0.5,
                            strokeWeight: 5,
                            zIndex: 10
                          });

          if (days < 7) {
            animatePoly = drawTrailPoints(trail,
                                          {strokeColor: '#FFFF00',
                                           zIndex: 5,
                                           opacity: 1.0,
                                           strokeWeight: 0});
            animatePolyInfo(animatePoly, color, 0);
          }
          addInfoWindowHandlers(infoWindow, map, poly, color, trail);
        }
      }
    }
    setTimeout(function() {
      setTimeout(animatePolyStep, 10);
    }, 1000);
  } catch (e) {
    console.log(e.message);
  }
}

var polysToAnimate = [];
function animatePolyInfo(poly, color, opacity) {
  polysToAnimate.push({poly: poly,
                       goalColor: color,
                       goalOpacity: opacity,
                       step: 0,
                       currentColor: color,
                       currentOpacity: 0});
}

function RGBtoHex(R,G,B) {return toHex(R)+toHex(G)+toHex(B)}
function toHex(N) {
  if (N==null) return "00";
  N=parseInt(N); if (N==0 || isNaN(N)) return "00";
  N=Math.max(0,N); N=Math.min(N,255); N=Math.round(N);
  return "0123456789ABCDEF".charAt((N-N%16)/16)
    + "0123456789ABCDEF".charAt(N%16);
}

function animatePolyStep() {
  if (polysToAnimate.length > 0) {
    var newPolysToAnimate = [];
    for (var i = 0; i < polysToAnimate.length; i++) {
      animateInfo = polysToAnimate[i];
      var opacity;
      var color;
      var steps = 20.0;
      if (animateInfo.step < (steps * 2)) {
        var virtualStep = animateInfo.step;
        if (animateInfo.step > steps / 2) {
          virtualStep = steps / 2 - (animateInfo.step - (steps / 2))
        }
        color = '#FFFF00'
        opacity = 1.0 - ((virtualStep / steps) * 1.0);
        animateInfo.step += 1;
        weight = (virtualStep / steps) * 30;
        newPolysToAnimate.push(animateInfo);
      } else {
        color = '#FFFF00'
        opacity = 0.5
        weight = 5;
      }
      animateInfo.poly.setOptions({
        strokeOpacity: opacity,
        strokeWeight: weight
      });
    }
    polysToAnimate = newPolysToAnimate;
    setTimeout(animatePolyStep, 10);
  }
}

function showInfoWindow(infoWindow, trail, poly, latLng, color) {
  if (prevPoly == poly) {
    return;
  }

  var description = '';
  if (conditions[trail.id]) {
    condition = conditions[trail.id];
    var date = new Date(parseInt(condition.updatedAt) * 1000);
    var today = new Date();
    var diff = today.getTime() - date.getTime();
    var days = Math.floor(diff / (1000 * 60 * 60 * 24));
    var daysAgo;
    if (days <= 0) {
      daysAgo = "today";
    } else {
      days + " days ago";
    }
    description = condition.nickname + " updated " + daysAgo + "<br/>";
    description += "<b>" + condition.comment + "</b><p/>";
  } else {
    description = trail.description;
  }
  
  if (description.length > 256) {
    description = description.substring(0, 256);
    description += '...';
  }
  var div = $('<div id="infobox"/>');
  div.addClass('infobox');
  var header = $('<h2><a href="#">' + trail.name + '</a></h1>').appendTo(div);
  header.click(function() {window.open(trail.url)});
  var stats = $('<div class="trail-stats"><h1>Trail Ratings</h1></div>').appendTo(div);
  $('<div>T: ' + trail.techRating + ' A: ' + trail.aerobicRating + ' C: ' + trail.coolRating + '</div>').appendTo(stats);
  $('<h1>Trail Length:</h1>').appendTo(stats);
  $('<div>' + trail.length + ' miles</div>').appendTo(stats);
  $('<h1>Elevation Gain:</h1>').appendTo(stats);
  $('<div>' + trail.elevationGain + ' ft.</div>').appendTo(stats);
  var desc = $('<div class="trail-desc"/></div>').appendTo(div);
  $('<div>' + description + '</div>').appendTo(desc);

  $('#trail_canvas-' + trail_canvas_buffer).hide();
  trail_canvas_buffer = (trail_canvas_buffer + 1) % 2;
  current_trail_canvas = '#trail_canvas-' + trail_canvas_buffer;
  $(current_trail_canvas).empty();
  div.appendTo($('#trail_canvas-' + trail_canvas_buffer));
  $(current_trail_canvas).show();
  
  poly.setOptions({strokeColor: '#FFFF00'});
  if (prevPoly) {
    prevPoly.setOptions({strokeColor: prevColor});
  }
  prevColor = color;
  prevPoly = poly;

/*
    
  infoWindow.setContent(div.get()[0]);

  infoWindow.setPosition(latLng);
  infoWindow.open(map);
*/
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
                                  showInfoWindow(infoWindow, trail, poly, event.latLng, color);
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
    var url;
    if (areaId) {
      url = '/v1/areas/' + areaId + '/trails?jsonp=trailDataReceived&skip_cache=' + skip_cache;
    } else {
      url = '/v1/regions/1/trails?jsonp=trailDataReceived&skip_cache=' + skip_cache;
    }
    $.ajax({url: url});
  }
}

