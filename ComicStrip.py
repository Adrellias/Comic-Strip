import sys
import os
import threading
import signal
import locale

import comicstrip

from comicstrip import db
from comicstrip import thread_man

#signal.signal(signal.SIGINT,comicstrip.sig_handler)
#signal.signal(signal.SIGTERM,comicstrip.sig_handler)


def daemonize():
    """ Split off and fork this god damn process
        This was pulled from http://code.activestate.com/recipes/66012-fork-a-daemon-process-on-unix/
    """
    # Do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    # Decouple from parent environment
    os.setsid()
    # Make sure I can read my own files and shut out others
    prev = os.umask(0)
    os.umask(prev and int('077', 8))

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent, print eventual PID before
            print "Daemon PID %d" % pid
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    # Replace stdin with /dev/null
    dev_null = file('/dev/null', 'r')
    os.dup2(dev_null.fileno(), sys.stdin.fileno())


def main():
    """
    comicStrips
    """
    comicstrip.MY_FULLNAME = os.path.normpath(os.path.abspath(__file__))
    comicstrip.MY_NAME = os.path.basename(comicstrip.MY_FULLNAME)
    comicstrip.PROG_DIR = os.path.dirname(comicstrip.MY_FULLNAME)
    comicstrip.DATA_DIR = comicstrip.PROG_DIR
    comicstrip.CREATEPID = False
    comicstrip.DAEMON = False

    comicstrip.SYS_ENCODING = None

    print "FULL NAME:" + comicstrip.MY_FULLNAME
    print "MY NAME:" + comicstrip.MY_NAME
    print "PROG DIR:" + comicstrip.PROG_DIR
    print "DATA DIR:" + comicstrip.DATA_DIR

    try:
        locale.setlocale(locale.LC_ALL, "")
        comicstrip.SYS_ENCODING = locale.getpreferredencoding()
    except (locale.Error, IOError):
        pass

  # For OSes that are poorly configured I'll just randomly force UTF-8
    if not comicstrip.SYS_ENCODING or comicstrip.SYS_ENCODING in ('ANSI_X3.4-1968', 'US-ASCII', 'ASCII'):
        comicstrip.SYS_ENCODING = 'UTF-8'

    if not hasattr(sys, "setdefaultencoding"):
        reload(sys)

    try:
        # pylint: disable=E1101
        # On non-unicode builds this will raise an AttributeError, if encoding type is not valid it throws a LookupError
        sys.setdefaultencoding(comicstrip.SYS_ENCODING)
    except:
        print 'Sorry, you MUST add the Sick Beard folder to the PYTHONPATH environment variable'
        print 'or find another way to force Python to use ' + comicstrip.SYS_ENCODING + ' for string encoding.'
        sys.exit(1)

    # Need console logging for comicstrip.py and SickBeard-console.exe
    consoleLogging = (not hasattr(sys, "frozen")) or (comicstrip.MY_NAME.lower().find('-console') > 0)

    print consoleLogging

    # Rename the main thread
    threading.currentThread().name = "MAIN"

    print comicstrip.SYS_ENCODING

if __name__ == "__main__":
    main()
    comicstrip.initialize()
