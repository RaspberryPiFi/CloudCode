"""deviceselection.py: Handles requests to the device selection page"""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

from modules import customframework
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import ndb

from models import Group
from models import Device


class DeviceSelectionHandler(customframework.RequestHandler):
  url = '/'
  page_title = 'Select Device'
  appear_in_navigation = True
  
  def get(self):
    """Shows the user their devices"""
    user_id = users.get_current_user().user_id()
    #TODO: Add multiple group functionality
    query = Group.query(Group.owner_id == user_id)
    group_keys = query.fetch(1, keys_only=True)
    if not group_keys:
      self.redirect('/settings/enroll')
      return
    
    devices = Device.query(ancestor=group_keys[0])
    self.render_template('deviceselection.html',{'devices': devices})

class DeviceTestHandler(customframework.RequestHandler):
  url = '/device/test'
  page_title = 'Device Control Test Page'
  
  def get(self):
    device_urlsafe_key = self.request.get('id')
    device_key = ndb.Key(urlsafe=device_urlsafe_key)
    device = device_key.get()
    template_values = {'device_urlsafe_key': device_urlsafe_key}
    self.render_template('devicetest.html', template_values)
    
class DeviceActionHandler(customframework.RequestHandler):
  url='/device/action'
  page_title = 'handle device actions'
  
  def post(self):
    """This is a temporary way of handling actions"""
    #TODO: Make this secure!
    action_type = self.request.get('action')
    arg = self.request.get('arg')
    device_urlsafe_key = self.request.get('device_urlsafe_key')
    device_key = ndb.Key(urlsafe=device_urlsafe_key)
    group_key = device_key.parent()
    action = {'device_id': str(device_key.id()), 'type': action_type}
    if action_type == 'set_volume':
      action['arg'] = float(arg)
    elif action_type == 'play_list':
      action['arg'] = arg.split(',')
      
    memcache_key = 'actions_%s' % group_key.id()
      
    action_list = memcache.get(memcache_key)
    if action_list: 
      action_list.append(action)
    else: 
      action_list = [action]
    memcache.set(memcache_key, action_list)
    self.redirect('/device/test?id=%s' % device_urlsafe_key)
    
class PartyTestHandler(customframework.RequestHandler):
  url = '/party/test'
  page_title = 'Party Mode Test Page'
  
  def get(self):
    self.render_template('partytest.html')
    
class PartyActionHandler(customframework.RequestHandler):
  url='/party/action'
  page_title = 'handle party actions'
  
  def post(self):
    """This is a temporary way of handling party actions"""
    action_type = self.request.get('action')
    arg = self.request.get('arg')
    user_id = users.get_current_user().user_id()
    query = Group.query(Group.owner_id == user_id)
    group_key = query.fetch(1, keys_only=True)[0]
    action = {'type': action_type, 'party_mode':True}
    if action_type == 'set_volume':
      action['arg'] = float(arg)
    elif action_type == 'play_list':
      action['arg'] = arg.split(',')
    devices = Device.query(ancestor=group_key)
    action['device_ids'] = [str(device.key.id()) for device in devices] 
    
    memcache_key = 'actions_%s' % group_key.id()
    action_list = memcache.get(memcache_key)
    if action_list: 
      action_list.append(action)
    else: 
      action_list = [action]
    memcache.set(memcache_key, action_list)
    self.redirect('/party/test')




