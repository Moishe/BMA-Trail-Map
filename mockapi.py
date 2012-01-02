#!/usr/bin/python

import buildpoints
import copy
import logging
import os
import webapp2

from xml.dom.minidom import parseString
from django.utils import simplejson as json

from google.appengine.api import memcache
from google.appengine.api import urlfetch

REGION_RESPONSE = {
  "meta": {
    "code": 200
    },
  "response": {
    "regions": [
      {
        "allowed": [
          "all"
          ],
        "id": "1",
        "name": "Boulder, CO",
        "sponsorAlertsUrl": "http://bma.geozen.com/alerts/2011/index.html",
        "sponsorId": "4def87fa7dcabb18dd36f524",
        "sponsorName": "Boulder Mountainbike Alliance",
        "sponsorTwitter": [
          "#boco_trails",
          "#valmontbikepark",
          "boulderbma"
          ],
        "updatedAt": 1317752573419.0
        }
      ]
    }
  }


BMA_DOMAIN = 'http://bouldermountainbike.org'


class RegionsPage(webapp2.RequestHandler):
  def get(self):
    return self.post()

  def post(self):
    self.response.out.write(json.dumps(REGION_RESPONSE))

def ResponseFromTrails(trails):
    response = {
      'meta': {'code': 200},
      'response': {'trails': []}
      }

    for trail in trails:
      trail_response = {
        'meta': {'code': 200},
        'response': trail
        }
      response['response']['trails'].append(trail_response)

    return response


def ResponseFromAreas(areas):
  response = {
    'meta': {'code': 200},
    'response': {'areas': areas}
    }

  return response


def ReadTrailsFromFile():
  path = os.path.join(os.path.dirname(__file__), 'trails')
  return json.loads(open(path).read())


def ReadAreasFromFile():
  path = os.path.join(os.path.dirname(__file__), 'areas')
  return json.loads(open(path).read())


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


class TrailsByAreaPage(JSONPHandler):
  def get_json(self, area_id):
    uri = 'http://bouldermountainbike.org/trailsAPI/areas/%s/trails' % region_id
    cached = memcache.get(uri)
    if cached: return cached

    result = urlfetch.fetch(url=url, method=urlfetch.GET)
    if result.status_code == 200:
      json_str = ExtractGxpAndInsertPoints(result.content)
      memcache.add(uri, json_str)
    else:
      return None

def ExtractGxpAndInsertPoints(trails_json):
  trails = json.loads(trails_json)['response']['trails']
  for trail in trails:
    if type(trail['files'] == dict):
      files_by_extension = {}
      for file in trail['files']:
        filepath = trail['files'][file]['filepath']
        files_by_extension[filepath.split('.')[-1]] = filepath

      if 'gpx' in files_by_extension:
        trail['points'] = buildpoints.BuildPoints().fromGpx(files_by_extension['gpx'])
      elif 'kml' in files_by_extension:
        trail['points'] = buildpoints.BuildPoints().fromKml(files_by_extension['kml'])

  return json.dumps(trails)


class TrailsByRegionPage(JSONPHandler):
  def get_json(self, region_id):
    uri = 'http://bouldermountainbike.org/trailsAPI/regions/%s/trails' % region_id
    cached = memcache.get(uri)
    if cached:
      content = cached
    else:
      result = urlfetch.fetch(url=uri, method=urlfetch.GET)
      if result.status_code == 200:
        content = result.content
        memcache.add(uri, content)
      else:
        return None

    json_str = ExtractGxpAndInsertPoints(content)
    return json_str

class TrailsPage(JSONPHandler):
  def get_json(self, trail_id):
    return SAMPLE_TRAIL_1

class AreasByRegionPage(JSONPHandler):
  def get_json(self, id):
    uri = '%s/trailsAPI/regions/%s/areas' % (BMA_DOMAIN, id)
    cached = memcache.get(uri)
    if cached: return cached

    result = urlfetch.fetch(url=uri, method=urlfetch.GET)
    if result.status_code == 200:
      memcache.add(uri, result.content)
      return result.content
    else:
      return None


app = webapp2.WSGIApplication([('/v1/trails/([^/]+)$', TrailsPage),
                               ('/v1/area/([^/]+)/trails$', TrailsByAreaPage),
                               ('/v1/regions$', RegionsPage),
                               ('/v1/regions/([^/]+)/areas$', AreasByRegionPage),
                               ('/v1/regions/([^/]+)/trails$', TrailsByRegionPage)], debug=True)

