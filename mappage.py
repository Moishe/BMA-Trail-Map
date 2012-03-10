#!/usr/bin/python

import mockapi

import logging
import os
import random
import webapp2

from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from django.utils import simplejson as json


class MapPage(webapp2.RequestHandler):
  def get(self):
    region_id = self.request.get('r', '1')
    area_id = self.request.get('a')
    skip_cache = self.request.get('skip_cache', 'n') == 'y'
    logging.info("MapPage: %s" % str(skip_cache))
    if skip_cache:
      logging.info('Flushing memcache.')
      memcache.flush_all()

    if skip_cache:
      cache_buster = '?cache_buster=' + str(random.randint(0, 4096))
    else:
      cache_buster = ''

    path = os.path.join(os.path.dirname(__file__), 'map.html')
    self.response.out.write(template.render(path, {'area': area_id,
                                                   'skip_cache': self.request.get('skip_cache', 'n'),
                                                   'cache_buster': cache_buster}))

app = webapp2.WSGIApplication([('/', MapPage)], debug=True)
