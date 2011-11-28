#!/usr/bin/python
# Copyright 2011 Moishe Lettvin (moishel@gmail.com)
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
import urlparse
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from django.utils import simplejson as json


""" Various constants used to construct URIs. """
VERSION = 'v1'
REGIONS = 'regions'
AREA = 'area'
AREAS = 'areas'
TRAILS = 'trails'

class SmartTrails():
  """A simple class to wrap the Smart Trails API.

  See here for API documentation: https://docs.google.com/document/d/1QWKGzQ85zBQUyGxCTClUxLJoAPfMPZ2R_Y1xstanJ94

  TODO(moishel): complete other calls."""

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
    content = None
    if self.use_cache:
      logging.warning('fetching %s from cache' % uri)
      content = memcache.get(uri)

    if not content:
      logging.warning('fetching: %s' % uri)
      result = urlfetch.fetch(url=uri,
                              method=urlfetch.POST)
      logging.warning('result: %d' % result.status_code)
      if result.status_code == 200:
        content = result.content
        memcache.add(uri, content)

    if parse_json and content:
      return json.loads(content)
    else:
      return content


  def get_regions(self, parse_json=True):
    return self.fetch_from_cache_or_server([REGIONS], parse_json)

  def get_trails_by_area(self, area_id, parse_json=True):
    return self.fetch_from_cache_or_server([AREA, area_id, TRAILS], parse_json)

  def get_trails_by_region(self, region_id, parse_json=True):
    return self.fetch_from_cache_or_server([REGIONS, region_id, TRAILS], parse_json)

  def get_areas_by_region(self, region_id, parse_json=True):
    return self.fetch_from_cache_or_server([REGIONS, region_id, AREAS], parse_json)
