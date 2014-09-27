#!/usr/bin/env python
#
# common.py
# Author: Alex Kozadaev (2014)
#

import sqlgen
import sqlite_conn as connector

class Transaction(object):
    """Transaction Decorator class"""
    def __init__(self):
        """constructor for the transaction"""
        pass

    def __call__(self, func):
        """wrap the function and do the transaction handling"""
        def wrapped(*args, **kwargs):
            success, status, data = True, "", None
            try:
                connector.begin_transaction()
                data = func(*args, **kwargs)
                connector.commit()
            except Exception as e:
                success = False
                status = e.message
                connector.rollback()
            return (success, status, data)
        return wrapped


def map2obj(values):
    """convert a dictionary to an object"""
    class ClassGen(object):
        def __init__(self, **args):
            """generate an object out of a dictionary"""
            self.__dict__.update(args)
        def get_dictionary(self):
            return self.__dict__
    return ClassGen(**values)

def obj2map(obj):
    """convert object to a dictionary"""
    return obj.__dict__

def sql_get_all(query, fields):
    """get all the values from the db. At ths point the query should contain
    all the necessary informaton about the query (eg. table, filters, etc)"""
    obj_list = connector.query_db(query, [])
    if len(obj_list):
        return [map2obj(dict(zip(fields, obj))) for obj in obj_list]
    return None

def sql_get(query, fields):
    """get one the values from the db. At ths point the query should contain
    all the necessary informaton about the query (eg. table, filters, etc)"""
    obj = connector.query_db(query, [], True)
    if obj:
        return map2obj(dict(zip(fields, obj)))
    return None

def sql_save(query, values):
    """insert/update values in the DB. At this point the query should have everything
    but the values in it (with =? arguments as a template).  The values
    parameters MUST be in the same order as the list of fields or else it would
    likely corrupt database."""
    assert(type(values) == list)
    return connector.execute_db(query, values)

def sql_delete(query):
    """delete object from the db. At this point the query should contain all the
    information in it (eg. table, filters, etc)."""
    return connector.execute_db(query, [])


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
