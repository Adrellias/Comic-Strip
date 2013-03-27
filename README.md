comicStrip
==========

*comicStrip is currently really early alpha release. There may be severe bugs in it and at any given time it may not work at all.*

comicStrip is a web-comic archiver. It watches your favorite web-comic for a new release and when they are posted, downloads
and indexes them localy for offline viewing. 

Currently the logic it uses supports only a limited amount of web-comic navigation methods. (Planning on making it configurable later)

Features Included

* Automaticaly check for new comic release
* Automaticaly download images and index them
* Offline viewer via webinterface (Remembers last strip viewed)

**comicStrip uses the following projects:**

* [cherrypy][cherrypy]
* [requests][requests]
* http://www.makotemplates.org/download.html

**comicStrip borrows and re-uses code from:**

* [Sick-Beard][Sick-Beard]
 
## Dependencies

To run comicStrip from source you will need Python 2.7.3+ and Mako 0.7.0+. The [binary releases][Mako] are standalone.


[cherrypy]: http://www.cherrypy.org
[Sick-Beard]: http://sickbeard.com/
[requests]: http://docs.python-requests.org/en/latest/
[Mako]: http://www.makotemplates.org/download.html


More info later..
