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


# @app.get("/json")
# def get_json():
#     """get all the db data in one json blob"""
#     error = []
#
#     subs_success, subs_error = db.get_all_subscribers()
#     if not subs_success:
#         error.append(subs_error)
#
#     conn_success, conn_error = db.get_all_connections()
#     if not conn_success:
#         error.append(conn_error)
#
#     return {"success" : subs_success and conn_success,
#             "error" : error,
#             "subscriber" : subscriber,
#             "connection" : connection }


@app.get("/json/get/subs_profile/")
def get_json_subs_profile():
    """get subscriber profile data in one json blob"""
    error = []
    subs_json = None

    get_res = db.get_all_subs_profiles()
    success, status_text = get_res["success"], ""
    if not success:
        status_text = "ERROR: {}".format(get_res["statusText"])
    else:
        subs_json = [subs.get_dict() for subs in get_res["data"]]

    return {"success" : success,
            "statusText" : status_text,
            "data": {
                "subs_profiles" : subs_json
                }
            }


@app.post("/json/save/subs_profile/")
def save_json_subs_profile():
    """save subscriber profile data in one json blob"""
    error = []
    subs_json = None

    form = bottle.request.forms

    print form.get("sprof_subs_id")

    subs_profile = dao.Subscriber(
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
        insert_res = db.insert_subs_profile(subs_profile)
        success = insert_res["success"]
        subs_profile.subs_id = insert_res["data"]
        action = "insert"
        if not success:
            status_text = ("ERROR: Could not create a subscriber "
                        "profile: {}").format(insert_res["statusText"])
        else:
            status_text = "The subscriber profile was created successfully"
    else:
        update_res = db.update_subs_profile(subs_profile)
        success = update_res["success"]
        action = "update"
        if not success:
            status_text = ("ERROR: Could not update the subscriber "
                        "profile: {}").format(update_res["statusText"])
        else:
            status_text = "The subscriber profile was updated successfully"

    return {"success" : success,
            "statusText" : status_text,
            "data": {
                "subs_id": subs_profile.subs_id,
                "action": action
                }
            }


@app.get("/json/get/conn_profile/")
def get_json_conn_profile():
    """get connection profile data in one json blob"""
    error = []
    conn_json = None

    conn_result = db.get_all_conn_profiles()
    success, status_text = conn_result["success"], ""
    if not conn_result["success"]:
        status_text = "ERROR: {}".format(conn_result["statusText"])
    else:
        conn_json = [conn.get_dict() for conn in conn_result["data"]]

    return {"success" : len(error) == 0,
            "statusText" : "\n".join(error),
            "data" : {
                "conn_profiles" : conn_json
                }
            }


@app.post("/json/save/conn_profile/")
def save_json_conn_profile():
    """save connection profile data in one json blob"""
    error = []
    conn_json = None

    form = bottle.request.forms
    conn_profile = dao.Connection(
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
        insert_res = db.insert_conn_profile(conn_profile)
        success = insert_res["success"]
        conn_profile.conn_id = insert_res["data"]
        action = "insert"
        if not success:
            status_text = ("ERROR: Could not create a connection "
                        "profile: {}").format(insert_res["statusText"])
        else:
            status_text = "The connection profile was created successfully"
    else:
        update_res = db.update_conn_profile(conn_profile)
        success = update_res["success"]
        action = "update"
        if not success:
            status_text = ("ERROR: Could not update the connection "
                        "profile: {}").format(update_res["statusText"])
        else:
            status_text = "The connection profile was updated successfully"

    return {"success" : success,
            "statusText" : status_text,
            "data": {
                "conn_id": conn_profile.conn_id,
                "action": action
                }
            }


@app.get("/json/get/settings/")
def get_json_settings():
    """get settings data in one json blob"""
    error = []

    settings_res = db.get_settings()
    success, status_text = settings_res["success"], ""
    if not success:
        status_text = "ERROR: {}".format(settings_res["statusText"])

    return {"success" : success,
            "statusText" : status_text,
            "data": {
                "settings" : settings_res["data"].get_dict()
                }
            }


@app.post("/json/save/settings/")
def save_json_settings():
    """save settings in the database"""
    get_res = db.get_settings()
    success, status_text = get_res["success"], get_res["statusText"]
    if get_res["success"]:
        settings = get_res["data"]
        form = bottle.request.forms
        settings.rad_ip = form.get("settings_rad_ip")
        settings.rad_port = form.get("settings_rad_port")
        settings.rad_user = form.get("settings_rad_user")
        settings.rad_pass = form.get("settings_rad_pass")
        settings.rad_secret = form.get("settings_rad_secret")
        update_res = db.update_settings(settings)
        success = update_res["success"]
        if not success:
            status_text = ("Could not update the settings: "
               " {}").format(update_res["statusText"])
        else:
            status_text = "The settings were updated successfully"

    return {"success" : success,
            "statusText" : status_text,
            "data" : "" }


if __name__ == "__main__":
    db.init_schema(config["DB_SCHEMA"])
    app.run(host="localhost", port=8080, debug=True, reloader=True)

# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
