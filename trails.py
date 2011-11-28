#!/usr/bin/python

import logging
import os
import webapp2

import smarttrails

from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from django.utils import simplejson as json


class AreaPage(webapp2.RequestHandler):
  def get(self):
    domain = self.request.get('d') or 'bma-trails.appspot.com'
    use_cache = not (self.request.get('f') == 'y')
    trails = smarttrails.SmartTrails(domain, use_cache=use_cache)

    areas = trails.get_areas_by_region('1')
    # Get the trails in the first region (arbitrarily for now)
    path = os.path.join(os.path.dirname(__file__), 'areas.html')
    logging.warning(areas['response']['areas'])
    self.response.out.write(template.render(path, {'areas': areas['response']['areas']}))

app = webapp2.WSGIApplication([('/', AreaPage)], debug=True)
