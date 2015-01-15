#!/usr/bin/env python
#
# settings.py
# Author: Alex Kozadaev (2014)
#

import common
import sqlgen

__table__ = "settings"
__fields__ = ["rad_ip", "rad_port", "rad_user", "rad_pass", "rad_secret"]


def new():
    """get a blank object with default values"""
    defaults = ["", 1813, "", "", ""]
    return dict(zip(__fields__, defaults))


@common.Transaction()
def get_all():
    """get settings object"""
    query = sqlgen.get_select_query(__fields__, [__table__])
    # using sql_get here since there is only 1 row in this table
    return common.sql_get(query, __fields__)


@common.Transaction()
def get(obj_id):
    raise NotImplementedError("Method not supported for Settings")


@common.Transaction()
def save(obj_dict):
    """update object"""
    assert(obj_dict is not None)
    query = sqlgen.get_update_query(obj_dict.keys(), __table__)
    return common.sql_save(query, obj_dict.values())


@common.Transaction()
def delete(obj_id):
    raise NotImplementedError("Method not supported for Settings")


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
