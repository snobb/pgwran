#!/usr/bin/env python
#
# controller.py
# Author: Alex Kozadaev (2014)
#

import sys
import dao
import bottle
import netem
import radi as radius
import config


__version__ = "1.5"


# == Globals ==================================================================
app = bottle.Bottle()
radius_config = radius.Config()


# == RADI functions ===========================================================
def ascii(str):
    return str.encode("ascii", "ignore")


def radius_configure(subscriber):
    """configure radi as per current settings/subscriber profile"""
    global radius_config
    subs_profile = subscriber["subs_profile"]
    success, status_text, settings = dao.settings.get_all()
    if success:
        radius_config.radius_dest = ascii(settings["rad_ip"])
        radius_config.radius_port = int(settings["rad_port"])

        if len(settings["rad_user"]) > 0:
            radius_config.username = ascii(settings["rad_user"])

        if len(settings["rad_secret"]) > 0:
            setting_ascii = ascii(settings["rad_secret"])
            radius_config.radius_secret = setting_ascii

        if len(subs_profile["called_id"]) > 0:
            radius_config.called_id = ascii(subs_profile["called_id"])

        radius_config.framed_ip = ascii(subs_profile["ipaddr"])

        if len(subs_profile["calling_id"]) > 0:
            radius_config.calling_id = ascii(subs_profile["calling_id"])

        if len(subs_profile["imsi"]) > 0:
            radius_config.imsi = ascii(subs_profile["imsi"])

        if len(subs_profile["imei"]) > 0:
            radius_config.imei = ascii(subs_profile["imei"])

        if len(subs_profile["loc_info"]) > 0:
            loc_info_ascii = ascii(subs_profile["loc_info"])
            radius_config.subs_loc_info = loc_info_ascii

        radius_config.avps = list()

        if "conn_profile" in subscriber:
            conn_profile = subscriber["conn_profile"]
            if "rat_type" in conn_profile:
                rat_type = conn_profile["rat_type"]
                radius_config.avps.append(("3GPP-RAT-Type", rat_type))
    return success, status_text


def radius_send(action):
    """send radius packet"""
    global radius_config
    radius_config.action = action
    radius.start_stop_session(radius_config)


def radius_session(subscriber, action=radius.START):
    """send radius accounting for the given subscriber"""
    radius_configure(subscriber)
    radius_send(action)


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
                                      config.egress_iface,
                                      config.ingress_iface))
    return success, status_text, connections


def netem_update_status():
    """go through all subscribers and update netem status"""
    success, status_text, subs_list = dao.subscriber.get_all()
    if not success:
        status_text = "ERROR: dao.subscriber.get_all() - ""{}".format(
            status_text)
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

        return {"success": success,
                "statusText": "\n".join(errors),
                "data": {
                    "conn_profiles": connp_data,
                    "subscribers": sorted(subs_data,
                                          key=lambda x: x["subs_id"])
                    }
                }


@app.post("/json/subscriber/save/")
def save_json_subscriber():
    """save the subscriber and reapply current status"""
    subscriber = bottle.request.json

    subscriber["enabled"] = ("enabled" in subscriber and
                             subscriber["enabled"] == "on")

    subs_id = subscriber["subs_id"]
    success, status_text, subs_orig = dao.subscriber.get(subs_id)
    if success:
        success, status_text, data = dao.subscriber.save(subscriber)
        if not success:
            status_text = ("ERROR: dao.subscriber.save(subs) - {}").format(
                status_text)
        else:
            success, status_text, subscriber = dao.subscriber.get(subs_id)
            if success:
                if subscriber["enabled"] == subs_orig["enabled"]:
                    action = radius.INTERIM
                elif subscriber["enabled"]:
                    action = radius.START
                else:
                    action = radius.STOP

                radius_session(subscriber, action)
                netem_update_status()

    return {"success": success,
            "statusText": status_text,
            "data": None}


@app.get("/json/subs_profile/get/")
def get_json_subs_profile():
    """get subscriber profile data in one json blob"""
    success, status_text, subs_data = dao.subs_profile.get_all()
    if not success:
        status_text = "ERROR: {}".format(status_text)

    return {"success": success,
            "statusText": status_text,
            "data": {
                "subs_profiles": subs_data
                }
            }


@app.post("/json/subs_profile/save/")
def save_json_subs_profile():
    """save subscriber profile data in one json blob"""
    subs_profile = bottle.request.json
    subs_profile["subs_id"] = int(subs_profile["subs_id"])
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
        success, status, subscriber = dao.subscriber.get(
            subs_profile["subs_id"])
        if success and subscriber["enabled"]:
            radius_session(subscriber, radius.INTERIM)
            netem_update_status()

    return {"success": success,
            "statusText": status_text,
            "data": {
                "subs_id": subs_profile["subs_id"],
                "action": action
                }
            }


@app.get("/json/subs_profile/delete/<subs_id>")
def delete_json_subs_profile(subs_id):
    success, status_text, data = dao.subs_profile.delete(subs_id)
    return {"success": success,
            "statusText": status_text,
            "data": data}


@app.get("/json/conn_profile/get/")
def get_json_conn_profile():
    """get connection profile data in one json blob"""
    success, status_text, conn_json = dao.conn_profile.get_all()
    if not success:
        status_text = "ERROR: {}".format(status_text)

    return {"success": success,
            "statusText": status_text,
            "data": {
                "conn_profiles": conn_json
                }
            }


@app.post("/json/conn_profile/save/")
def save_json_conn_profile():
    """save connection profile data in one json blob"""
    conn_profile = bottle.request.json
    conn_profile["conn_id"] = int(conn_profile["conn_id"])

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

    # updating netem
    if success:
        success, status, subscribers = dao.subscriber.get_all()
        if success:
            for subscriber in subscribers:
                if (subscriber["enabled"] and
                        int(subscriber["conn_id"]) == conn_profile["conn_id"]):
                    radius_session(subscriber, radius.INTERIM)
        else:
            status_text = status

        netem_full_reload()

    return {"success": success,
            "statusText": status_text,
            "data": {
                "conn_id": conn_profile["conn_id"],
                "action": action
            }}


@app.get("/json/conn_profile/delete/<conn_id>")
def delete_json_conn_profile(conn_id):
    success, status_text, data = dao.conn_profile.delete(conn_id)
    return {"success": success,
            "statusText": status_text,
            "data": data}


@app.get("/json/settings/get/")
def get_json_settings():
    """get settings data in one json blob"""
    success, status_text, data = dao.settings.get_all()
    if not success:
        status_text = "ERROR: {}".format(status_text)

    return {"success": success,
            "statusText": status_text,
            "data": {
                "settings": data
            }}


@app.post("/json/settings/save/")
def save_json_settings():
    """save settings in the database"""
    success, status_text, settings = dao.settings.get_all()
    if success:
        settings = bottle.request.json
        success, status_text, data = dao.settings.save(settings)
        if not success:
            status_text = ("Could not update the settings: "
                           " {}").format(status_text)
        else:
            status_text = "The settings were updated successfully"

    return {"success": success,
            "statusText": status_text,
            "data": None}


if __name__ == "__main__":
    dao.initialize(config.database, config.db_schema)
    try:
        success, status_text, data = netem_update_profiles()
        if not success:
            print >>sys.stderr, status_text
            exit(1)

        success, status_text, subscribers = dao.subscriber.get_all()
        if not success:
            print >>sys.stderr, status_text
            exit(1)

        for subscriber in subscribers:
            if subscriber["enabled"]:
                radius_session(subscriber)

        netem_update_status()
        app.run(host=config.listen_address, port=config.listen_port,
                debug=config.debug,
                reloader=config.reloader)
    finally:
        netem.commit(netem.clear_all())


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
