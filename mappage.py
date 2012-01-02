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
    # Get the trails in the first region (arbitrarily for now)
    path = os.path.join(os.path.dirname(__file__), 'map.html')
    self.response.out.write(template.render(path, {}))

app = webapp2.WSGIApplication([('/', MapPage)], debug=True)
