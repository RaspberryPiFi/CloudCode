"""settings.py: Handles requests related to the settings page"""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

from google.appengine.api import users
from modules import customframework
from models import Group


class SettingsHandler(customframework.RequestHandler):
  url = '/settings'
  page_title = 'Settings'
  appear_in_navigation = True
  
  def get(self):
    """Shows the user the settings page"""
    self.render_template('settings.html')
    
class SetupDeviceHandler(customframework.RequestHandler):
  url = '/settings/enroll'
  page_title = 'Setup system'

  def get(self):
    """Shows the user the system setup page"""
    user_id = users.get_current_user().user_id()
    #TODO: Add multiple group functionality
    group_list = Group.query(Group.owner_id == user_id).fetch(1)
    if group_list:
      self.redirect('/')
      return
    self.render_template('setupdevice.html')
  
  def post(self):
    registration_code = self.request.get('registration_code')
    query = Group.query(Group.registration_code == registration_code)
    group_list = query.fetch(1)
    if not group_list:
      self.render_template('setupdevice.html',{'error': True})
    else:
      group = group_list[0]
      group.registered = True
      group.owner_id = users.get_current_user().user_id()
      group.put()
      self.redirect('/')
      #TODO: Butter bar style thing would be nice here for confirmation
      
      
      