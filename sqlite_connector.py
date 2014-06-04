#!/usr/bin/env python
#
# sqlite_connector.py
# Author: Alex Kozadaev (2014)
#

import sqlite3
import os.path


class DBFactory(object):
    def __init__(self, db_fname=":memory", db_schema=None):
        self.db_fname = db_fname
        self.db_schema = db_schema
        self.db = None
        self.init_db()


    def get_db(self):
        """Opens a new database connection if there is none yet for the
        current application context."""
        if not self.db:
            self.db = self.connect_db()
            self.db.execute("PRAGMA foreign_keys=ON");
        return self.db


    def connect_db(self):
        """Connects to the specific database."""
        rv = sqlite3.connect(self.db_fname, check_same_thread = False)
        rv.row_factory = sqlite3.Row
        self.db = rv
        return self.db


    def init_db(self):
        """Creates the database tables."""
        self.db = self.connect_db()
        with open(self.db_fname, "r") as f:
            self.db.cursor().executescript(f.read())



class ConnectDB(object):
    def __init__(self, db_factory):
        self.db_factory = db_factory

    def __call__(self, func):
        def wrapped(*args, **kwargs):
            try:
                db = self.db_factory.get_db()
                db.execute("PRAGMA foreign_keys=ON");
                db.execute("BEGIN TRANSACTION")

                print "here"
                kwargs["db"] = self
                func(*args, **kwargs)

                db.commit()
            except sqlite3.Error as e:
                db.rollback()
            finally:
                if db:
                    db.close()
        return wrapped


    def get_db(self):
        return self.db_factory.get_db()


    def execute_db(self, query, args):
        """Insert into the table"""
        self.get_db().execute(query, args)


    def query_db(self, query, args=(), one=False):
        """Queries the database and returns a list of rows"""
        cur = self.get_db().execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv



if __name__ == "__main__":
    db_factory = DBFactory("test.db", "schema.sql")

    @ConnectDB(db_factory)
    def test_db(*args, **kwargs):
        print kwargs
        values = kwargs["db"].query_db("select * from conn_profile")
        for val in values:
            print val

    test_db()

# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
