#!/usr/bin/env python
#
# controller.py
# Author: Alex Kozadaev (2014)
#

import dao
import bottle
import radius, netem


# Configuration
config = {
    "DATABASE"  : "database.db",
    "DB_SCHEMA" : "schema.sql",
    "DEBUG"     : True,
    "RELOADER"  : True,
    "EGRESS_IFACE": "eth1",
    "INGRESS_IFACE": "eth0",
}

# Globals
app = bottle.Bottle()
radius_config = radius.Config()


# DAO initialization
subs_dao = dao.SubscriberDao()
conn_prof_dao = dao.ConnectionProfileDao()
subs_prof_dao = dao.SubscriberProfileDao()
settings_dao = dao.SettingsDao()


### RADI functions ###
def radius_configure(subscriber):
    """configure radi as per current settings/subscriber profile"""
    global radius_config
    success, status_text, settings = settings_dao.get_all()
    if success:
        radius_config.radius_dest = settings.rad_ip.encode("ascii")
        radius_config.radius_port = int(settings.rad_port)

        if len(settings.rad_user) > 0:
            radius_config.username = settings.rad_user.encode("ascii")

        if len(settings.rad_secret) > 0:
            radius_config.radius_secret = settings.rad_secret.encode("ascii")

        if len(subscriber.called_id) > 0:
            radius_config.called_id = subscriber.called_id.encode("ascii")

        radius_config.framed_ip = subscriber.ipaddr.encode("ascii")

        if len(subscriber.calling_id) > 0:
            radius_config.calling_id = subscriber.calling_id.encode("ascii")

        if len(subscriber.imsi) > 0:
            radius_config.imsi = subscriber.imsi.encode("ascii")

        if len(subscriber.imei) > 0:
            radius_config.imei = subscriber.imei.encode("ascii")

        if len(subscriber.loc_info) > 0:
            radius_config.subs_loc_info = subscriber.loc_info.encode("ascii")
    return success, status_text


def radius_send(action):
    """send radius packet"""
    global radius_config
    radius_config.action = action
    radius.start_stop_session(radius_config)


### netem functions ###
def netem_obj_redo_filters(subscribers):
    """update and reapply filters based on the enabled_subscribers list"""
    cmd = netem.clear_filters()
    for subs in subscribers:
        if subs.enabled:
            cmd.extend(netem.add_filter(subs.conn_id, subs.ipaddr))
    netem.commit(cmd)


### session management ###
def enable_session(subs_profile, subs_status_list):
    """enable session"""
    netem_obj_redo_filters(subs_status_list)
    radius_configure(subs_profile)
    radius_send(radius.START)


def disable_session(subs_profile, subs_status_list):
    """diable session"""
    netem_obj_redo_filters(subs_status_list)
    radius_configure(subs_profile)
    radius_send(radius.STOP)


# dispatch handlers
@app.get("/static/<filepath:path>")
def server_static(filepath):
    """serving static files located at the static"""
    return bottle.static_file(filepath, root="static/")


@app.get("/")
def home_get():
    """GET handler for home"""
    return bottle.template("base.tmpl")


@app.get("/json/subscriber/get/")
def get_json_subscriber():
    errors = []
    connp_json, subs_json = [], []
    success, status_text, data = conn_prof_dao.get_all()
    if not success:
        errors.append("ERROR: {}".format(status_text))
    else:
        connp_json = [conn.get_dict() for conn in data]
        success, status_text, data = subs_dao.get_all()
        if not success:
            errors.append("ERROR: {}".format(status_text))
        else:
            subs_json = [subs.get_dict() for subs in data]

        return {"success" : success,
                "statusText" : "\n".join(errors),
                "data" : {
                    "conn_profiles" : connp_json,
                    "subscribers" : sorted(subs_json, key=lambda x: x["subs_id"])
                    }
                }


@app.post("/json/subscriber/save/")
def save_json_subscriber():
    form = bottle.request.forms

    subscriber = dao.Subscriber(
            subs_id = int(form.get("subs_id")),
            conn_id = int(form.get("conn_id")),
            enabled = form.get("enabled") == 'on',
            );

    success, status_text, data = subs_dao.save(subscriber)
    if not success:
        status_text = ("ERROR: Could not update the subscriber: "
                "{}").format(status_text)
    else:
        status_text = "The subscriber profile was updated successfully"

    return {"success" : success,
            "statusText" : status_text,
            "data": None}


@app.post("/json/subscriber/<action>/")
def change_json_subscriber(action):
    """enable subscriber"""
    form = bottle.request.forms

    subscriber = dao.Subscriber(
            subs_id = int(form.get("subs_id")),
            conn_id = int(form.get("conn_id")),
            enabled = form.get("enabled") == 'on',
            );

    success, status_text, data = subs_dao.save(subscriber)
    if not success:
        status_text = ("ERROR: subs_dao.save(subs) - {}").format(status_text)
    else:
        success, status_text, subs_status_list = subs_dao.get_all_status()
        if not success:
            status_text = "ERROR: subs_dao.get_all_status() - {}".format(status_text)
        else:
            success, status_text, subs_profile = subs_prof_dao.get(subscriber.subs_id)
            if not success:
                status_text = "ERROR: subs_dao.get(obj) - {}".format(status_text)
            else:
                if action == "enable":
                    enable_session(subs_profile, subs_status_list)
                elif action == "disable":
                    disable_session(subs_profile, subs_status_list)
                else:
                    success = False
                    status_text = "ERROR: Unknown action"

    return {"success" : success,
            "statusText" : status_text,
            "data": None}


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
    form = bottle.request.forms

    subs_profile = dao.SubscriberProfile(
            subs_id = int(form.get("subs_id")),
            name = form.get("name"),
            ipaddr = form.get("ipaddr"),
            calling_id = form.get("calling_id"),
            called_id = form.get("called_id"),
            imsi = form.get("imsi"),
            imei = form.get("imei"),
            loc_info = form.get("loc_info"),
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
    form = bottle.request.forms
    conn_profile = dao.ConnectionProfile(
            name = form.get("name"),
            description = form.get("description"),
            speed_down = form.get("speed_down"),
            speed_up = form.get("speed_up"),
            speed_var = form.get("speed_var"),
            latency_up = form.get("latency_up"),
            latency_down = form.get("latency_down"),
            latency_jitter = form.get("latency_jitter"),
            loss_down = form.get("loss_down"),
            loss_up = form.get("loss_up"),
            loss_jitter = form.get("loss_jitter"),
            conn_id = int(form.get("conn_id")),
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
        settings.rad_ip = form.get("rad_ip")
        settings.rad_port = form.get("rad_port")
        settings.rad_user = form.get("rad_user")
        settings.rad_pass = form.get("rad_pass")
        settings.rad_secret = form.get("rad_secret")
        success, status_text, data = settings_dao.save(settings)
        if not success:
            status_text = ("Could not update the settings: "
               " {}").format(status_text)
        else:
            status_text = "The settings were updated successfully"

    return {"success" : success,
            "statusText" : status_text,
            "data" : None }


if __name__ == "__main__":
    dao.initialize(config["DATABASE"], config["DB_SCHEMA"])
    success, status_text, connections = conn_prof_dao.get_all()
    if success:
        try:
            netem.commit(netem.initialize(connections,
                config["EGRESS_IFACE"], config["INGRESS_IFACE"]))
            app.run(host="0.0.0.0", port=8080,
                    debug=config["DEBUG"],
                    reloader=config["RELOADER"])
        finally:
            netem.commit(netem.clear_all())
    else:
        print >> sys.stderr, "ERROR: {}".format(status_text)


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
