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

subs_dao = dao.SubscriberDao()
conn_prof_dao = dao.ConnectionProfileDao()
subs_prof_dao = dao.SubscriberProfileDao()
settings_dao = dao.SettingsDao()

# dispatch handlers
@app.get("/static/<filepath:path>")
def server_static(filepath):
    """serving static files located at the static"""
    return bottle.static_file(filepath, root="static/")

@app.get("/")
def home_get():
    """GET handler for home"""
    return bottle.template("base.tmpl")


@app.get("/json/subs_profile/get/")
def get_json_subs_profile():
    """get subscriber profile data in one json blob"""
    subs_json = None

    success, status_text, data = subs_prof_dao.get_all()
    if not success:
        status_text = "ERROR: {}".format(status_text)
    else:
        subs_json = [subs.get_dict() for subs in data]

    return {"success" : success,
            "statusText" : status_text,
            "data": {
                "subs_profiles" : subs_json
                }
            }


@app.post("/json/subs_profile/save/")
def save_json_subs_profile():
    """save subscriber profile data in one json blob"""
    subs_json = None

    form = bottle.request.forms

    print form.get("sprof_subs_id")

    subs_profile = dao.SubscriberProfile(
            subs_id = int(form.get("sprof_subs_id")),
            name = form.get("sprof_subs_name"),
            ipaddr = form.get("sprof_subs_ipaddr"),
            calling_id = form.get("sprof_subs_calling_id"),
            called_id = form.get("sprof_subs_called_id"),
            imsi = form.get("sprof_subs_imsi"),
            imei = form.get("sprof_subs_imei"),
            loc_info = form.get("sprof_subs_loc_info"),
            );

    if subs_profile.subs_id == -1:
        success, status_text, data = subs_prof_dao.save(subs_profile)
        subs_profile.subs_id = data
        action = "insert"
        if not success:
            status_text = ("ERROR: Could not create a subscriber "
                        "profile: {}").format(status_text)
        else:
            status_text = "The subscriber profile was created successfully"
    else:
        success, status_text, data = subs_prof_dao.save(subs_profile)
        action = "update"
        if not success:
            status_text = ("ERROR: Could not update the subscriber "
                        "profile: {}").format(status_text)
        else:
            status_text = "The subscriber profile was updated successfully"

    return {"success" : success,
            "statusText" : status_text,
            "data": {
                "subs_id": subs_profile.subs_id,
                "action": action
                }
            }


@app.get("/json/subs_profile/delete/<subs_id>")
def delete_json_subs_profile(subs_id):
    success, status_text, data = subs_prof_dao.delete(subs_id)
    return {"success" : success,
            "statusText" : status_text,
            "data": data }



@app.get("/json/conn_profile/get/")
def get_json_conn_profile():
    """get connection profile data in one json blob"""
    conn_json = None

    success, status_text, data = conn_prof_dao.get_all()
    if not success:
        status_text = "ERROR: {}".format(status_text)
    else:
        conn_json = [conn.get_dict() for conn in data]

    return {"success" : success,
            "statusText" : status_text,
            "data" : {
                "conn_profiles" : conn_json
                }
            }


@app.post("/json/conn_profile/save/")
def save_json_conn_profile():
    """save connection profile data in one json blob"""
    conn_json = None

    form = bottle.request.forms
    conn_profile = dao.ConnectionProfile(
            name = form.get("cprof_name"),
            description = form.get("cprof_description"),
            speed_down = form.get("cprof_speed_down"),
            speed_up = form.get("cprof_speed_up"),
            speed_var = form.get("cprof_speed_var"),
            latency_up = form.get("cprof_latency_up"),
            latency_down = form.get("cprof_latency_down"),
            latency_jitter = form.get("cprof_latency_jitter"),
            loss_down = form.get("cprof_loss_down"),
            loss_up = form.get("cprof_loss_up"),
            loss_jitter = form.get("cprof_loss_jitter"),
            conn_id = int(form.get("cprof_conn_id")),
            );

    if conn_profile.conn_id == -1:
        success, status_text, data = conn_prof_dao.save(conn_profile)
        conn_profile.conn_id = data
        action = "insert"
        if not success:
            status_text = ("ERROR: Could not create a connection "
                        "profile: {}").format(status_text)
        else:
            status_text = "The connection profile was created successfully"
    else:
        success, status_text, data = conn_prof_dao.save(conn_profile)
        action = "update"
        if not success:
            status_text = ("ERROR: Could not update the connection "
                        "profile: {}").format(status_text)
        else:
            status_text = "The connection profile was updated successfully"

    return {"success" : success,
            "statusText" : status_text,
            "data": {
                "conn_id": conn_profile.conn_id,
                "action": action
                }
            }


@app.get("/json/conn_profile/delete/<conn_id>")
def delete_json_conn_profile(conn_id):
    success, status_text, data = conn_prof_dao.delete(conn_id)
    return {"success" : success,
            "statusText" : status_text,
            "data": data }


@app.get("/json/settings/get/")
def get_json_settings():
    """get settings data in one json blob"""
    success, status_text, data = settings_dao.get()
    if not success:
        status_text = "ERROR: {}".format(status_text)

    return {"success" : success,
            "statusText" : status_text,
            "data": {
                "settings" : data.get_dict()
                }
            }


@app.post("/json/settings/save/")
def save_json_settings():
    """save settings in the database"""
    success, status_text, settings = settings_dao.get()
    if success:
        form = bottle.request.forms
        settings.rad_ip = form.get("settings_rad_ip")
        settings.rad_port = form.get("settings_rad_port")
        settings.rad_user = form.get("settings_rad_user")
        settings.rad_pass = form.get("settings_rad_pass")
        settings.rad_secret = form.get("settings_rad_secret")
        success, status_text, data = settings_dao.save(settings)
        if not success:
            status_text = ("Could not update the settings: "
               " {}").format(status_text)
        else:
            status_text = "The settings were updated successfully"

    return {"success" : success,
            "statusText" : status_text,
            "data" : "" }


if __name__ == "__main__":
    dao.initialize("database.db", "schema.sql")
    app.run(host="localhost", port=8080, debug=True, reloader=True)

# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
