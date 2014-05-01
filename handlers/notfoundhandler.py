"""notfoundhandler.py: Handles requests to pages that dont exist"""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

from modules import customframework

# Pylint doesn't like that I don't use args or kwargs
# pylint: disable=W0613

class HandleNotFound(customframework.RequestHandler):
  """Provides methods to handle get or post requests to an unknown page
     This is basically only here to make the 404 page pretty"""
  url = r'/<:.*>'
  page_title = 'Error Occurred... Uh-Oh'
  
  def get(self, *args, **kwargs):
    """Shows 404 error"""
    self.abort(404)
  def post(self, *args, **kwargs):
    """Shows 404 error"""
    self.abort(404)