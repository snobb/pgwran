#!/usr/bin/env python
#
# subs_profile.py
# Author: Alex Kozadaev (2014)
#

import common
import sqlgen

__table__ = "subs_profile"
__pkey__ = "subs_id"
__fields__ = [
    "subs_id", "name", "ipaddr",
    "calling_id", "called_id",
    "imsi", "imei",
    "loc_info"
]


def new():
    """get a blank object with default values"""
    defaults = [
        -1, "New", "",
        "000000000000000", "web.apn",
        "90000000000000", "012345678901234",
        "f5f5"
    ]

    return dict(zip(__fields__, defaults))


@common.Transaction()
def get_all():
    """get all objects"""
    query = sqlgen.get_select_query(__fields__, [__table__])
    return common.sql_get_all(query, __fields__)


def notrans_get(obj_id):
    """get a single object by id"""
    sql_filter = "{}={}".format(__pkey__, obj_id)
    query = sqlgen.get_select_query(__fields__, [__table__], sql_filter)
    return common.sql_get(query, __fields__)


@common.Transaction()
def get(obj_id):
    return notrans_get(obj_id)


@common.Transaction()
def save(obj_dict):
    """update object"""
    assert(obj_dict is not None)
    subs_id = obj_dict[__pkey__]
    obj_dict = obj_dict.copy()
    obj_dict.pop(__pkey__)
    if subs_id == -1:
        # insert
        query = sqlgen.get_insert_query(obj_dict.keys(), __table__)
    else:
        # update
        sql_filter = "{}={}".format(__pkey__, subs_id)
        query = sqlgen.get_update_query(obj_dict.keys(), __table__, sql_filter)
    return common.sql_save(query, obj_dict.values())


@common.Transaction()
def delete(obj_id):
    """delete object"""
    sql_filter = "{}={}".format(__pkey__, obj_id)
    query = sqlgen.get_delete_query(__table__, sql_filter)
    return common.sql_delete(query)


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
