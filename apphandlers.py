"""apphandlers.py: Sets up the application handlers."""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

from handlers import notfoundhandler
from handlers import deviceselection
from handlers import settings
from handlers import api
from modules import customframework
import webapp2

app = customframework.WSGIApplication([
  deviceselection.DeviceSelectionHandler,
  settings.SettingsHandler,
  settings.SetupDeviceHandler,
  api.SystemEnrollHandler,
  api.CheckEnrollHandler,
  api.DeviceEnrollHandler,
  # 404 handler
  notfoundhandler.HandleNotFound
  ], debug=True)