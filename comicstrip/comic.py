import os
import sys
import re

# Used to process URLS
import requests
import errno
import urlparse

# Used to find images
from BeautifulSoup import BeautifulSoup as bs

# Used to store images
from PIL import Image
from StringIO import StringIO

from comicstrip import db

# First function is to find all the next links and build a list of them with the strip number they should be associated with.
def page_find(comic_url):
    # This will run through all the next pages
    parse_page = bs(requests.get(comic_url).text)
    parsed_url = urlparse.urlparse(comic_url)

    # First find all the links on the page
    for links in parse_page.findAll(['a']):
        if re.compile(".*next.*", re.IGNORECASE).match(str(links)):
           if links['href'].lower().startswith('http'):
              next_page = links['href']
              print "CUR:%s NEXT:%s" % (comic_url,next_page)
              return next_page
           else:
              if parsed_url.path and not parsed_url.query:
                 parsed_url = list(parsed_url)
                 # Catch those stupid # refrences to the same page
                 if not re.compile('.*#$.*').match(links['href']):
                    parsed_url[2] = links['href']
                    next_page = urlparse.urlunparse(parsed_url)
                    print "CUR:%s NEXT:%s" % (comic_url,next_page)
                 else:
                    next_page = None
              else:
                 print "DEBUG: %s %s" % (parsed_url,links['href'])
                 next_page = list(parsed_url)
                 # Catch those stupid # refrences to the same page
                 if not re.compile('.*#$.*').match(links['href']):
                    if parsed_url.path.strip('/') not in links['href']:
                       next_page[4] = links['href'].strip('?')
                    else:
                       next_page[2] = links['href']
                       next_page[4] = None
                    next_page = urlparse.urlunparse(next_page)
                    print "CUR:%s NEXT:%s" % (comic_url,next_page)
                 else:
                    next_page = None
              return next_page
    else:
        print "FAILED: comic: %s" % (comic_url)
        return None

def grab_strip(comic_id,outpath,strip_no,current_url,replace=False):
    parsed = list(urlparse.urlparse(current_url))
    soup = bs(requests.get(current_url).text)

    # Loop through all the images soup finds
    for image in soup.findAll('img'):
        filename = image['src'].split('/')[-1]
        if filename.endswith(('.jpg','.png','.gif')):
           if image['src'].lower().startswith('http'):
              strip_img = requests.get(image["src"])
           else:
              parsed[2] = image['src']
              parsed[4] = None
              strip_img = requests.get(urlparse.urlunparse(parsed))

           if strip_img.status_code == requests.codes.ok:
              s = StringIO(strip_img.content)
              strip = Image.open(s)
              w,h = strip.size
              if w > 250 and h > 420 or w > 420 and h > 250:
                 filename = "%s%s" % (strip_no,os.path.splitext(filename)[-1])
                 path_exists(outpath)
                 outpath = os.path.join(outpath, filename)
                 print "PAGE: %s IMAGE: %s" % (current_url,filename)

                 if not os.path.exists(outpath):
                    strip.save(outpath)
                 else:
                    print "FOUND: %s" % (outpath)
                 return { 'strip_no': strip_no, 'page_url': current_url, 'location': outpath }
    else:
       return { 'strip_no': strip_no, 'page_url': current_url, 'location': 'SKIPPED' }

def update_engine(comic_id=None,que=None):
    # Connect to the db
    myDB = db.DBConnection()

    if comic_id != None:
       sqlQuery = 'SELECT id,path,first_page,end_page FROM comic_list WHERE id = (%s)' % (comic_id,)
    else:
       sqlQuery = 'SELECT id,path,first_page,end_page FROM comic_list'

    for info in myDB.select(sqlQuery):
        print "\r\n"
        # Populate some empty data stores
        db_upd_list = list()
        url_list = dict()
        # Grab the ending page if there is one.
        end_page = info[3]

        last_url = myDB.select('SELECT strip_no,page_url FROM comic_strips WHERE comic_id = (?) ORDER BY strip_no DESC LIMIT 1',(info[0],))
        if last_url:
           page_url = page_find(last_url[0][1])
           strip_no = last_url[0][0]
        else:
           page_url = info[2]
           strip_no = 0

        #while page_url != None and page_url not in url_list.values() and page_url != end_page and strip_no < 195:
        while page_url != None and page_url not in url_list.values() and page_url != end_page:
              strip_no += 1
              url_list[strip_no] = page_url
              page_url = page_find(page_url)

        for strip_no in url_list.keys():
            myDB.upsert('comic_strips',grab_strip(info[0],info[1],strip_no,url_list[strip_no]),{ 'comic_id': info[0], 'strip_no': strip_no })

def path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
           raise
