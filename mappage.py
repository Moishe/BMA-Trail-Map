#!/usr/bin/python

import logging
import os
import webapp2

import smarttrails

from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from django.utils import simplejson as json


class MapPage(webapp2.RequestHandler):
  def get(self):
    domain = self.request.get('d') or 'bma-trails.appspot.com'
    use_cache = not (self.request.get('f') == 'y')
    area_id = self.request.get('a')
    trails_in_areas = []
    if area_id:
      if area_id.find(',') != -1:
        area_ids = area_id.split(',')
      else:
        area_ids = [area_id]

      trails = smarttrails.SmartTrails(domain, use_cache=use_cache)

      trails_in_areas = []
      for area_id in area_ids:
        trails_in_area = trails.get_trails_by_area(area_id)
        if not trails_in_area or len(trails_in_area) == 0:
          self.response.out.write('No trails found for area %s' % area_id)
          self.response.set_status(404)
          return
        trails_in_areas.append(trails_in_area)

    # Get the trails in the first region (arbitrarily for now)
    path = os.path.join(os.path.dirname(__file__), 'map.html')
    self.response.out.write(template.render(path, {'trails': json.dumps(trails_in_areas)}))

app = webapp2.WSGIApplication([('/map', MapPage)], debug=True)
