#!/usr/bin/env python
#
# subscriber.py
# Author: Alex Kozadaev (2014)
#

import common
import sqlgen
import subs_profile
import conn_profile

__table__ = "subscriber"
__pkey__ = "subs_id"
__fields__ = ["subs_id", "conn_id", "enabled"]

def new():
    """get a blank object with default values"""
    defaults = [-1, 0, 0]
    return dict(zip(__fields__, defaults))

@common.Transaction()
def get_all():
    """get all objects - makes recursive queries to get referenced objects.
    namely:
        subs_profile => obj.subs_profile
        conn_profile => conn_profile)
    """
    query = sqlgen.get_select_query(__fields__, [__table__])
    subscribers = common.sql_get_all(query, __fields__)

    for subs in subscribers:
        subs["subs_profile"] = subs_profile.notrans_get(subs["subs_id"])
        subs["conn_profile"] = conn_profile.notrans_get(subs["conn_id"])

    return subscribers

@common.Transaction()
def get(obj_id):
    """get a single object by id"""
    sql_filter = "{}={}".format(__pkey__, obj_id)
    query = sqlgen.get_select_query(__fields__, [__table__], sql_filter)
    subs = common.sql_get(query, __fields__)
    subs["subs_profile"] = subs_profile.notrans_get(subs["subs_id"])
    subs["conn_profile"] = conn_profile.notrans_get(subs["subs_id"])

    return subs

@common.Transaction()
def save(obj_dict):
    """update object"""
    assert(obj_dict != None)
    obj_dict = obj_dict.copy()
    subs_id = obj_dict["subs_id"]
    if subs_id == -1:
        raise NotImplementedError("Method is not supported (addition disabled)")
    else:
        obj_dict.pop(__pkey__)       # removing subs_id for query generation
        try:
            obj_dict.pop("conn_profile") # removing the profile objects
            obj_dict.pop("subs_profile") #
        except KeyError:
            pass
        sql_filter = "{}={}".format(__pkey__, subs_id)
    query = sqlgen.get_update_query(obj_dict.keys(), __table__, sql_filter)
    return common.sql_save(query, obj_dict.values())

@common.Transaction()
def delete(obj_id):
    """delete object"""
    raise NotImplementedError("Method not supported for this object ")


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
