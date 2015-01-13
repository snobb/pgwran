#!/usr/bin/env python
#
# test_dao_sqlgen.py
# Author: Alex Kozadaev (2014)
#

import os
import unittest
import dao.sqlgen as ds


class SQLGenTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_select_query(self):
        query = ds.get_select_query(
            ["subs_id", "conn_id", "value1", "value2", "value3"],
            ["table1", "table2"],
            "subs_id=conn_id")
        expect = ("SELECT subs_id,conn_id,value1,value2,value3 "
                  "FROM table1,table2 WHERE subs_id=conn_id")
        self.assertEquals(expect, query)

        query = ds.get_select_query(["subs_id"], ["table1"])

        expect = "SELECT subs_id FROM table1"
        self.assertEquals(expect, query)

    def test_update_query(self):
        query = ds.get_update_query(
            ["subs_id", "conn_id", "value1", "value2", "value3"],
            "table1",
            "subs_id=conn_id")
        expect = ("UPDATE table1 SET subs_id=?,conn_id=?,value1=?,"
                  "value2=?,value3=? WHERE subs_id=conn_id")
        self.assertEquals(expect, query)

        query = ds.get_update_query(["key"], "table1", "subs_id=conn_id")
        expect = "UPDATE table1 SET key=? WHERE subs_id=conn_id"
        self.assertEquals(expect, query)

    def test_insert_query(self):
        query = ds.get_insert_query(
            ["subs_id", "conn_id", "value1", "value2", "value3"],
            "table1")
        expect = ("INSERT INTO table1(subs_id,conn_id,value1,value2,"
                  "value3) VALUES (?,?,?,?,?)")
        self.assertEquals(expect, query)

    def test_delete_query(self):
        query = ds.get_delete_query("table1", "id=1")
        expect = "DELETE FROM table1 WHERE id=1"
        self.assertEquals(expect, query)


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
