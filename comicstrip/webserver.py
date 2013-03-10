import os
import cherrypy
import logging
from comicstrip import db

#from mako.template import Template
from mako.lookup import TemplateLookup


def update_cache(comicId, stripNo):
    myDB = db.DBConnection()
    myDB.upsert('view_cache', {'comic_id': comicId, 'last_strip': stripNo}, {'comic_id': comicId})


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


def redirect(abspath, *args, **KWs):
    assert abspath[0] == '/'
#    raise cherrypy.HTTPRedirect(comicstrip.WEB_ROOT + abspath, *args, **KWs)
    raise cherrypy.HTTPRedirect("" + abspath, *args, **KWs)


class Root:
    @cherrypy.expose
    @cherrypy.tools.mako(filename="home.html")
    def index(self):
        myDB = db.DBConnection(row_type="dict")
        stripList = myDB.select("SELECT id,name FROM comic_list")
        logging.debug("DATA DUMP: %s" % (stripList))

        return {'stripList': stripList}


class Config:
    @cherrypy.expose
    @cherrypy.tools.mako(filename="config.html")
    def index(self):
        myDB = db.DBConnection(row_type="dict")
        stripList = myDB.select("SELECT id,name FROM comic_list")
        logging.debug("DATA DUMP: %s" % (stripList))

        return {'stripList': stripList}


class View:
    @cherrypy.expose
    def ajax_strip(self, comicId, stripNo=None):
        return "<img></img>"

    @cherrypy.expose
    @cherrypy.tools.mako(filename="view.html")
    def strip(self, comicId, stripNo=None):

        prevStrip = None
        nextStrip = None

        myDB = db.DBConnection(row_type="dict")

        if not comicId:
            raise cherrypy.HTTPError(400, "A comic id was expected but not supplied.")

        comicTitle = myDB.select("SELECT name FROM comic_list WHERE id=(?) LIMIT 1", (comicId,))
        lastStrip = myDB.select("SELECT strip_no FROM comic_strips WHERE comic_id=(?) ORDER BY strip_no DESC LIMIT 1", (comicId,))
        lastView = myDB.select("SELECT last_strip FROM view_cache WHERE comic_id=(?)", (comicId,))

        if lastStrip is not None:
            lastStrip = lastStrip[0]['strip_no']

        if comicTitle is not None:
            comicTitle = comicTitle[0]['name']

        if stripNo is not None:
            comicStrip = myDB.select("SELECT location FROM comic_strips WHERE comic_id=(?) and strip_no =(?)", (comicId, stripNo, ))
            stripNo = int(stripNo)
            update_cache(comicId, stripNo)
        else:
            if not lastView:
                comicStrip = myDB.select("SELECT location FROM comic_strips WHERE comic_id=(?) and strip_no = 1", (comicId, ))
                stripNo = 1
            else:
                print "Found lastview"
                comicStrip = myDB.select("SELECT location FROM comic_strips WHERE comic_id=(?) and strip_no = (?)", (comicId, lastView[0]['last_strip'], ))
                stripNo = lastView[0]['last_strip']

        if comicStrip is not None:
            comicStrip = comicStrip[0]['location']

        nextStrip = stripNo + 1

        if nextStrip >= 1:
            prevStrip = stripNo - 1

        print nextStrip
        print prevStrip
        print lastView
        print lastStrip
        print comicStrip

        logging.debug("DATA DUMP: %s %s" % (lastStrip, comicTitle))
        return {'comicStrip': comicStrip, 'comicTitle': comicTitle, 'lastStrip': int(lastStrip), 'stripNo': int(stripNo), 'comicId': comicId, 'prevStrip': prevStrip, 'nextStrip': nextStrip}


class webInterface:

    @cherrypy.expose
    def index(self):
        redirect("/root/")
    root = Root()
    root.view = View()


def webInit():

    logging.basicConfig(level=logging.DEBUG)

    settings = {
        'global': {
            'server.socket_port': 8085,
            'server.socket_host': "127.0.0.1",
            'server.socket_file': "",
            'server.socket_queue_size': 5,
            'server.protocol_version': "HTTP/1.2",
            'server.log_to_screen': False,
            'server.log_file': "weblog.log",
            'server.reverse_dns': False,
            'server.thread_pool': 10,
            'server.environment': "development",
            'tools.mako.collection_size': 500,
            'tools.mako.directories': 'data/interface/',
        },
        '/images': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '%s' % (os.path.join(os.path.dirname(os.path.abspath(__name__)), 'strips')),
        },
        '/bootstrap': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '%s' % (os.path.join(os.path.dirname(os.path.abspath(__name__)), 'data/bootstrap')),
        },
    }

    cherrypy.config.update(settings)
    cherrypy.tree.mount(webInterface(), '/', settings)
    cherrypy.server.start()
    cherrypy.server.wait()

    logging.debug("THIS IS A ERROR: %s" % (os.path.dirname(os.path.abspath(__name__))))


def webStop():
    logging.debug("Die! Die! Die!")
    cherrypy.engine.exit()
