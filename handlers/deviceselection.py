"""deviceselection.py: Handles requests to the device selection page"""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

from modules import customframework
from google.appengine.api import users

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
    group_list = Group.query(Group.owner_id == user_id).fetch(1)
    if not group_list:
      self.redirect('/settings/enroll')
      return
    
    devices = Device.query(ancestor=group_list[0].key)
    self.render_template('deviceselection.html',{'devices': devices})