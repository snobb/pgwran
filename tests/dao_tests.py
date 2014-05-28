#!/usr/bin/env python
#
# dao_tests.py
# Author: Alex Kozadaev (2014)
#


import os
import unittest
from dao import *

class DaoTest(unittest.TestCase):
    def setUp(self):
        self.dbname = ":memory:"
        self.connector = DaoConnectorSQLite(self.dbname)
        self.dao = Dao(self.connector)
        self.dao.init_schema("tests/schema.sql")


    def tearDown(self):
        self.connector.close_db()
        del(self.dao)


    def test_get_all_conn_profiles(self):
        conns = self.dao.get_all_conn_profiles()
        self.assertNotEquals(0, len(conns))
        self.assertEquals(4, len(conns))

        self.assertEquals(conns[1].name, "3G")
        self.assertEquals(conns[1].latency_up, 50)
        self.assertEquals(conns[2].name, "2.5G")
        self.assertEquals(conns[2].speed_up, 59.3)


    def test_get_all_subs_profiles(self):
        subs = self.dao.get_all_subs_profiles()
        self.assertNotEquals(0, len(subs))
        self.assertEquals(4, len(subs))

        self.assertEquals(subs[0].name, "Marie")
        self.assertEquals(subs[2].name, "Linus")


    def test_get_settings(self):
        settings = self.dao.get_settings()
        self.assertIsNotNone(settings)
        self.assertEquals("10.0.16.1", settings.rad_ip)
        self.assertEquals(1813, settings.rad_port)



# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
