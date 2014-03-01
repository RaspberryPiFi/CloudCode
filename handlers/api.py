"""api.py: handles API requests"""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

from modules import customframework
from models import Group
from models import Device
import json
import logging


class SystemEnrollHandler(customframework.RequestHandler):
  url = '/api/system_enroll'
  page_title = 'enroll'
  
  def post(self):
    """Creates a group entry with registration code and returns the ID"""
    try:
      request = json.loads(self.request.body)
      registration_code = request['registration_code']
      if len(registration_code) != 6: raise ValueError
    except:
      self.error(400)
      self.response.write('6 digit registration_code in JSON format must be supplied!')
      return
    query = Group.query(Group.registration_code == registration_code)
    if query.fetch():
      self.error(409)
    else:
      new_group = Group(registration_code=registration_code).put()
      new_device = Device(parent=new_group).put()
      response_dict = {'group_id': str(new_group.id()),
                       'device_id': str(new_device.id())}
      json_string = json.dumps(response_dict)
      self.response.headers['Content-Type'] = "application/json"
      self.response.write(json_string)


class CheckEnrollHandler(customframework.RequestHandler):
  url = '/api/system_enroll_status'
  page_title = 'check enroll status'
  
  def post(self):
    """Returns the registered status for ID provided"""
    try:
      request = json.loads(self.request.body)
      group_id = int(request['group_id'])
    except:
      self.error(400)
      self.response.write('group_id in JSON format must be supplied!')
      return
    group = Group.get_by_id(group_id)
    if group:
      json_string = json.dumps({'registered': group.registered})
      self.response.headers['Content-Type'] = "application/json"
      self.response.write(json_string)
    else:
      self.error(400)
      self.response.write('Group with id provided does not exist')


class DeviceEnrollHandler(customframework.RequestHandler):
  url = '/api/device_enroll'
  page_title = 'enroll device'
  
  def post(self):
    """Creates a device entry and returns its id"""
    try:
      request = json.loads(self.request.body)
      group_id = int(request['group_id'])
      logging.error(group_id)
    except:
      self.error(400)
      self.response.write('group_id in JSON format must be supplied!')
      return
    group = Group.get_by_id(group_id)
    if group:
      new_device = Device(parent=group.key).put()
      json_string = json.dumps({'device_id': str(new_device.id())})
      self.response.headers['Content-Type'] = "application/json"
      self.response.write(json_string)
    else:
      self.error(400)
      self.response.write('Group with id provided does not exist')
    
    
    