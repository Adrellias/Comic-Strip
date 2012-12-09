'''
 Author: <adrellias@gmail.com>
 url: https://github.com/adrellias
'''
from ConfigParser import ConfigParser
from threading import Lock
from comicstrip import db

import sys

# Some Defaults if they are not there alreedy

COMIC_LIST = None
WEB_PORT = 8080
LOG_DIR = 'logs'
COMIC_DIR = 'strips'
COMIC_DB = 'comic.db'
INIT_LOCK = Lock()


def save_config():

    new_conf = ConfigParser()
    new_conf.add_section('General')
    new_conf.set('General', 'web_port', WEB_PORT)
    new_conf.set('General', 'log_dir', LOG_DIR)
    new_conf.set('General', 'comic_download_dir', COMIC_DIR)
    new_conf.set('General', 'comic_db', COMIC_DIR)
    new_conf.write(sys.stdout)


def db_check():
    connection = db.DBConnection(COMIC_DB)

    queries = [
        'CREATE TABLE comic_list (id INTEGER PRIMARY KEY, name text, path text, first_page text, end_page text);',
        'CREATE TABLE comic_strips (comic_id NUMERIC, strip_no NUMERIC, location TEXT, page_url TEXT);',
        'CREATE TABLE download_cache (comic_id NUMERIC, strip_no NUMERIC, page_url TEXT, strip_url TEXT);',
        'CREATE TABLE view_cache (comic_id NUMERIC, last_strip NUMERIC);'
    ]

    for query in queries:
        connection.action(query)
        pass


def initialize():
    ''' Check what we have to check and set paramaters '''
    with INIT_LOCK:
        db_check()
        save_config()
        pass
