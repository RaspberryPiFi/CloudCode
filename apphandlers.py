"""apphandlers.py: Sets up the application handlers."""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

from handlers import notfoundhandler
from modules import customframework
import webapp2

app = customframework.WSGIApplication([
  # 404 handler
  notfoundhandler.HandleNotFound
  ], debug=True)