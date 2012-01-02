#!/usr/bin/python

import webapp2
import logging
import urllib
import urlparse

from google.appengine.api import memcache
from google.appengine.api import urlfetch

from xml.dom.minidom import parseString
from django.utils import simplejson as json

class KmlToPointsServlet(webapp2.RequestHandler):
  def get(self):
    return self.post()

  def post(self):
    # get the kml specified as a param
    uri = self.request.get('uri')
    parsed_uri = urlparse.urlparse(uri)
    path = urllib.quote(parsed_uri.path)
    
    uri = urlparse.urlunparse((parsed_uri.scheme,
                               parsed_uri.netloc,
                               urllib.quote(parsed_uri.path),
                               urllib.quote(parsed_uri.params),
                               urllib.quote(parsed_uri.query),
                               urllib.quote(parsed_uri.fragment)))

    if not self.request.get('no_cache') == 'y':
      cached = memcache.get(uri)
      if cached:
        self.response.out.write(cached)
        return

    logging.warning('uri: %s' % uri)
    response = urlfetch.fetch(url=uri, method=urlfetch.GET)
    logging.warning('response: %d (%s)' % (response.status_code, uri))
    if response.status_code == 200:
      dom = parseString(response.content)
      line = dom.getElementsByTagName('LineString')[0]
      coords = line.getElementsByTagName('coordinates')[0].childNodes[0].nodeValue
      coord_return = []
      for coord in coords.split('\n'):
        coord_array = coord.split(',')
        if len(coord_array) >= 2:
          coord_return.append([coord_array[0].strip(), coord_array[1].strip()])

      json_str = json.dumps(coord_return)
      memcache.add(uri, json_str)
      self.response.out.write(json_str)
    else:
      self.response.set_status(response.status_code)

app = webapp2.WSGIApplication([('/points', KmlToPointsServlet)], debug=True)
