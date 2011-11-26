#!/usr/bin/python

import os

import webapp2
from django.utils import simplejson as json

SAMPLE_TRAIL_1 = {u'meta': {u'code': 200}, u'response': {u'trail': {u'areaId': u'4de9684ea5486462740f95c4', u'description': '', u'url': u'http://bouldermountainbike.org/trail/coal-seam-trail', u'regionId': u'4de6d929a8a32cc7f387f52b', u'head': {u'lat': 39.952602, u'lon': -105.231247}, u'owner': u'City of Boulder Open Space & Mountain Parks', u'kmlurl': u'http://bouldermountainbike.org/sites/default/files/Benjamin%20Loop.kml', u'updatedAt': 1307551432975.0, u'keywords': u'South', u'id': u'4de9689c457c5678aa351a6b', u'name': u'Coal Seam'}}}

SAMPLE_TRAIL_2 = {u'meta': {u'code': 200}, u'response': {u'trail': {u'areaId': u'4de9684ea5486462740f95c4', u'description': '', u'url': u'http://bouldermountainbike.org/trail/coal-seam-trail', u'regionId': u'4de6d929a8a32cc7f387f52b', u'head': {u'lat': 39.952602, u'lon': -105.231247}, u'owner': u'City of Boulder Open Space & Mountain Parks', u'kmlurl': u'http://bouldermountainbike.org/sites/default/files/Canyon%20Loop.kmz', u'updatedAt': 1307551432975.0, u'keywords': u'South', u'id': u'4de9689c457c5678aa351a6b', u'name': u'Coal Seam'}}}

REGION_RESPONSE = {u'meta': {u'code': 200}, u'response': {u'regions': [{u'name': u'Boulder, CO', u'updatedAt': 1317752573419.0, u'sponsorName': u'Boulder Mountainbike Alliance', u'sponsorTwitter': [u'#boco_trails', u'#valmontbikepark', u'boulderbma'], u'sponsorId': u'4def87fa7dcabb18dd36f524', u'allowed': [u'all'], u'sponsorAlertsUrl': u'http://bma.geozen.com/alerts/2011/index.html', u'id': u'4de6d929a8a32cc7f387f52b'}]}}


class RegionsPage(webapp2.RequestHandler):
  def post(self):
    self.response.out.write(json.dumps(REGION_RESPONSE))

class TrailsByRegionPage(webapp2.RequestHandler):
  def post(self, region_id):
    response = {'meta': 
                {'code': 200},
                'response': 
                 {'trails': [SAMPLE_TRAIL_1, SAMPLE_TRAIL_2]}
               }
    self.response.out.write(json.dumps(response))

class TrailsPage(webapp2.RequestHandler):
  def post(self, trail_id):
    self.response.out.write(json.dumps(SAMPLE_TRAIL_1))

app = webapp2.WSGIApplication([('/v1/trails/([^/]+)$', TrailsPage),
                               ('/v1/regions$', RegionsPage),
                               ('/v1/regions/([^/]+)/trails$', TrailsByRegionPage)], debug=True)
