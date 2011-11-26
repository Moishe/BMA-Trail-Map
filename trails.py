#!/usr/bin/python

import logging
import os

import smarttrails

from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template

import webapp2


class MainPage(webapp2.RequestHandler):
  def get(self):
    domain = self.request.get('d') or 'bma-trails.appspot.com'
    use_cache = not (self.request.get('f') == 'y')
    region_id = self.request.get('r')

    trails = smarttrails.SmartTrails(domain, use_cache=use_cache)

    if not region_id:
      # Get the regions.
      regions = trails.get_regions()
      if not regions:
        self.response.set_status(500)
        self.response.out.write('Could not load regions.')

      region_id = regions['response']['regions'][0]['id']

    trails_in_region = trails.get_trails_by_region(region_id, parse_json=False)

    # Get the trails in the first region (arbitrarily for now)
    path = os.path.join(os.path.dirname(__file__), 'map.html')
    self.response.out.write(template.render(path, {'trails': trails_in_region}))

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)
