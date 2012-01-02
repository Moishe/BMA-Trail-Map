#!/usr/bin/python

import logging
import urllib
import urlparse

from google.appengine.api import memcache
from google.appengine.api import urlfetch

from xml.dom.minidom import parseString

class BuildPoints():
  def __init__(self, use_cache = True):
    self.use_cache = use_cache

  def makeUri(self, filepath):
    uri = urlparse.urlunparse(('http',
                               'bouldermountainbike.org',
                               urllib.quote(filepath),
                               '',
                               '',
                               ''))
    return uri


  def fromGpx(self, filepath):
    points = None
    uri = self.makeUri(filepath)

    if self.use_cache:
      points = memcache.get(uri)
      if points: return points

    logging.warning('Not using cache for points: %s' % uri)
      
    try:
      result = urlfetch.fetch(uri)
    except ValueError:
      logging.error('result too big; ignoring.')
      return None


    if result.status_code == 200:
      points = []
      dom = parseString(result.content)
      for el in dom.getElementsByTagName('trkpt'):
        points.append({'lat': el.getAttribute('lat'),
                       'lon': el.getAttribute('lon')})

    memcache.add(uri, points)

    return points

  def fromKml(self, filepath):
    points = None
    uri = self.makeUri(filepath)

    if self.use_cache:
      points = memcache.get(uri)
      if points: return points

    logging.warning('Not using cache for points: %s' % uri)

    try:
      result = urlfetch.fetch(url=uri, method=urlfetch.GET)
    except ValueError:
      logging.error('result too big; ignoring.')
      return

    if result.status_code == 200:
      dom = parseString(result.content)
      line = dom.getElementsByTagName('LineString')[0]
      coords = line.getElementsByTagName('coordinates')[0].childNodes[0].nodeValue
      coord_return = []
      for coord in coords.split('\n'):
        coord_array = coord.split(',')
        if len(coord_array) >= 2:
          coord_return.append([coord_array[0].strip(), coord_array[1].strip()])

      json_str = json.dumps(coord_return)

    memcache.add(uri, points)

    return points
    
