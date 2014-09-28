#!/usr/bin/env python
#
# __init__.py
# Author: Alex Kozadaev (2014)
#

import subscriber
import conn_profile
import subs_profile
import settings

def initialize(db_name, db_schema):
    import sqlite_conn
    sqlite_conn.initialize(db_name, db_schema)

def restart_connection():
    sqlite_conn.get_db()

def close():
    sqlite_conn.close()

# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
