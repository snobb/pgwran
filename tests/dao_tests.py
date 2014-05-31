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


    def test_get_all_subs_profiles(self):
        subs_res = self.dao.get_all_subs_profiles()
        self.assertTrue(subs_res["success"])
        subs = subs_res["data"]
        self.assertNotEquals(0, len(subs))
        self.assertEquals(4, len(subs))

        self.assertEquals(subs[0].name, "Marie")
        self.assertEquals(subs[2].name, "Linus")


    def test_update_subscriber(self):
        subs_res = self.dao.get_all_subs_profiles()
        self.assertTrue(subs_res["success"])
        subs = subs_res["data"][1]
        subs.name = "test"
        subs.imsi = "1234"
        subs.called_id = "4567"
        update_res = self.dao.update_subs_profile(subs)
        self.assertTrue(update_res["success"])

        subs_id = subs.subs_id

        found = False
        get_res = self.dao.get_all_subs_profiles()
        self.assertTrue(get_res["success"])
        for subs in get_res["data"]:
            if subs.subs_id == subs_id:
                found = True
                self.assertEquals("test", subs.name);
                self.assertEquals("1234", subs.imsi);
                self.assertEquals("4567", subs.called_id);
        self.assertTrue(found)


    def test_insert_subscriber(self):
        subs = Subscriber(
                name="test",
                imsi=2345,
                calling_id=3456,
                loc_info="f5f5")
        insert_res = self.dao.insert_subs_profile(subs)
        self.assertTrue(insert_res["success"])

        found = False
        subs = self.dao.get_all_subs_profiles()["data"]
        self.assertEquals(5, len(subs))
        for sub in subs:
            if sub.name == "test":
                found = True
                self.assertEquals(insert_res["data"], sub.subs_id)
                self.assertEquals(2345, int(sub.imsi));
                self.assertEquals(3456, int(sub.calling_id));
                self.assertEquals("f5f5", sub.loc_info);
        self.assertTrue(found)


    def test_get_all_conn_profiles(self):
        conns_res = self.dao.get_all_conn_profiles()
        self.assertTrue(conns_res["success"])
        conns = conns_res["data"]
        self.assertNotEquals(0, len(conns))
        self.assertEquals(4, len(conns))

        self.assertEquals(conns[1].name, "3G")
        self.assertEquals(conns[1].latency_up, 50)
        self.assertEquals(conns[2].name, "2.5G")
        self.assertEquals(conns[2].speed_up, 59.3)


    def test_update_connection(self):
        conns_res = self.dao.get_all_conn_profiles()
        self.assertTrue(conns_res["success"])
        conn = conns_res["data"][0]
        conn_id = conn.conn_id
        conn.name = "test"
        conn.speed_up = 101
        conn.loss_down = 202
        update_res = self.dao.update_conn_profile(conn)
        self.assertTrue(update_res["success"])

        found = False
        get_res = self.dao.get_all_conn_profiles()
        self.assertTrue(get_res["success"])
        for conn in get_res["data"]:
            if conn.conn_id == conn_id:
                found = True
                self.assertEquals("test", conn.name);
                self.assertEquals(101, conn.speed_up);
                self.assertEquals(202, conn.loss_down);
        self.assertTrue(found)


    def test_insert_connection(self):
        conn = Connection()
        conn.name = "test"
        conn.speed_up = 101
        conn.loss_down = 202
        insert_res = self.dao.insert_conn_profile(conn)
        self.assertTrue(insert_res["success"])

        found = False
        conns = self.dao.get_all_conn_profiles()["data"]
        self.assertEquals(5, len(conns))
        for conn in conns:
            if conn.name == "test":
                found = True
                self.assertEquals(insert_res["data"], conn.conn_id)
                self.assertEquals(101, conn.speed_up);
                self.assertEquals(202, conn.loss_down);
        self.assertTrue(found)


    def test_get_settings(self):
        sett_res = self.dao.get_settings()
        self.assertTrue(sett_res["success"])
        settings = sett_res["data"]
        self.assertIsNotNone(settings)
        self.assertEquals("10.0.16.1", settings.rad_ip)
        self.assertEquals(1813, settings.rad_port)


    def test_update_settings(self):
        sett_update_res = self.dao.update_settings(
                Settings(rad_secret="qwerty", rad_ip="1.1.1.1"))
        self.assertTrue(sett_update_res["success"])

        sett_res = self.dao.get_settings()
        self.assertTrue(sett_res["success"])
        settings = sett_res["data"]

        self.assertEquals(settings.rad_secret, "qwerty");
        self.assertEquals(settings.rad_ip, "1.1.1.1");



# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
