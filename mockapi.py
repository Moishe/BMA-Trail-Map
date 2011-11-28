#!/usr/bin/python

import copy
import logging
import os

import webapp2
from django.utils import simplejson as json

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


class RegionsPage(webapp2.RequestHandler):
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


class TrailsByAreaPage(webapp2.RequestHandler):
  def get(self, area_id):
    return self.post(area_id)

  def post(self, area_id):
    trails = ReadTrailsFromFile()
    filtered_trails = filter(lambda x: str(x['trail']['areaId']) == area_id, trails)
    self.response.out.write(json.dumps(ResponseFromTrails(filtered_trails)))

class TrailsByRegionPage(webapp2.RequestHandler):
  def get(self, region_id):
    return self.post(region_id)

  def post(self, region_id):
    trails = ReadTrailsFromFile()
    self.response.out.write(json.dumps(ResponseFromTrails(trails)))

class TrailsPage(webapp2.RequestHandler):
  def post(self, trail_id):
    self.response.out.write(json.dumps(SAMPLE_TRAIL_1))

class AreasByRegionPage(webapp2.RequestHandler):
  def get(self, region_id):
    return self.post(region_id)

  def post(self, region_id):
    areas = ReadAreasFromFile()
    self.response.out.write(json.dumps(ResponseFromAreas(areas)))

app = webapp2.WSGIApplication([('/v1/trails/([^/]+)$', TrailsPage),
                               ('/v1/area/([^/]+)/trails$', TrailsByAreaPage),
                               ('/v1/regions$', RegionsPage),
                               ('/v1/regions/([^/]+)/areas$', AreasByRegionPage),
                               ('/v1/regions/([^/]+)/trails$', TrailsByRegionPage)], debug=True)
