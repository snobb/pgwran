#!/usr/bin/env python
#
# subs_profile.py
# Author: Alex Kozadaev (2014)
#

import common
import sqlgen

__table__ = "subs_profile"
__fields__ = [
        "subs_id", "name", "ipaddr", "calling_id",
        "called_id", "imsi", "imei", "loc_info"
        ]

def new():
    """get a blank object with default values"""
    defaults = [
            -1, "New", "", "000000000000000",
            "web.apn", "90000000000000",
            "012345678901234", "f5f5"]

    return common.map2obj(dict(zip(__fields__, defaults)))

@common.Transaction()
def get_all():
    """get subscriber profile object"""
    query = sqlgen.get_select_query(__fields__, [__table__])
    return common.sql_get_all(query, __fields__)

@common.Transaction()
def get(obj_id):
    sql_filter = "subs_id={}".format(obj_id)
    query = sqlgen.get_select_query(__fields__, [__table__], sql_filter)
    return common.sql_get(query, __fields__)

@common.Transaction()
def save(obj):
    """update object"""
    assert(obj != None)
    obj_dict = obj.__dict__
    sql_filter = "subs_id={}".format(obj.subs_id)
    query = sqlgen.get_update_query(obj_dict.keys(), __table__, sql_filter)
    return common.sql_save(query, obj_dict.values())

@common.Transaction()
def delete(obj_id):
    """delete object"""
    sql_filter = "subs_id={}".format(obj_id)
    query = sqlgen.get_delete_query(__table__, sql_filter)
    return common.sql_delete(query)



# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
