"""settings.py: Handles requests related to the settings page"""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

from google.appengine.api import users, memcache
from google.appengine.ext import ndb

from modules import customframework
from models import Group, Device


class SettingsHandler(customframework.RequestHandler):
  """Handles requests to the settings page"""
  url = '/settings'
  page_title = 'Settings'
  appear_in_navigation = True
  
  def get(self):
    """Renders a set of forms to change a device's name"""
    user_id = users.get_current_user().user_id()
    group_key = memcache.get('group_key_%s' % user_id)
    error = self.request.get('error')
    if not group_key:
      query = Group.query(Group.owner_id == user_id)
      group_keys = query.fetch(1, keys_only=True)
      if not group_keys:
        self.redirect('/settings/enroll')
      group_key = group_keys[0]
      memcache.set('group_key_%s' % user_id, group_key)
    devices = Device.query(ancestor=group_key)
    template_values = {'devices': devices,
                       'error': error}
    self.render_template('settings.html', template_values)
    
  def post(self):
    """Changes a device's name in the datastore"""
    device_urlsafe_key = self.request.get('device_urlsafe_key')
    new_device_name = self.request.get('name')
    if not new_device_name:
      self.redirect('settings?error=1')
      return
    device = ndb.Key(urlsafe=device_urlsafe_key).get()
    device.name = new_device_name
    device.put()
    self.redirect('settings')
    
class SetupGroupHandler(customframework.RequestHandler):
  """Handles requests to the setup group page"""
  url = '/settings/enroll'
  page_title = 'Setup system'

  def get(self):
    """Renders the system setup page"""
    user_id = users.get_current_user().user_id()
    #TODO: Add multiple group functionality
    group_list = Group.query(Group.owner_id == user_id).fetch(1)
    if group_list:
      self.redirect('/')
      return
    self.render_template('setupdevice.html')
  
  def post(self):
    """Claims the device registration number provided as the user's"""
    registration_code = self.request.get('registration_code')
    query = Group.query(Group.registration_code == registration_code)
    group_list = query.fetch(1)
    if not group_list:
      self.render_template('setupdevice.html', {'error': True})
    else:
      group = group_list[0]
      group.registered = True
      group.owner_id = users.get_current_user().user_id()
      group.put()
      self.redirect('/')
      #TODO: Redirect to page that waits about 5-10 seconds then redirects
      
      
      