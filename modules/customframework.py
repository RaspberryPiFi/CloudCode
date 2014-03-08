"""webappframework.py: Contains an implementation of the webapp2.RequestHandler with custom error handling"""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

from config import JINJA_ENVIRONMENT
from google.appengine.api import users, memcache
from google.appengine.ext import ndb
from webob import exc
from models import Page

import webapp2
import logging


class RequestHandler(webapp2.RequestHandler):
  """Handles HTTP requests"""
  appear_in_navigation = False
  def abort(self,code,message=None,headers=None,exception=None):
    """Raises exception and displays error page"""
    self.response.status = code
    self.response.clear()

    cls = exc.status_map.get(code)
    if not cls:
      raise KeyError('No exception is defined for code %r.' % code)
      
    if not message:
        message = cls.explanation

    if code >= 500:
      if exception:
        logging.exception(exception)
      else:
        logging.error('Unexpected Error! Message: %s' % message)

    if headers:
      for header in headers:
        self.response.headers.add_header(*header)

    template_values = {
      'code': code,
      'error_title': cls.title,
      'message': message,
    }

    self.render_template('error.html',template_values)

    raise HandledHTTPException(code,self.response)
    #TODO: Add some try catches for any errors in this code

  def render_template(self,template, values={}):
    """Renders the template and writes this to the reponse"""
    values['user'] = users.get_current_user()
    values['navigation_pages'] = self.get_navigation_pages()
    #TODO: Handle error in event that self.url does not exist
    values['current_page'] = self
    template = JINJA_ENVIRONMENT.get_template(template)
    self.response.write(template.render(values))
  
  def get_navigation_pages(self):
    navigation_pages = memcache.get('navigation_pages')
    if navigation_pages is not None:
      return navigation_pages
    else:
      query = Page.query(Page.appear_in_navigation == True)
      #TODO: Change the fetch limit or document that it'll only fetch 10
      navigation_pages = query.fetch()
      if not memcache.set('navigation_pages', navigation_pages):
        logging.error('Write to memcache failed!')
      return navigation_pages
      

class HandledHTTPException(exc.HTTPException):
  """Creates a custom HTTPException"""
  def __init__(self, code, wsgi_response):
    """Overides the default __init__ to provide custom functionality"""
    Exception.__init__(self,'Handled %s error' % code)
    self.code = code
    self.wsgi_response = wsgi_response 
    
    
class WSGIApplication(webapp2.WSGIApplication):
  """A customised version of webapp2's WSGI-compliant application."""
  def __init__(self, route_handlers=None, debug=False, config=None):
    """Calls the store_pages() function with routes provided then 
    calls parent __init__ to Initializes the WSGI application.

    :param routes:
        A sequence of :class:`Route` instances or, for simple routes,
        tuples ``(regex, handler)``.
    :param debug:
        True to enable debug mode, False otherwise.
    :param config:
        A configuration dictionary for the application.
    """
    routes = self.store_pages(route_handlers)
    super(WSGIApplication, self).__init__(routes, debug, config)
  
  def store_pages(self, route_handlers):
    """Stores information on each handler in the datastore and returns a list
    of routes for the Router.
    
    :param routes_handler:
        A list of FrameworkHandler subclasses which identify routes and 
        their meta data.
    :returns:
        A list of webapp2.Route instance.
    """
    memcache.delete('navigation_pages')
    routes = []
    new_key_set = set()
    for route_handler in route_handlers:
      # Checks if datastore entry exits and uses if it is.
      query = Page.query(Page.url == route_handler.url)
      datastore_list = query.fetch(1)
      if datastore_list:
        datastore_entity = datastore_list[0]
      else:
        datastore_entity = Page()

      datastore_entity.url = route_handler.url
      datastore_entity.page_title = route_handler.page_title
      datastore_entity.appear_in_navigation = route_handler.appear_in_navigation
      #TODO: Not write to the datastore if there are no changes to be made
      datastore_entity.put()
      new_key_set.add(datastore_entity.key)
      
      # Creates a route for each handler and adds it to the routes list
      routes.append(webapp2.Route(route_handler.url,route_handler))
      
    # The following removes old pages from the datastore
    old_key_set = set(Page.query().fetch(keys_only=True))
    ndb.delete_multi(list(old_key_set - new_key_set))
    
    return routes