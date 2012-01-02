var polyByArea = [];
var selectedPolys = [];
var map;
var areas;

function trailDataReceived(trailResponse) {
  try {
    for (i = 0; i < trailResponse.length; i++) {
      var trail = trailResponse[i];
      if (trail.points) {
        var points = [];
        var bounds = new google.maps.LatLngBounds();
        for (var j = 0; j < trail.points.length; j++) {
          var p = new google.maps.LatLng(trail.points[j].lat,
                                         trail.points[j].lon);
          points.push(p);
          bounds.extend(p);
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

        addInfoWindow(map, poly, color, trail);
        poly.setMap(map)
        
        if (polyByArea[trail.area]) {
          polyByArea[trail.area].push(poly);
        } else {
          polyByArea[trail.area] = [poly];
        }
      }
    }
  } catch (err) {
    debugger;
    alert(err.description);
  }
}

function addInfoWindow(map, poly, color, trail) {
  description = trail.description;
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
  
    
  var infoWindow = new google.maps.InfoWindow(
    {content: div.get()[0]});

  google.maps.event.addListener(infoWindow,
                                'closeclick',
                                function() {
                                  poly.setOptions({strokeColor: color});
                                });

  google.maps.event.addListener(poly,
                                'click',
                                function(event) {
                                  infoWindow.setPosition(event.latLng);
                                  poly.setOptions({strokeColor: '#FFFF00'});
                                  infoWindow.open(map);
                                });

}

function initializeMap() {
  var latlng = new google.maps.LatLng(40.0, -105.26);
  var myOptions = {
    zoom: 11,
    center: latlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  map = new google.maps.Map(document.getElementById("map_canvas"),
                            myOptions);

  $.ajax({url: '/v1/regions/1/trails?jsonp=trailDataReceived'});
}

