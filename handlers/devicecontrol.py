"""deviceselection.py: Handles requests to the device selection page"""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

import json

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import ndb

from modules import customframework
import models


def get_group_key(device_key=False):
  """Gets group key from memcache or gets from datastore"""
  user_id = users.get_current_user().user_id()
  group_key = memcache.get('group_key_%s' % user_id)
  if not group_key:
    query = models.Group.query(models.Group.owner_id == user_id)
    group_keys = query.fetch(1, keys_only=True)
    if not group_keys:
      return False
    group_key = group_keys[0]
    memcache.set('group_key_%s' % user_id, group_key)
  if device_key:
    if group_key != device_key.parent():
      return False
  return group_key

def get_audio_attr(group_key, attr):
  """Gets audio data from memcache or gets from datastore"""
  audio_attr = memcache.get('%s_%s' % (group_key.urlsafe(), attr))
  if not audio_attr:
    query = models.AudioData.query(models.AudioData.group_key == group_key)
    results = query.fetch(1)
    if not results: 
      return False
    audio_data = results[0]
    mapping = {'_artists': audio_data.artists,
               '_albums': audio_data.albums,
               '_songs': audio_data.songs}
    memcache.set_multi(mapping, key_prefix=group_key.urlsafe())
    audio_attr = getattr(audio_data, attr)
  return audio_attr
  
def send_action(group_key, action):
  """Stores up-coming action to the memcache"""
  memcache_key = 'actions_%s' % group_key.id()
  action_list = memcache.get(memcache_key)
  if action_list: 
    action_list.append(action)
  else: 
    action_list = [action]
  memcache.set(memcache_key, action_list, 60)
  

class DeviceSelectionHandler(customframework.RequestHandler):
  """Provides functions to handle requests to the device selection page"""
  url = '/'
  page_title = 'Select Device'
  appear_in_navigation = True
  
  def get(self):
    """Shows the user their devices"""
    group_key = get_group_key()
    if not group_key:
      self.redirect('/settings/enroll')
      return
    group_id = group_key.id()
    template_values = {}
    statuses = memcache.get('%s_statuses' % group_id)
    template_values['statuses'] = statuses
    if not statuses: 
      template_values['all_dead'] = True
    template_values['devices'] = models.Device.query(ancestor=group_key)
    self.render_template('deviceselection.html', template_values)
    
    
class DeviceMainPage(customframework.RequestHandler):
  """Provides functions to handle requests to the device main page"""
  url = '/device'
  page_title = 'Device Control'
  
  def get(self):
    """Renders the main page"""
    device_urlsafe_key = self.request.get('key')
    template_values = {'device_urlsafe_key': device_urlsafe_key}
    self.render_template('devicemain.html', template_values)
    
    
class DeviceArtists(customframework.RequestHandler):
  """Provides functions to handle requests to the artists page"""
  url = '/device/artists'
  page_title = 'Artists'
  
  def get(self):
    """Renders the artists page"""
    #TODO: Handle erros with below
    device_urlsafe_key = self.request.get('key')
    #TODO: Compare to device group_key to check if this device belongs to user
    group_key = get_group_key(ndb.Key(urlsafe=device_urlsafe_key))
    if not group_key:
      self.abort(403,'This device is not part of your group!')
    artists = get_audio_attr(group_key,'artists')
    if not artists:
      self.abort(404,'No Music Found!')
    
    template_values = {'device_urlsafe_key': device_urlsafe_key,
                       'artists': artists}
    self.render_template('deviceartists.html', template_values)
    

class DeviceAlbums(customframework.RequestHandler):
  """Provides functions to handle requests to the albums page"""
  url = '/device/albums'
  page_title = 'Albums'
  
  def get(self):
    """Renders the albums page"""
    device_urlsafe_key = self.request.get('key')
    #TODO: Compare to device group_key to check if this device belongs to user
    group_key = get_group_key(ndb.Key(urlsafe=device_urlsafe_key))
    if not group_key:
      self.abort(403,'This device is not part of your group!')
    albums = get_audio_attr(group_key,'albums')
    if not albums:
      self.abort(404,'No Music Found!')
    
    template_values = {'device_urlsafe_key': device_urlsafe_key,
                       'albums': albums}
    self.render_template('devicealbums.html', template_values)
    
class DeviceArtist(customframework.RequestHandler):
  """Provides functions to handle requests to the artist page"""
  url='/device/artist'
  page_title = 'Artist'
  
  def get(self):
    """Gets the songs and albums by the artist and renderes thw page"""
    artist_id = self.request.get('id')
    device_urlsafe_key = self.request.get('key')
    group_key = get_group_key(ndb.Key(urlsafe=device_urlsafe_key))
    if not group_key:
      self.abort(403,'This device is not part of your group!')
    songs = get_audio_attr(group_key,'songs')
    if not songs:
      self.abort(404,'No Music Found!')
    
    artist = get_audio_attr(group_key, 'artists')[int(artist_id)]
    albums = get_audio_attr(group_key, 'albums')
    template_values = {'device_urlsafe_key': device_urlsafe_key,
                       'albums': albums,
                       'songs': songs,
                       'artist_name': artist.name}
                       
    self.render_template('deviceartist.html', template_values)

class DeviceSongs(customframework.RequestHandler):
  """Provides functions to handle requests to the songs page"""
  url = '/device/songs'
  page_title = 'Songs'
  
  def get(self):
    """Gets all songs and/or album details if applicable and renders the page"""
    album_id = self.request.get('album')
    device_urlsafe_key = self.request.get('key')
    group_key = get_group_key(ndb.Key(urlsafe=device_urlsafe_key))
    if not group_key:
      self.abort(403,'This device is not part of your group!')
    songs = get_audio_attr(group_key,'songs')
    if not songs:
      self.abort(404,'No Music Found!')
      
    template_values = {'device_urlsafe_key': device_urlsafe_key,
                       'songs': songs}
    #TODO: Check input and ensure is int
    if album_id:
      album = get_audio_attr(group_key, 'albums')[int(album_id)]
      template_values['album_name'] = album.name
      template_values['artist_name'] = album.artist_name
      template_values['album_id'] = album_id
    
    self.render_template('devicesongs.html', template_values)
    
    
class DeviceActionHandler(customframework.RequestHandler):
  """Provides functions to handle device action requests"""
  url = '/device/action'
  page_title = 'handle device actions'
  
  def post(self):
    """Handles actions sent by the user"""
    try:
      request = json.loads(self.request.body)
      action_type = request['action']
      try:
        arg = request['arg']
      except KeyError:
        pass
      device_urlsafe_key = request['device_urlsafe_key']
    except Exception:
      self.abort(400)
      
    possible_actions = ['play_pause', 'skip_forward', 'test_tone',
                        'skip_backward', 'stop', 'set_volume']
                        
    if action_type not in possible_actions:
      self.abort(400,'Action not supported')
    
    action = {'type': action_type}
    
    if action_type == 'set_volume':
      action['arg'] = float(arg)
      
    if device_urlsafe_key == 'party_mode':
      group_key = get_group_key()
      action['party_mode'] = True
    else:
      device_key = ndb.Key(urlsafe=device_urlsafe_key)
      group_key = get_group_key(device_key)
      action['device_id'] = str(device_key.id())
      if not group_key:
        self.abort(403,'This device is not part of your group!')
        
    send_action(group_key, action)
    
class DeviceUpdateHandler(customframework.RequestHandler):
  """Provides functions to handle device update requests"""
  url = '/device/get_update'
  page_title = 'handle device actions'
  
  def post(self):
    """Returns the current statuses dict for the device"""
    try:
      request = json.loads(self.request.body)
      device_urlsafe_key = request['device_urlsafe_key']
    except Exception:
      self.abort(400)
    
    if device_urlsafe_key == 'party_mode':
      group_key = get_group_key()
      statuses = memcache.get('%s_statuses' % group_key.id())
      if not statuses:
        self.abort(404)
      else:
        if statuses['party_mode']:
          status = statuses['party']
        else:
          status = {'alive': False}
    else:
      device_key = ndb.Key(urlsafe=device_urlsafe_key)
      device_id = str(device_key.id())
      group_key = get_group_key(device_key)
      if not group_key:
        self.abort(403,'This device is not part of your group!')
      statuses = memcache.get('%s_statuses' % group_key.id())
      if not statuses or device_id not in statuses: 
        self.abort(404)
      else:
        status = statuses[device_id]

    json_string = json.dumps(status)
    self.response.write(json_string)

      
class DevicePlayHandler(customframework.RequestHandler):
  """Provides functions to handle device play requests"""
  url = '/device/play'
  page_title = 'Device Play Handler'
  
  def post(self):
    """Handles playing a song and passing the other songs in the series"""
    #TODO: Possibly combine with above as alot of duplicate code
    try:
      request = json.loads(self.request.body)
      song_id = request['song_id']
      device_urlsafe_key = request['device_urlsafe_key']
    except Exception:
      self.abort(400)
    
    action = {'type': 'play_list'}
    
    if device_urlsafe_key == 'party_mode':
      group_key = get_group_key()
      action['party_mode'] = True
    else:
      device_key = ndb.Key(urlsafe=device_urlsafe_key)
      group_key = get_group_key(device_key)
      action['device_id'] = str(device_key.id())
      if not group_key:
        self.abort(403,'This device is not part of your group!')
      
    songs = get_audio_attr(group_key,'songs')
    
    if 'artist' in request:
      artist = get_audio_attr(group_key, 'artists')[int(request['artist'])]
      song_locs = [{'source':e.source, 'path':e.path} for e in songs 
                   if e.artist_name == artist.name]
                   
    elif 'album' in request:
      album = get_audio_attr(group_key, 'albums')[int(request['album'])]
      song_locs = [{'source':e.source, 'path':e.path} for e in songs
                   if e.album_name == album.name]
                   
    else:
      song_locs = [{'source':e.source, 'path':e.path} for e in songs]
    
    song_locs = song_locs[int(song_id):]
    action['arg'] =  song_locs
    send_action(group_key, action)
    

class PartyMainPage(customframework.RequestHandler):
  """Provides functions to handle requests to the party main page"""
  url = '/party'
  page_title = 'Party Mode Control'
  
  def get(self):
    """Renders the main page"""
    template_values = {'party_mode': True}
    self.render_template('devicemain.html', template_values)
    
    
class PartyArtists(customframework.RequestHandler):
  """Provides functions to handle requests to the party artists page"""
  url = '/party/artists'
  page_title = 'Party Artists'
  
  def get(self):
    """Renders the artists page"""
    group_key = get_group_key()
    artists = get_audio_attr(group_key,'artists')
    if not artists:
      self.abort(404,'No Music Found!')
    
    template_values = {'party_mode': True,
                       'artists': artists}
    self.render_template('deviceartists.html', template_values)
    

class PartyAlbums(customframework.RequestHandler):
  """Provides functions to handle requests to the party albums page"""
  url = '/party/albums'
  page_title = 'Party Albums'
  
  def get(self):
    """Renders the albums page"""
    group_key = get_group_key()
    albums = get_audio_attr(group_key,'albums')
    if not albums:
      self.abort(404,'No Music Found!')
    
    template_values = {'party_mode': True,
                       'albums': albums}
    self.render_template('devicealbums.html', template_values)
    
class PartyArtist(customframework.RequestHandler):
  """Provides functions to handle requests to the artist page"""
  url='/party/artist'
  page_title = 'Artist'
  
  def get(self):
    """Gets the songs and albums by the artist and renderes thw page"""
    artist_id = self.request.get('id')
    group_key = get_group_key()
    songs = get_audio_attr(group_key,'songs')
    if not songs:
      self.abort(404,'No Music Found!')
    
    artist = get_audio_attr(group_key, 'artists')[int(artist_id)]
    albums = get_audio_attr(group_key, 'albums')
    template_values = {'party_mode': True,
                       'albums': albums,
                       'songs': songs,
                       'artist_name': artist.name,
                       'artist_id': artist_id}
    
    self.render_template('deviceartist.html', template_values)
    

class PartySongs(customframework.RequestHandler):
  """Provides functions to handle requests to the party songs page"""
  url = '/party/songs'
  page_title = 'Songs'
  
  def get(self):
    """Renders the songs page"""
    album_id = self.request.get('album')
    group_key = get_group_key()
    songs = get_audio_attr(group_key,'songs')
    if not songs:
      self.abort(404,'No Music Found!')
      
    template_values = {'party_mode': True,
                       'songs': songs}
    #TODO: Check input and ensure is int
    if album_id:
      album = get_audio_attr(group_key, 'albums')[int(album_id)]
      template_values['album_name'] = album.name
      template_values['artist_name'] = album.artist_name
      template_values['album_id'] = album_id
    
    self.render_template('devicesongs.html', template_values)