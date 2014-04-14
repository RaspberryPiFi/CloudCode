"""apphandlers.py: Sets up the application handlers"""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

from handlers import notfoundhandler
from handlers import devicecontrol
from handlers import settings
from handlers import api
from modules import customframework

app = customframework.WSGIApplication([
  devicecontrol.DeviceSelectionHandler,
  devicecontrol.DeviceMainPage,
  devicecontrol.DeviceArtists,
  devicecontrol.DeviceAlbums,
  devicecontrol.DeviceArtist,
  devicecontrol.DeviceSongs,
  devicecontrol.PartyMainPage,
  devicecontrol.PartyArtists,
  devicecontrol.PartyAlbums,
  devicecontrol.PartyArtist,
  devicecontrol.PartySongs,
  devicecontrol.DeviceActionHandler,
  devicecontrol.DevicePlayHandler,
  devicecontrol.DeviceUpdateHandler,
  
  settings.SettingsHandler,
  settings.SetupGroupHandler,
  
  api.SystemEnrollHandler,
  api.CheckEnrollHandler,
  api.DeviceEnrollHandler,
  api.GroupUpdateHandler,
  api.LibraryUpdateHandler,
  
  # 404 handler
  notfoundhandler.HandleNotFound
  ], debug=True)