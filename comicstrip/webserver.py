import os
import sys
import cherrypy
import sqlite3
import datetime
import logging
from comicstrip import db

from mako.template import Template
from mako.lookup import TemplateLookup


class MakoHandler(cherrypy.dispatch.LateParamPageHandler):
    """Callable which sets response.body."""

    def __init__(self, template, next_handler):
        self.template = template
        self.next_handler = next_handler

    def __call__(self):
        env = globals().copy()
        env.update(self.next_handler())
        return self.template.render(**env)


class MakoLoader(object):

    def __init__(self):
        self.lookups = {}

    def __call__(self, filename, directories, module_directory=None,
                 collection_size=-1):
        # Find the appropriate template lookup.
        key = (tuple(directories), module_directory)
        try:
            lookup = self.lookups[key]
        except KeyError:
            lookup = TemplateLookup(directories=directories,
                                    module_directory=module_directory,
                                    collection_size=collection_size,
                                    )
            self.lookups[key] = lookup
        cherrypy.request.lookup = lookup

        # Replace the current handler.
        cherrypy.request.template = t = lookup.get_template(filename)
        cherrypy.request.handler = MakoHandler(t, cherrypy.request.handler)

main = MakoLoader()
cherrypy.tools.mako = cherrypy.Tool('on_start_resource', main)


class Root:
    @cherrypy.expose
    @cherrypy.tools.mako(filename="home.html")
    def index(self):
        myDB = db.DBConnection()
        stripList = myDB.select("SELECT id,name FROM comic_list")
        return { 'stripList': stripList }

class View:
    @cherrypy.expose
    @cherrypy.tools.mako(filename="view_strip.html")

    def strip(self,comicId,stripNo=None):
        myDB = db.DBConnection()
        if not comicId:
           raise cherrypy.HTTPError(400, "A user id was expected but not supplied.")
        # Grab the strip from the db
        comicTitle = myDB.select("SELECT id,name FROM comic_list WHERE id=(?) LIMIT 1",(comicId,))[0][0]
        lastStrip = myDB.select("SELECT strip_no FROM comic_strips WHERE comic_id=(?) ORDER BY strip_no DESC LIMIT 1",(comicId,))[0][0]

        if stripNo != None:
           comicStrip = myDB.select("SELECT location FROM comic_strips WHERE comic_id=(?) and strip_no =(?)",(comicId,stripNo,))
        else:
           comicStrip = myDB.select("SELECT location FROM comic_strips WHERE comic_id=(?) and strip_no = 1",(comicId,))
           stripNo = 1

        logging.debug("DATA DUMP: %s %s" % (lastStrip,comicTitle))
        return { 'comicStrip': comicStrip, 'comicTitle': comicTitle, 'lastStrip': int(lastStrip), 'stripNo': int(stripNo), 'comicId': comicId }


def webInit():
    root = Root()
    root.view = View()

    #logging.basicConfig(level=logging.DEBUG)

    # Empty Vars
    comicId = None
    the_db = os.path.join(os.path.dirname(os.path.abspath(__name__)),'comic.db')

    settings = {
       'global': {
          'server.socket_port' : 8085,
          'server.socket_host': "127.0.0.1",
          'server.socket_file': "",
          'server.socket_queue_size': 5,
          'server.protocol_version': "HTTP/1.2",
          'server.log_to_screen': False,
          'server.log_file': "",
          'server.reverse_dns': False,
          'server.thread_pool': 10,
          'server.environment': "development",
          'tools.mako.collection_size': 500,
          'tools.mako.directories': 'data/interface/',
       },
       '/images': {
          'tools.staticdir.on': True,
          'tools.staticdir.dir': '%s' % (os.path.join(os.path.dirname(os.path.abspath(__name__)),'strips')),
    #      'tools.staticdir.dir': '%s' % (os.path.dirname(os.path.abspath(__name__))),
       },
       '/bootstrap': {
          'tools.staticdir.on': True,
          'tools.staticdir.dir': '%s' % (os.path.join(os.path.dirname(os.path.abspath(__name__)),'data/bootstrap')),
       },

    }


    cherrypy.config.update(settings)

    #cherrypy.tree.mount(Root,'/',settings)
    #cherrypy.tree.mount(viewStrip,'/viewStrip',settings)

    #cherrypy.config.update({
    #      'tools.mako.collection_size': 500,
    #      'tools.mako.directories': 'data/interface/',
    #})


    #cherrypy.server.start()
    cherrypy.quickstart(root, config=settings)

    logging.debug("THIS IS A ERROR: %s" % (os.path.dirname(os.path.abspath(__name__))))
