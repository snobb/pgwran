#!/usr/bin/env python
#
# sqlite_connector.py
# Author: Alex Kozadaev (2014)
#

import sqlite3
import os.path

config = {
        "db_fname": "",
        "db_schema": "",
}
__db__ = None


def initialize(db_fname, db_schema=None):
    config["db_fname"] = db_fname
    config["db_schema"] = db_schema
    __db__ = None


def __init_db():
    """Creates the database tables."""
    with open(config["db_schema"], "r") as f:
        __db__.cursor().executescript(f.read())


def __connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(config["db_fname"], check_same_thread = False)
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context."""
    global __db__
    if not __db__:
        __db__ = __connect_db()
        __init_db()
        __db__.execute("PRAGMA foreign_keys=ON");
    return __db__



# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
