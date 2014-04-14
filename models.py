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
  
class Song(ndb.Model):
  """Models the meta data of a song"""
  name = ndb.StringProperty(indexed=False)
  path = ndb.StringProperty(indexed=False)
  artist_name = ndb.StringProperty(indexed=False)
  album_name = ndb.StringProperty(indexed=False)
  source = ndb.StringProperty(indexed=False)
  length = ndb.StringProperty(indexed=False)
  track = ndb.IntegerProperty(indexed=False)
  
class Album(ndb.Model):
  """Models the meta data of an album"""
  name = ndb.StringProperty(indexed=False)
  artist_name = ndb.StringProperty(indexed=False)
  
class Artist(ndb.Model):
  """Models the meta data of an artist"""
  name = ndb.StringProperty(indexed=False)
  
class AudioData(ndb.Model):
  """Models a single group's available media collection"""
  group_key = ndb.KeyProperty()
  songs = ndb.StructuredProperty(Song, repeated=True, indexed=False)
  albums = ndb.StructuredProperty(Album, repeated=True, indexed=False)
  artists = ndb.StructuredProperty(Artist, repeated=True, indexed=False)
  
  
  
  