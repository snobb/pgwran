#!/usr/bin/env python
#
# controller.py
# Author: Alex Kozadaev (2014)
#

import db
import bottle

# Configuration
config = {
    "DATABASE"  : "database.db",
    "DB_SCHEMA" : "schema.sql",
    "DEBUG"     : True,
    "EGRESS_IFACE": "eth1",
    "INGRESS_IFACE": "eth3",
}

# Globals
app = bottle.Bottle()
db = db.DB(db.DBConnectorSQLite(config["DATABASE"]))


# dispatch handlers
@app.get("/static/<filepath:path>")
def server_static(filepath):
    """serving static files located at the static"""
    return bottle.static_file(filepath, root="static/")


@app.get("/")
def home_get():
    """GET handler for home"""
    return bottle.template("base.tmpl")


@app.get("/data")
def get_data():
    """get all the db data in one json blob"""
    error = []

    subs_success, subs_error = db.get_all_subscribers()
    if not subs_success:
        error.append(subs_error)

    conn_success, conn_error = db.get_all_connections()
    if not conn_success:
        error.append(conn_error)

    return {"success" : subs_success and conn_success,
            "error" : error,
            "subscriber" : subscriber,
            "connection" : connection }


@app.get("/data/connection")
def get_data_connection():
    """get all the db data in one json blob"""
    error = []

    conn_success, conn_error = db.get_all_connections()
    if not conn_success:
        error.append(conn_error)

    return {"success" : conn_success,
            "error" : error,
            "connection" : connection }



if __name__ == "__main__":
    db.init_schema(config["DB_SCHEMA"])
    app.run(host="localhost", port=8080, debug=True, reloader=True)

# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
