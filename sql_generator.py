#!/usr/bin/env python
#
# sql_generator.py
# Author: Alex Kozadaev (2014)
#

class ClassGenerator(object):
    def __init__(self, **args):
        """generate an object out of a dictionary"""
        self.__dict__.update(args)

    def get_dictionary(self):
        return self.__dict__


def get_select_query(fields, tables, sql_filter=None):
    """get a select query based on fields, tables
    Input:
        fields      list: list of fields (can be a tuple)
        tables      list: list of tables (can be a tuple)
        sql_filter  string: sql filter for the select
    Returns: sql select query"""
    condition = ""
    if sql_filter != None:
        condition = " WHERE {}".format(sql_filter)
    return "SELECT {} FROM {}{}".format(",".join(fields),
            ",".join(tables), condition)

def get_update_query(fields, table, sql_filter=None):
    """get an update query based on fields and table
    Input:
        fields      list:list of fields (MUST BE A LIST)
        table       string:name of a table
        sql_filter  string:
    Returns: sql update query"""
    condition = ""
    if sql_filter != None:
        condition = " WHERE {}".format(sql_filter)
    return "UPDATE {} SET {}=?{}".format(
            table,
            "=?,".join(fields),
            condition)

def get_insert_query(fields, table):
    """get an insert query based on fields and table
    Input:
        fields      list:list of fields (can be a tuple)
        table       string:name of a table
        sql_filter  string:
    Returns: sql insert query"""
    return "INSERT INTO {}({}) VALUES {}".format(
            table,
            ",".join(fields),
            ",".join("?"*len(fields)))



if __name__ == "__main__":
    print get_select_query(
            ["subs_id", "conn_id", "value1", "value2", "value3"],
            ["table1", "table2"],
            "subs_id = conn_id")
    print get_select_query(
            ["subs_id"],
            ["table1"])
    print get_update_query(
            ["subs_id", "conn_id", "value1", "value2", "value3"],
            "table1",
            "subs_id = conn_id")
    print get_update_query(
            ["key"],
            "table1",
            "subs_id = conn_id")
    print get_insert_query(
            ["subs_id", "conn_id", "value1", "value2", "value3"],
            "table1")

# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
