#!/usr/bin/env python
#
# controller.py
# Author: Alex Kozadaev (2014)
#

import dao
import bottle
import netem, radi as radius
import config


# == Globals ==================================================================
app = bottle.Bottle()
radius_config = radius.Config()


# == RADI functions ===========================================================
def radius_configure(subscriber):
    """configure radi as per current settings/subscriber profile"""
    global radius_config
    success, status_text, settings = dao.settings.get_all()
    if success:
        radius_config.radius_dest = settings["rad_ip"].encode("ascii")
        radius_config.radius_port = int(settings["rad_port"])

        if len(settings["rad_user"]) > 0:
            radius_config.username = settings["rad_user"].encode("ascii")

        if len(settings["rad_secret"]) > 0:
            radius_config.radius_secret = settings["rad_secret"].encode("ascii")

        if len(subscriber["called_id"]) > 0:
            radius_config.called_id = subscriber["called_id"].encode("ascii")

        radius_config.framed_ip = subscriber["ipaddr"].encode("ascii")

        if len(subscriber["calling_id"]) > 0:
            radius_config.calling_id = subscriber["calling_id"].encode("ascii")

        if len(subscriber["imsi"]) > 0:
            radius_config.imsi = subscriber["imsi"].encode("ascii")

        if len(subscriber["imei"]) > 0:
            radius_config.imei = subscriber["imei"].encode("ascii")

        if len(subscriber["loc_info"]) > 0:
            radius_config.subs_loc_info = subscriber["loc_info"].encode("ascii")
    return success, status_text

def radius_send(action):
    """send radius packet"""
    global radius_config
    radius_config.action = action
    radius.start_stop_session(radius_config)

def radius_session(subs_profile, do_start=True):
    """send radius accounting for the given subscriber"""
    radius_configure(subs_profile)
    if do_start:
        radius_send(radius.START)
    else:
        radius_send(radius.STOP)


# == netem functions ==========================================================
def netem_redo_filters(subscribers):
    """update and reapply filters based on the enabled_subscribers list"""
    cmd = netem.clear_filters()
    for subs in subscribers:
        if subs["enabled"]:
            subs_profile = subs["subs_profile"]
            cmd.extend(netem.add_filter(subs["conn_id"],
                subs_profile["ipaddr"]))
    netem.commit(cmd)

def netem_update_profiles(do_cleanup=False):
    """apply connection profiles"""
    if do_cleanup:
        netem.commit(netem.clear_all())

    success, status_text, connections = dao.conn_profile.get_all()
    if success:
        netem.commit(netem.initialize(connections,
            config.egress_iface, config.ingress_iface))
    return success, status_text, connections

def netem_update_status():
    """go through all subscribers and update netem status"""
    success, status_text, subs_list = dao.subscriber.get_all()
    if not success:
        status_text = "ERROR: dao.subscriber.get_all() - {}".format(status_text)
    else:
        netem_redo_filters(subs_list)
    return success, status_text, subs_list

def netem_full_reload():
    # Updating the netem
    netem_update_profiles(do_cleanup=True)
    netem_update_status()


# == dispatch handlers ========================================================
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
    success, status_text, connp_data = dao.conn_profile.get_all()
    if not success:
        errors.append("ERROR: {}".format(status_text))
    else:
        success, status_text, subs_data = dao.subscriber.get_all()
        if not success:
            errors.append("ERROR: {}".format(status_text))

        return {"success" : success,
                "statusText" : "\n".join(errors),
                "data" : {
                    "conn_profiles" : connp_data,
                    "subscribers" : sorted(subs_data, key=lambda x: x["subs_id"])
                    }
                }


@app.post("/json/subscriber/save/")
def save_json_subscriber():
    """save the subscriber and reapply current status"""
    form = bottle.request.forms

    subscriber = {
            "subs_id" :  int(form.get("subs_id")),
            "conn_id" :  int(form.get("conn_id")),
            "enabled" :  form.get("enabled") == 'on'
    }

    subs_id = subscriber["subs_id"]
    success, status_text, data = dao.subscriber.save(subscriber)
    if not success:
        status_text = ("ERROR: dao.subscriber.save(subs) - {}").format(
                status_text)
    else:
        success, status_text, subs_prof_profile = dao.subs_profile.get(subs_id)
        if not success:
            status_text = "ERROR: dao.subscriber.get_all() - {}".format(
                    status_text)
        else:
            radius_session(subs_prof_profile, subscriber["enabled"])
            netem_update_status()

    return {"success" : success,
            "statusText" : status_text,
            "data" : None}


@app.get("/json/subs_profile/get/")
def get_json_subs_profile():
    """get subscriber profile data in one json blob"""
    success, status_text, subs_data = dao.subs_profile.get_all()
    if not success:
        status_text = "ERROR: {}".format(status_text)

    return {"success" : success,
            "statusText" : status_text,
            "data": {
                "subs_profiles" : subs_data
                }
            }


@app.post("/json/subs_profile/save/")
def save_json_subs_profile():
    """save subscriber profile data in one json blob"""
    form = bottle.request.forms

    subs_profile = {
            "subs_id"       : int(form.get("subs_id")),
            "name"          : form.get("name"),
            "ipaddr"        : form.get("ipaddr"),
            "calling_id"    : form.get("calling_id"),
            "called_id"     : form.get("called_id"),
            "imsi"          : form.get("imsi"),
            "imei"          : form.get("imei"),
            "loc_info"      : form.get("loc_info")
            }

    if subs_profile["subs_id"] == -1:
        success, status_text, data = dao.subs_profile.save(subs_profile)
        subs_profile["subs_id"] = data
        action = "insert"
        if not success:
            status_text = ("ERROR: Could not create a subscriber "
                        "profile: {}").format(status_text)
        else:
            status_text = "The subscriber profile was created successfully"
    else:
        success, status_text, data = dao.subs_profile.save(subs_profile)
        action = "update"
        if not success:
            status_text = ("ERROR: Could not update the subscriber "
                        "profile: {}").format(status_text)
        else:
            status_text = "The subscriber profile was updated successfully"

        # updating radius and netem
        success, status, subs = dao.subscriber.get(subs_profile["subs_id"])
        if success and subs["enabled"]:
            radius_session(subs_profile, True)
            netem_update_status()


    return {"success" : success,
            "statusText" : status_text,
            "data": {
                "subs_id": subs_profile["subs_id"],
                "action": action
                }
            }


@app.get("/json/subs_profile/delete/<subs_id>")
def delete_json_subs_profile(subs_id):
    success, status_text, data = dao.subs_profile.delete(subs_id)
    return {"success" : success,
            "statusText" : status_text,
            "data": data }


@app.get("/json/conn_profile/get/")
def get_json_conn_profile():
    """get connection profile data in one json blob"""
    success, status_text, conn_json = dao.conn_profile.get_all()
    if not success:
        status_text = "ERROR: {}".format(status_text)

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
    conn_profile = {
        "name"              : form.get("name"),
        "description"       : form.get("description"),
        "speed_down"        : form.get("speed_down"),
        "speed_up"          : form.get("speed_up"),
        "speed_var"         : form.get("speed_var"),
        "latency_up"        : form.get("latency_up"),
        "latency_down"      : form.get("latency_down"),
        "latency_jitter"    : form.get("latency_jitter"),
        "loss_down"         : form.get("loss_down"),
        "loss_up"           : form.get("loss_up"),
        "loss_jitter"       : form.get("loss_jitter"),
        "conn_id"           : int(form.get("conn_id")),
    }

    if conn_profile["conn_id"] == -1:
        success, status_text, data = dao.conn_profile.save(conn_profile)
        conn_profile["conn_id"] = data
        action = "insert"
        if not success:
            status_text = ("ERROR: Could not create a connection "
                        "profile: {}").format(status_text)
        else:
            status_text = "The connection profile was created successfully"
    else:
        success, status_text, data = dao.conn_profile.save(conn_profile)
        action = "update"
        if not success:
            status_text = ("ERROR: Could not update the connection "
                        "profile: {}").format(status_text)
        else:
            status_text = "The connection profile was updated successfully"

    #updating netem
    if success:
        netem_full_reload()

    return {"success" : success,
            "statusText" : status_text,
            "data": {
                "conn_id": conn_profile["conn_id"],
                "action": action
                }
            }


@app.get("/json/conn_profile/delete/<conn_id>")
def delete_json_conn_profile(conn_id):
    success, status_text, data = dao.conn_profile.delete(conn_id)
    return {"success" : success,
            "statusText" : status_text,
            "data": data }


@app.get("/json/settings/get/")
def get_json_settings():
    """get settings data in one json blob"""
    success, status_text, data = dao.settings.get_all()
    if not success:
        status_text = "ERROR: {}".format(status_text)

    return {"success" : success,
            "statusText" : status_text,
            "data": {
                "settings" : data
                }
            }


@app.post("/json/settings/save/")
def save_json_settings():
    """save settings in the database"""
    success, status_text, settings = dao.settings.get_all()
    if success:
        form = bottle.request.forms
        settings["rad_ip"] = form.get("rad_ip")
        settings["rad_port"] = form.get("rad_port")
        settings["rad_user"] = form.get("rad_user")
        settings["rad_pass"] = form.get("rad_pass")
        settings["rad_secret"] = form.get("rad_secret")
        success, status_text, data = dao.settings.save(settings)
        if not success:
            status_text = ("Could not update the settings: "
               " {}").format(status_text)
        else:
            status_text = "The settings were updated successfully"

    return {"success" : success,
            "statusText" : status_text,
            "data" : None }


if __name__ == "__main__":
    dao.initialize(config.database, config.db_schema)
    try:
        success, status_text, data = netem_update_profiles()
        if not success:
            print status_text
            exit(1)

        success, status_text, subscribers = dao.subscriber.get_all()
        if not success:
            print status_text
            exit(1)

        for subs in subscribers:
            if subs["enabled"]:
                radius_session(subs["subs_profile"], True)

        netem_update_status()
        app.run(host=config.listen_address, port=config.listen_port,
                debug=config.debug,
                reloader=config.reloader)
    finally:
        netem.commit(netem.clear_all())


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
