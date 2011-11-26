#!/usr/bin/python

import logging
import urlparse

from google.appengine.api import memcache
from google.appengine.api import urlfetch
from django.utils import simplejson as json


""" Various constants used to construct URIs. """
VERSION = 'v1'
REGIONS = 'regions'
TRAILS = 'trails'


class SmartTrails():

  def __init__(self, domain, scheme='http', use_cache=False):
    self.scheme = scheme
    self.domain = domain
    self.use_cache = use_cache

  def make_uri(self, path_items):
    path_items.insert(0, VERSION)
    path = '/'.join(path_items)
    return urlparse.urlunparse((self.scheme, self.domain, path, '', '', ''))

  def fetch_from_cache_or_server(self, path, parse_json):
    uri = self.make_uri(path)
    logging.warning('uri: %s' % uri)
    if self.use_cache:
      content = memcache.get(uri)

    logging.warning('content: %s' % content)

    if not content:
      result = urlfetch.fetch(url=uri,
                              method=urlfetch.POST)
      logging.warning('result: %d: %s' % (result.status_code, result.content))
      if result.status_code == 200:
        content = result.content
        memcache.add(uri, content)

    if parse_json and content:
      return json.loads(content)
    else:
      return content


  def get_regions(self, parse_json=True):
    return self.fetch_from_cache_or_server([REGIONS], parse_json)

  def get_trails_by_region(self, region_id, parse_json=True):
    return self.fetch_from_cache_or_server([REGIONS, region_id, TRAILS], parse_json)
