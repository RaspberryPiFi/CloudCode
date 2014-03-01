"""notfoundhandler.py: Handles requests to pages that dont exist"""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

from modules import customframework

class HandleNotFound(customframework.RequestHandler):
  url = r'/<:.*>'
  page_title = 'Error Occurred... Uh-Oh'
  
  def get(self, *args, **kwargs):
    """Shows 404 error"""
    self.abort(404)
  def post(self, *args, **kwargs):
    """Shows 404 error"""
    self.abort(404)