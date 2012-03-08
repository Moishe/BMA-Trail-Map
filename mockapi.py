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
    json_str = self.get_json(id)
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


def GetPointsForTrail(trail):
  # First, see if there's an entry in memcache for this trail
  logging.info('Looking up %s in memcache' % trail['id'])
  cached_trail = memcache.get(trail['id'])
  if cached_trail:
    (timestamp, points) = cached_trail
  else:
    timestamp = None
    points = None

  # Next, see if there's something more recent than what we got from memcache.
  if type(trail['files'] == dict):
    files_by_extension = {}
    file_to_load = None
    file_timestamp = None
    for file_id in trail['files']:
      file = trail['files'][file_id]
      file_timestamp = int(file['timestamp'])
      file_extension = file['filepath'].split('.')[-1]
      if file_timestamp > timestamp and file_extension in ['gpx','kml']:
        file_to_load = file['filepath']

    if timestamp and points and file_timestamp <= timestamp:
      logging.info('Returning points from memcache.')
      return points

    if file_to_load:
      # Before we do an urlfetch, see if this trail is in our datastore.
      trail_points = TrailPoints.get_by_key_name(trail['id'])
      if trail_points:
        logging.info('Found trail_points, %d, %d' % (trail_points.timestamp, file_timestamp))
      else:
        logging.info('Couldn\'t find trail_points %s' % (trail['id']))

      if trail_points and trail_points.timestamp >= file_timestamp:
        logging.info('Found %s in datastore' % trail['id'])
        points = json.loads(trail_points.points)
        memcache.add(trail['id'], [trail_points.timestamp, points])
        return points
      
      uri = 'http://xmltopoints.appspot.com/getpoints?uri=' + MakeFileUri(file_to_load)
      result = urlfetch.fetch(url=uri)
      
      if result and result.status_code == 200:
        points = json.loads(result.content)
        memcache.add(trail['id'], [file_timestamp, points])

        trail_points = TrailPoints(timestamp=file_timestamp,points=result.content,key_name=trail['id'])
        logging.info('Adding (%d,%s) to datastore' % (file_timestamp, trail['id']))
        trail_points.put()
        return points
  else:
    logging.info('Returning points from memcache.')
    return points

  return None


def ExtractGxpAndInsertPoints(trails_json):
  trails = json.loads(trails_json)['response']['trails']
  for trail in trails:
    trail['points'] = GetPointsForTrail(trail)

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

  def get_json(self, region_id):
    uri = self.get_query_uri(region_id)
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

    json_str = ExtractGxpAndInsertPoints(content)
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

  def get_json(self, area_id):
    uri = self.get_query_uri(area_id)
    logging.warning('Getting %s' % uri)
    result = urlfetch.fetch(url=uri, method=urlfetch.GET)
    if result.status_code == 200:
      content = result.content

    json_str = ExtractGxpAndInsertPoints(content)
    return json_str


class ConditionsByRegionPage(JSONPHandler):
  def get_json(self, region_id):
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

