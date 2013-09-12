# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

import os.path
import sqlite3
import time
import threading
import comicstrip

from comicstrip import logger

db_lock = threading.Lock()


def dbFilename(filename="comic.db", suffix=None):
    """
    @param filename: The sqlite database filename to use. If not specified,
                     will be made to be comic.db
    @param suffix: The suffix to append to the filename. A '.' will be added
                   automatically, i.e. suffix='v0' will make dbfile.db.v0
    @return: the correct location of the database file.
    """
    if suffix:
        filename = "%s.%s" % (filename, suffix)
    return os.path.join(comicstrip.DATA_DIR, filename)


class DBConnection:
    def __init__(self, filename="comic.db", suffix=None, row_type=None):

        self.filename = filename
        self.connection = sqlite3.connect(dbFilename(filename), 20)

        if row_type == "dict":
            self.connection.row_factory = self._dict_factory
        else:
            self.connection.row_factory = sqlite3.Row

    def action(self, query, args=None):

        with db_lock:

            if query is None:
                return

            sqlResult = None
            attempt = 0

            while attempt < 5:
                try:
                    if args is None:
                        logger.log(self.filename+": "+query)
                        sqlResult = self.connection.execute(query)
                    else:
                        logger.log(self.filename+": "+query+" with args "+str(args))
                        sqlResult = self.connection.execute(query, args)
                    self.connection.commit()
                    # get out of the connection attempt loop since we were successful
                    break
                except sqlite3.OperationalError, e:
                    if "unable to open database file" in e.message or "database is locked" in e.message:
                        #logger.log(u"DB error: "+ex(e), logger.WARNING)
                        attempt += 1
                        time.sleep(1)
                    else:
                        #logger.log(u"DB error: "+ex(e), logger.ERROR)
                        raise
                except sqlite3.DatabaseError, e:
                    #logger.log(u"Fatal error executing query: " + ex(e), logger.ERROR)
                    raise
            return sqlResult


    def select(self, query, args=None):

        sqlResults = self.action(query, args).fetchall()

        if sqlResults == None:
            return []

        return sqlResults

    def upsert(self, tableName, valueDict, keyDict):
        logger.log(u'TB: ' + str(tableName) + 'val: ' + str(valueDict) + 'key: ' + str(keyDict))
        changesBefore = self.connection.total_changes

        genParams = lambda myDict : [x + " = ?" for x in myDict.keys()]

        query = "UPDATE "+tableName+" SET " + ", ".join(genParams(valueDict)) + " WHERE " + " AND ".join(genParams(keyDict))

        self.action(query, valueDict.values() + keyDict.values())

        if self.connection.total_changes == changesBefore:
            query = "INSERT INTO "+tableName+" (" + ", ".join(valueDict.keys() + keyDict.keys()) + ")" + \
                     " VALUES (" + ", ".join(["?"] * len(valueDict.keys() + keyDict.keys())) + ")"
            self.action(query, valueDict.values() + keyDict.values())

    def tableInfo(self, tableName):
        # FIXME ? binding is not supported here, but I cannot find a way to escape a string manually
        cursor = self.connection.execute("PRAGMA table_info(%s)" % tableName)
        columns = {}
        for column in cursor:
            columns[column['name']] = { 'type': column['type'] }
        return columns

    # http://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
    def _dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

def sanityCheckDatabase(connection, sanity_check):
    sanity_check(connection).check()

class DBSanityCheck(object):
    def __init__(self, connection):
        self.connection = connection

    def check(self):
        pass
