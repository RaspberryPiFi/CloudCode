"""models.py: Datastore models."""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

from google.appengine.ext import ndb

class Page(ndb.Model):
  """Models a page in the application"""
  url = ndb.StringProperty(required=True)
  # If navigation_title is not present, it will not appear in the navigation.
  page_title = ndb.StringProperty()
  appear_in_navigation = ndb.BooleanProperty(default=False)

class Group(ndb.Model):
  """Models a single device group"""
  registration_code = ndb.StringProperty(required=True)
  registered = ndb.BooleanProperty(default=False)
  owner_id = ndb.StringProperty()

class Device(ndb.Model):
  """Models a single device"""
  name = ndb.StringProperty(default='Unamed Device')
  
  