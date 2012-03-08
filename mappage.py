#!/usr/bin/python

import mockapi

import logging
import os
import webapp2

from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from django.utils import simplejson as json


class MapPage(webapp2.RequestHandler):
  def get(self):
    region_id = self.request.get('r', '1')
    area_id = self.request.get('a')
    # If we have them cached, send the trails down in the payload.
    if not area_id:
      uri = mockapi.TrailsByRegionPage().get_query_uri(region_id)
    else:
      uri = mockapi.TrailsByAreaPage().get_query_uri(area_id)
    cached = memcache.get(uri)
    if cached:
      cached_with_points = mockapi.ExtractGxpAndInsertPoints(cached)
    else:
      cached_with_points = None

    path = os.path.join(os.path.dirname(__file__), 'map.html')
    self.response.out.write(template.render(path, {'cached_trails': cached_with_points,
                                                   'area': area_id}))

app = webapp2.WSGIApplication([('/', MapPage)], debug=True)
