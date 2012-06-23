#!/usr/bin/python

import copy
import logging
import os
import urllib
import urlparse
import webapp2

from xml.dom.minidom import parseString
from django.utils import simplejson as json

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import urlfetch

BMA_SCHEME = 'http'
BMA_DOMAIN = 'bouldermountainbike.org'

class JSONPHandler(webapp2.RequestHandler):
  def get(self, id):
    return self.post(id)

  def post(self, id):
    json_str = self.get_json(id, self.request.get('skip_cache', 'n') == 'y')
    jsonp = self.request.get('jsonp')
    if jsonp:
      self.response.headers['Content-Type'] = 'application/javascript'
      self.response.out.write('%s(%s);'% (jsonp, json_str))
    else:
      self.response.out.write(json_str)


def MakeFileUri(filepath):
  uri = urlparse.urlunparse((BMA_SCHEME,
                             BMA_DOMAIN,
                             urllib.quote(filepath),
                             '',
                             '',
                             ''))
  return uri


class TrailPoints(db.Model):
  timestamp = db.IntegerProperty()
  points = db.TextProperty()


def GetPointsForTrail(trail, skip_cache, timestamp=None, points=None):
  # Next, see if there's something more recent than what we got from memcache.
  if type(trail['files'] == dict):
    file_to_load = None
    file_timestamp = None
    for file_id in trail['files']:
      file = trail['files'][file_id]
      file_timestamp = int(file['timestamp'])
      file_extension = file['filepath'].split('.')[-1]
      if file_timestamp > timestamp and file_extension in ['gpx','kml', 'kmz']:
        file_to_load = file['filepath']

    if timestamp and points and file_timestamp <= timestamp:
      return (points, None)

    if file_to_load:
      # Before we do an urlfetch, see if this trail is in our datastore.
      if not skip_cache:
        trail_points = TrailPoints.get_by_key_name(trail['id'])
        if trail_points and trail_points.timestamp >= file_timestamp:
          points = json.loads(trail_points.points)
          memcache.add(trail['id'], [trail_points.timestamp, points])
          return (points, None)
      
      uri = 'http://4.xmltopoints.appspot.com/getpoints?uri=' + MakeFileUri(file_to_load)
      rpc = urlfetch.create_rpc()
      urlfetch.make_fetch_call(rpc, uri)
      logging.warning('Retrieving: ' + uri)
      return (None, rpc, file_timestamp)
      
      if result and result.status_code == 200:
        return (points, None)
  else:
    return (points, None)

  return None


def ExtractGxpAndInsertPoints(trails_json, skip_cache):
  trails = json.loads(trails_json)['response']['trails']
  cache_get = []
  for trail in trails:
    cache_get.append(trail['id'])

  trail_points = memcache.get_multi(cache_get)

  for trail in trails:
    if trail['id'] in trail_points:
      (timestamp, points) = trail_points[trail['id']]
      trail['points'] = GetPointsForTrail(trail, skip_cache, timestamp, points)
    else:
      trail['points'] = GetPointsForTrail(trail, skip_cache)

  for trail in trails:
    if not trail['points']:
      continue

    if trail['points'][1]:
      result = trail['points'][1].get_result()
      file_timestamp = trail['points'][2]
      if result.status_code == 200:
        points = json.loads(result.content)
        memcache.add(trail['id'], [file_timestamp, points])

        trail_points = TrailPoints(timestamp=file_timestamp,points=result.content,key_name=trail['id'])
        trail_points.put()
        trail['points'] = points
    else:
      trail['points'] = trail['points'][0]

  return json.dumps(trails)


class TrailsByRegionPage(JSONPHandler):
  def get_query_uri(self, region_id):
    uri = urlparse.urlunparse((BMA_SCHEME,
                               BMA_DOMAIN,
                               urllib.quote('/trailsAPI/regions/%s/trails' % region_id),
                               '',
                               '',
                               ''))
    return uri

  def get_json(self, region_id, skip_cache):
    uri = self.get_query_uri(region_id)
    if skip_cache:
      cached = None
    else:
      cached = memcache.get(uri)
    if cached:
      content = cached
    else:
      logging.info('Getting: %s' % uri)
      result = urlfetch.fetch(url=uri, method=urlfetch.GET)
      if result.status_code == 200:
        content = result.content
        memcache.add(uri, content)
      else:
        return None

    json_str = ExtractGxpAndInsertPoints(content, skip_cache)
    return json_str


class TrailsByAreaPage(JSONPHandler):
  def get_query_uri(self, area_id):
    uri = urlparse.urlunparse((BMA_SCHEME,
                               BMA_DOMAIN,
                               urllib.quote('/trailsAPI/areas/%s/trails' % area_id),
                               '',
                               '',
                               ''))
    return uri

  def get_json(self, area_id, skip_cache):
    uri = self.get_query_uri(area_id)
    logging.warning('Getting %s' % uri)
    result = urlfetch.fetch(url=uri, method=urlfetch.GET)
    if result.status_code == 200:
      content = result.content

    json_str = ExtractGxpAndInsertPoints(content, skip_cache)
    return json_str


class ConditionsByRegionPage(JSONPHandler):
  def get_json(self, region_id, skip_cache):
    uri = urlparse.urlunparse((BMA_SCHEME,
                               BMA_DOMAIN,
                               urllib.quote('/trailsAPI/regions/%s/conditions' % region_id),
                               '',
                               '',
                               ''))
    result = urlfetch.fetch(url=uri, method=urlfetch.GET)
    if result.status_code == 200:
      return result.content

    return None


app = webapp2.WSGIApplication([('/v1/regions/([^/]+)/conditions$', ConditionsByRegionPage),
                               ('/v1/areas/([^/]+)/trails', TrailsByAreaPage),
                               ('/v1/regions/([^/]+)/trails$', TrailsByRegionPage)], debug=True)

