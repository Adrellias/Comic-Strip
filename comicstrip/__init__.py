'''
 Author: <adrellias@gmail.com>
 url: https://github.com/adrellias
'''
import os
import errno

from ConfigParser import ConfigParser
from threading import Lock
from comicstrip import db

# Some Defaults if they are not there alreedy

# Path related defaults
MY_FULLNAME = None
MY_NAME = None
PROG_DIR = None
DATA_DIR = None
CREATEPID = False
DAEMON = False
SYS_ENCODING = None

# Config File Defaults
COMIC_LIST = None
WEB_PORT = 8080
WEB_HOST = '0.0.0.0'
LOG_DIR = 'logs'
COMIC_DIR = 'strips'
COMIC_DB = 'comic.db'
INIT_LOCK = Lock()
CFG_FILE = None


def save_config():

    global WEB_PORT, WEB_HOST, LOG_DIR, COMIC_DIR, COMIC_DB
    conf_file = open(CFG_FILE, 'w')

    new_conf = ConfigParser()
    new_conf.add_section('General')
    new_conf.set('General', 'web_port', WEB_PORT)
    new_conf.set('General', 'web_host', WEB_HOST)
    new_conf.set('General', 'log_dir', LOG_DIR)
    new_conf.set('General', 'comic_dir', COMIC_DIR)
    new_conf.set('General', 'comic_db', COMIC_DB)
    new_conf.write(conf_file)

    return True


def load_config():
    global WEB_PORT, WEB_HOST, LOG_DIR, COMIC_DIR, COMIC_DB

    conf = ConfigParser()
    conf.read(CFG_FILE)
    try:
        WEB_PORT = conf.get('General', 'web_port')
        WEB_HOST = conf.get('General', 'web_host')
        LOG_DIR = conf.get('General', 'log_dir')
        COMIC_DIR = conf.get('General', 'comic_dir')
        COMIC_DB = conf.get('General', 'comic_db')

        return True
    except:
        print "Could not load config file creating default file"
        save_config()


def db_check():
    connection = db.DBConnection(COMIC_DB)

    queries = [
        'CREATE TABLE IF NOT EXISTS comic_list (id INTEGER PRIMARY KEY, name text, path text, first_page text, end_page text);',
        'CREATE TABLE IF NOT EXISTS comic_strips (comic_id NUMERIC, strip_no NUMERIC, location TEXT, page_url TEXT);',
        'CREATE TABLE IF NOT EXISTS download_cache (comic_id NUMERIC, strip_no NUMERIC, page_url TEXT, strip_url TEXT);',
        'CREATE TABLE IF NOT EXISTS view_cache (comic_id NUMERIC, last_strip NUMERIC);'
    ]

    for query in queries:
        connection.action(query)


def dir_check(path):
    ''' Create the directory if its not there '''
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def initialize():
    ''' Check what we have to check and set paramaters '''
    with INIT_LOCK:
        db_check()

        if load_config():
            # Lets create some directories
            dirs = [COMIC_DIR, LOG_DIR]

            OPS_LIST = [WEB_PORT, LOG_DIR, COMIC_DIR, COMIC_DB]

            for opts in OPS_LIST:
                print "Loaded: %s" % (opts)

            for folder in dirs:
                dir_check(os.path.join(DATA_DIR, folder))
