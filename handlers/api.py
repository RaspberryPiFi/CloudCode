"""api.py: handles API requests"""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

import json

from google.appengine.api import memcache
from google.appengine.ext import ndb

import models
from modules import customframework


class SystemEnrollHandler(customframework.RequestHandler):
  """Provides functions to handle system enroll requests"""
  url = '/api/system_enroll'
  page_title = 'enroll'
  
  def post(self):
    """Creates a group entry with registration code and returns the ID"""
    try:
      request = json.loads(self.request.body)
      registration_code = request['registration_code']
      if len(registration_code) != 6: 
        raise ValueError
    except Exception:
      self.error(400)
      self.response.write('6 digit registration_code in a JSON object required')
      return
    q = models.Group.query(models.Group.registration_code == registration_code)
    if q.fetch():
      self.error(409)
    else:
      new_group = models.Group(registration_code=registration_code).put()
      new_device = models.Device(parent=new_group).put()
      response_dict = {'group_id': str(new_group.id()),
                       'device_id': str(new_device.id())}
      json_string = json.dumps(response_dict)
      self.response.headers['Content-Type'] = "application/json"
      self.response.write(json_string)


class CheckEnrollHandler(customframework.RequestHandler):
  """Provides functions to handle requests to check enroll status"""
  url = '/api/system_enroll_status'
  page_title = 'check enroll status'
  
  def post(self):
    """Returns the registered status for ID provided"""
    try:
      request = json.loads(self.request.body)
      group_id = int(request['group_id'])
    except Exception:
      self.error(400)
      self.response.write('group_id in a JSON object must be supplied!')
      return
    group = models.Group.get_by_id(group_id)
    if group:
      json_string = json.dumps({'registered': group.registered})
      self.response.headers['Content-Type'] = "application/json"
      self.response.write(json_string)
    else:
      self.error(400)
      self.response.write('Group with id provided does not exist')


class DeviceEnrollHandler(customframework.RequestHandler):
  """Provides functions to handle device enroll requests"""
  url = '/api/device_enroll'
  page_title = 'enroll device'
  
  def post(self):
    """Creates a device entry and returns its id"""
    try:
      request = json.loads(self.request.body)
      group_id = int(request['group_id'])
    except Exception:
      self.error(400)
      self.response.write('group_id in a JSON object must be supplied!')
      return
    group = models.Group.get_by_id(group_id)
    if group:
      new_device = models.Device(parent=group.key).put()
      json_string = json.dumps({'device_id': str(new_device.id())})
      self.response.headers['Content-Type'] = "application/json"
      self.response.write(json_string)
    else:
      self.error(400)
      self.response.write('Group with id provided does not exist')
      
class GroupUpdateHandler(customframework.RequestHandler):
  """Provides functions to handle group update requests"""
  url = '/api/group/update'
  page_title = 'group update'
  
  def post(self):
    """Communicates any actions to be taken to the master device"""
    try:
      request = json.loads(self.request.body)
      group_id = int(request['group_id'])
    except Exception:
      self.error(400)
      self.response.write('group_id in a JSON object must be supplied!')
      return
    #TODO: Use channels to send updates to the users
    #TODO: Sanitise this data
    memcache.set('%s_statuses' % group_id, request['statuses'], 30)
    
    actions = memcache.get('actions_%s' % group_id)
    if actions:
      memcache.set('actions_%s' % group_id, [])
      json_string = json.dumps({'actions': actions})
    else:
      json_string = json.dumps({})
      
    self.response.headers['Content-Type'] = "application/json"
    self.response.write(json_string)
    
class LibraryUpdateHandler(customframework.RequestHandler):
  """Provides functions to handle library update requests"""
  url = '/api/group/library'
  page_title = 'Library Update'
  
  def post(self):
    """Gets an update from the master device"""
    request = json.loads(self.request.body)
    group_key = ndb.Key(models.Group, int(request['group_id']))
    artists = request['artists']
    albums = request['albums']
    songs = request['songs']
    
    db_artists = []
    for artist in artists:
      db_artists.append(models.Artist(name=artist['name']))
    
    db_albums = []  
    for album in albums:
      db_albums.append(models.Album(name=album['name'],
                                    artist_name=album['artist']))
    
    db_songs = []
    for song in songs:
      db_songs.append(models.Song(name=song['name'],
                                  artist_name=song['artist'],
                                  album_name=song['album'],
                                  length=song['length'],
                                  path=song['path'],
                                  source=song['source'],
                                  track=song['track']))
                                  
    query = models.AudioData.query(models.AudioData.group_key == group_key)
    results = query.fetch(1)
    if results:
      audio_data = results[0]
    else:
      audio_data = models.AudioData(group_key=group_key)
      
    memcache.delete_multi(['_albums', '_artists', '_songs'],
                          key_prefix=group_key.urlsafe())
    
    audio_data.artists = db_artists
    audio_data.albums = db_albums
    audio_data.songs = db_songs
    audio_data.put()
    
    