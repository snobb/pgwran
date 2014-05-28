#!/usr/bin/env python
#
# controller.py
# Author: Alex Kozadaev (2014)
#

import dao
import bottle
from json import JSONEncoder, dumps as jsonify

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
db = dao.Dao(dao.DaoConnectorSQLite(config["DATABASE"]))


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


@app.get("/data/subs_profile/")
def get_data_subs_profile():
    """get subscriber profile data in one json blob"""
    error = []
    subs_json = None

    subs_profiles = db.get_all_subs_profiles()
    if not subs_profiles:
        error.append("Could not load the subcriber profiles from the db")
    else:
        subs_json = [subs.get_dict() for subs in subs_profiles]

    return {"success" : len(error) == 0,
            "error" : error,
            "subs_profiles" : subs_json }


@app.get("/data/conn_profile/")
def get_data_conn_profile():
    """get connection profile data in one json blob"""
    error = []
    conn_json = None

    conn_profiles = db.get_all_conn_profiles()
    if not conn_profiles:
        error.append("Could not load the connection profiles from the db")
    else:
        conn_json = [conn.get_dict() for conn in conn_profiles]

    return {"success" : len(error) == 0,
            "error" : error,
            "conn_profiles" : conn_json }


@app.get("/data/settings/")
def get_data_settings():
    """get settings data in one json blob"""
    error = []

    settings = db.get_settings()
    if not settings:
        error.append("Could not load settings from the db")

    return {"success" : len(error) == 0,
            "error" : error,
            "settings" : settings.get_dict()}


if __name__ == "__main__":
    db.init_schema(config["DB_SCHEMA"])
    app.run(host="localhost", port=8080, debug=True, reloader=True)

# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
