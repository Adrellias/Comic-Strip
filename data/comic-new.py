import os
import sys
import urlparse
import errno
from BeautifulSoup import BeautifulSoup as bs
from urllib2 import HTTPError, URLError
from urllib2 import urlopen
from urllib2 import Request
from urllib import urlretrieve
from PIL import Image
from StringIO import StringIO
import re
import db

def first_page(current_url):
    parsed = list(urlparse.urlparse(current_url))
    soup = bs(urlopen(Request(current_url,None,headers)))

    for index, links in enumerate(soup.findAll('a')):
        if links.find(attrs={'title': re.compile("first", re.IGNORECASE)}) != None:
           parsed[2] = links['href']
           first_page = parsed
        if links.find(text=re.compile("first", re.IGNORECASE)) != None:
           parsed[2] = links['href']
           first_page = parsed
    return first_page

def next_page(current_url):
    parsed = list(urlparse.urlparse(current_url))
    soup = bs(urlopen(Request(current_url,None,headers)))

    for links in soup.findAll('a', attrs={'class': re.compile(".*next.*", re.IGNORECASE)}):
        if links['href'].lower().startswith('http'):
           next_page = links['href']
           return next_page
        else:
           if parsed[4]:
              parsed[4] = links['href'].split('?')[-1]
           else:
              parsed[2] = links['href']
           next_page = urlparse.urlunparse(parsed)
           print "NEXT PAGE: %s" % (urlparse.urlunparse(parsed))
           return next_page

    for links in soup.findAll('a', attrs={'title': re.compile(".*next.*", re.IGNORECASE)}):
        if links['href'].lower().startswith('http'):
           next_page = links['href']
           print "NEXT PAGE: %s" % (links['href'])
           return next_page
        else:
           if parsed[4]:
              parsed[4] = links['href'].split('?')[-1]
           else:
              parsed[2] = links['href']
           next_page = urlparse.urlunparse(parsed)
           print "NEXT PAGE: %s" % (urlparse.urlunparse(parsed))
           return next_page

    for links in soup.findAll('a', href=True):
        if re.search('.*next.*', links.text, re.IGNORECASE):
           if links['href'].lower().startswith('http'):
              next_page = links['href']
              print "NEXT PAGE: %s" % (links['href'])
              return next_page
           else:
              if parsed[4]:
                 parsed[4] = links['href'].split('?')[-1]
              else:
                 parsed[2] = links['href']
              next_page = urlparse.urlunparse(parsed)
              print "NEXT PAGE: %s" % (urlparse.urlunparse(parsed))
              return next_page

    print "ERROR NEXT: %s %s" % (urlparse.urlunparse(parsed),parsed)
    return None

def got_strip(comic_id,current_url):
    strip_no = db.get_last_strip(comic_id)
    strip_no += 1
    parsed = list(urlparse.urlparse(current_url))
    soup = bs(urlopen(Request(current_url,None,headers)))

    for image in soup.findAll('img'):
        filename = image['src'].split('/')[-1]
        if filename.endswith(('.jpg','.png','.gif')):
           outpath = os.path.join(db.get_comic_path(comic_id)[0], filename)
           if os.path.exists(outpath):
              print db.add_strip(comic_id,strip_no,outpath)
              print db.update_last_url(current_url,comic_id)
              return outpath

def get_strip(comic_id,current_url):
    strip_no = db.get_last_strip(comic_id)
    strip_no += 1
    parsed = list(urlparse.urlparse(current_url))
    soup = bs(urlopen(Request(current_url,None,headers)))

    # Loop through all the images soup finds
    for image in soup.findAll('img'):
	# Rip out the filename from the url
        filename = image['src'].split('/')[-1]
	# Does the filename end in a supported format
	# This needs to be changed, it should not matter as long as PIL opens it
        if filename.endswith(('.jpg','.png','.gif')):
           # Does the image link have the full url in it?
           if image['src'].lower().startswith('http'):
              try:
                  # Open the image and grab the with and height
                  strip_img = urlopen(Request(image["src"],None,headers))
                  s = StringIO(strip_img.read())
                  strip = Image.open(s)
                  w,h = strip.size
              # Watch for those errors
              except HTTPError, e:
                  print "ERROR: %s %s" % (e.code,urlparse.urlunparse(parsed))
                  w,h = 0,0
              # Watch for those errors
              except URLError, e:
                  print "ERROR: %s %s" % (e.reason,urlparse.urlunparse(parsed))
                  w,h = 0,0
              # Is the with and height of the picture lager on way or the other.
              # If it is check that the comic path is there or create it and save
              # the image file we just loaded.
              if w > 250 and h > 420 or w > 420 and h > 250:
                 make_sure_path_exists(db.get_comic_path(comic_id)[0])
                 # Use os.path.splitext(filename)[-1] to figure out and change filename to a strip no. Its cleaner
                 # than naming it to the strip the author used.
                 filename = "%s%s" % (strip_no,os.path.splitext(filename)[-1])
                 outpath = os.path.join(db.get_comic_path(comic_id)[0], filename)
                 strip.save(outpath)
                 db.add_strip(comic_id,strip_no,outpath,current_url)
                 db.update_last_url(current_url,comic_id)
                 print "PAGE: %s IMAGE: %s" % (current_url,filename)
                 return filename
           else:
              # This fires if the image['src'] does not contain the absolute path.
              # So we replace the last link in the url with our image and that should work right ?
              parsed[2] = image['src']
              try:
                  strip_img = urlopen(Request(urlparse.urlunparse(parsed),None,headers))
                  s = StringIO(strip_img.read())
                  strip = Image.open(s)
                  w,h = strip.size
              except HTTPError, e:
                  print "ERROR: %s %s" % (e.code,urlparse.urlunparse(parsed))
                  w,h = 0,0
              except URLError, e:
                  print "ERROR: %s %s" % (e.reason,urlparse.urlunparse(parsed))
                  w,h = 0,0
              if w > 250 and h > 420 or w > 420 and h > 250:
                 make_sure_path_exists(db.get_comic_path(comic_id)[0])
                 filename = "%s%s" % (strip_no,os.path.splitext(filename)[-1])
                 outpath = os.path.join(db.get_comic_path(comic_id)[0], filename)
                 # Update db stuff needs to be stuck in a class
                 strip.save(outpath)
                 db.add_strip(comic_id,strip_no,outpath,current_url)
                 db.update_last_url(current_url,comic_id)
                 print "PAGE: %s IMAGE: %s" % (current_url,filename)
                 return filename

    # If we find nothing update the last url we checked
    # and add the db reference that this image was skipped for some reason
    db.update_last_url(current_url,comic_id)
    db.add_strip(comic_id,strip_no,'nostrip',current_url)

def path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
           raise

headers = { 'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11' }

#comic_path = db.get_all_comic()
#db.add_comic('Jefbot','comic/jefbot','http://jefbot.com/2007/08/06/axis-powers-webcomic-michael/')

comic_id = 4

# Download the first comic - This wont be part of the update engine but to get the initial 
# comic this is how it will work. Update engine will check from last_url and then update

#get_strip(comic_id,db.get_last_url(comic_id)[0])
current_page = next_page(db.get_last_url(comic_id)[0])

while current_page != None:
      get_strip(comic_id,current_page)
      current_page = next_page(current_page)
