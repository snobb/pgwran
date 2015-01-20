#!/usr/bin/env python
#
# test_dao.py
# Author: Alex Kozadaev (2014)
#


import os
import unittest
import dao

dao.initialize(":memory:", "tests/schema.sql")


class SubscriberDaoTest(unittest.TestCase):
    def setUp(self):
        dao.restart_connection()

    def tearDown(self):
        dao.close()

    def test_get_all(self):
        success, status, subs = dao.subscriber.get_all()
        self.assertTrue(success)
        self.assertNotEquals(0, len(subs))
        self.assertEquals(4, len(subs))

        self.assertEquals(2, subs[1]["subs_id"])
        self.assertEquals(2, subs[1]["conn_id"])
        self.assertEquals(subs[1]["subs_profile"]["name"], "John")
        self.assertEquals(subs[1]["subs_profile"]["ipaddr"], "10.0.0.20")
        self.assertEquals(subs[1]["subs_profile"]["imsi"], "90108576436201")
        self.assertEquals(subs[1]["conn_profile"]["name"], "3G")
        self.assertEquals(subs[1]["conn_profile"]["rat_type"], 3)
        self.assertEquals(subs[2]["subs_profile"]["name"], "Linus")
        self.assertEquals(subs[2]["subs_profile"]["ipaddr"], "10.0.0.30")
        self.assertEquals(subs[2]["subs_profile"]["imsi"], "90156451177704")
        self.assertEquals(subs[2]["conn_profile"]["name"], "2.5G")
        self.assertEquals(subs[2]["conn_profile"]["rat_type"], 2)

    def test_get(self):
        success, status, subs = dao.settings.get(1)
        self.assertFalse(success)
        self.assertTrue(status.startswith("Method"))

    def test_save_update(self):
        success, status, subs = dao.subscriber.get_all()
        self.assertTrue(success)
        self.assertNotEquals(0, len(subs))
        self.assertEquals(4, len(subs))

        s1 = subs[1]
        s2 = subs[2]
        s1["conn_id"] = s2["conn_id"]
        success, status, subs = dao.subscriber.save(s1)
        self.assertTrue(success)

        success, status, subs = dao.subscriber.get_all()
        self.assertTrue(success)
        self.assertNotEquals(0, len(subs))
        self.assertEquals(4, len(subs))
        self.assertEquals(subs[1]["conn_profile"]["name"], "2.5G")

    def test_save_insert(self):
        subs = dao.subscriber.new()
        success, status, subs = dao.subscriber.save(subs)
        self.assertFalse(success)
        self.assertTrue(status.startswith("Method"))

    def test_delete(self):
        success, status, subs = dao.settings.delete(1)
        self.assertFalse(success)
        self.assertTrue(status.startswith("Method"))


class ConnProfDaoTest(unittest.TestCase):
    def setUp(self):
        dao.restart_connection()

    def tearDown(self):
        dao.close()

    def test_get_all(self):
        success, status, conns = dao.conn_profile.get_all()
        self.assertTrue(success)

        self.assertNotEquals(0, len(conns))
        self.assertEquals(4, len(conns))

        self.assertEquals(conns[1]["name"], "3G")
        self.assertEquals(conns[1]["latency_up"], 100)
        self.assertEquals(conns[1]["rat_type"], 3)
        self.assertEquals(conns[2]["name"], "2.5G")
        self.assertEquals(conns[2]["speed_up"], 59.3)
        self.assertEquals(conns[2]["rat_type"], 2)

    def test_save_update(self):
        success, status, data = dao.conn_profile.get_all()
        self.assertTrue(success)
        conn = data[0]
        conn_id = conn["conn_id"]
        conn["name"] = "test"
        conn["speed_up"] = 101
        conn["loss_down"] = 202
        conn["rat_type"] = 7
        update_res = dao.conn_profile.save(conn)
        self.assertEquals("", update_res[1])
        self.assertTrue(update_res[0])

        success, status, conn = dao.conn_profile.get(conn_id)
        self.assertTrue(success)
        self.assertEquals(conn_id, conn["conn_id"])
        self.assertEquals("test", conn["name"])
        self.assertEquals(101, conn["speed_up"])
        self.assertEquals(202, conn["loss_down"])
        self.assertEquals(7, conn["rat_type"])

    def test_save_insert(self):
        conn = dao.conn_profile.new()
        conn["name"] = "test"
        conn["speed_up"] = 101
        conn["loss_down"] = 202
        success, status, ins_data = dao.conn_profile.save(conn)
        self.assertTrue(success)

        res, _, conns = dao.conn_profile.get_all()
        self.assertTrue(res)
        self.assertEquals(5, len(conns))
        for conn in conns:
            if conn["name"] == "test":
                found = True
                self.assertTrue(ins_data > 0)
                self.assertEquals(101, conn["speed_up"])
                self.assertEquals(202, conn["loss_down"])
        self.assertTrue(found)

    def test_delete(self):
        success, _, data = dao.conn_profile.get_all()
        self.assertTrue(success)
        conn_id = data[0]["conn_id"]
        conn_len = len(data)

        success, _, data = dao.conn_profile.delete(conn_id)
        self.assertTrue(success)

        success, _, data = dao.conn_profile.get_all()
        self.assertTrue(success)
        self.assertEquals(conn_len-1, len(data))

        success, _, data = dao.conn_profile.get(conn_id)
        self.assertTrue(success)
        self.assertEquals(None, data)


class SubscriberProfDaoTest(unittest.TestCase):
    def setUp(self):
        dao.restart_connection()

    def tearDown(self):
        dao.close()

    def test_new(self):
        obj_dict = dao.subs_profile.new()
        self.assertIsNotNone(obj_dict)
        self.assertEquals(-1, obj_dict["subs_id"])
        self.assertEquals("New", obj_dict["name"])
        self.assertEquals("", obj_dict["ipaddr"])
        self.assertEquals("000000000000000", obj_dict["calling_id"])
        self.assertEquals("web.apn", obj_dict["called_id"])
        self.assertEquals("90000000000000", obj_dict["imsi"])
        self.assertEquals("012345678901234", obj_dict["imei"])
        self.assertEquals("f5f5", obj_dict["loc_info"])

    def test_get_all(self):
        success, status, subs = dao.subs_profile.get_all()
        self.assertTrue(success)
        self.assertNotEquals(0, len(subs))
        self.assertEquals(4, len(subs))

        self.assertEquals(subs[0]["name"], "Marie")
        self.assertEquals(subs[2]["name"], "Linus")

    def test_save_update(self):
        success, status, subs = dao.subs_profile.get_all()
        self.assertTrue(success)
        subs = subs[1]
        subs["name"] = "test"
        subs["imsi"] = "1234"
        subs["called_id"] = "4567"
        update_res = dao.subs_profile.save(subs)
        self.assertTrue(update_res[0])

        subs_id = subs["subs_id"]

        success, status, subs = dao.subs_profile.get(subs_id)
        self.assertTrue(success)
        self.assertEquals(subs_id, subs["subs_id"])
        self.assertEquals("test", subs["name"])
        self.assertEquals("1234", subs["imsi"])
        self.assertEquals("4567", subs["called_id"])

    def test_save_insert(self):
        obj_dict = dao.subs_profile.new()
        obj_dict["name"] = "test_aaa"
        obj_dict["imsi"] = 2345
        obj_dict["calling_id"] = 3456
        obj_dict["loc_info"] = "f5f5"

        insert_res = dao.subs_profile.save(obj_dict)
        self.assertTrue(insert_res[0])
        new_id = insert_res[2]
        self.assertTrue(new_id > 0)

        found = False
        success, status, subs = dao.subs_profile.get_all()
        self.assertTrue(success)
        self.assertEquals(5, len(subs))
        for sub in subs:
            if sub["subs_id"] == new_id:
                found = True
                self.assertEquals(new_id, sub["subs_id"])
                self.assertEquals(2345, int(sub["imsi"]))
                self.assertEquals(3456, int(sub["calling_id"]))
                self.assertEquals("f5f5", sub["loc_info"])
        self.assertTrue(found)

        success, status, subs = dao.subscriber.get_all()
        self.assertTrue(success)
        self.assertEquals(subs[4]["subs_id"], new_id)
        self.assertEquals(subs[4]["conn_id"], 1)
        self.assertEquals(subs[4]["enabled"], False)

    def test_delete(self):
        success, _, data = dao.subs_profile.get_all()
        self.assertTrue(success)
        subs_id = data[1]["subs_id"]
        subs_len = len(data)

        success, _, data = dao.subs_profile.delete(subs_id)
        self.assertTrue(success)

        success, _, data = dao.subs_profile.get_all()
        self.assertTrue(success)
        self.assertEquals(subs_len-1, len(data))

        success, _, data = dao.subs_profile.get(subs_id)
        self.assertTrue(success)
        self.assertEquals(None, data)


class SettingsDaoTest(unittest.TestCase):
    def setUp(self):
        dao.restart_connection()

    def tearDown(self):
        dao.close()

    def test_new(self):
        obj_dict = dao.settings.new()

        self.assertIsNotNone(obj_dict)
        self.assertEquals("", obj_dict["rad_ip"])
        self.assertEquals(1813, obj_dict["rad_port"])
        self.assertEquals("", obj_dict["rad_user"])
        self.assertEquals("", obj_dict["rad_pass"])
        self.assertEquals("", obj_dict["rad_secret"])

    def test_get_all(self):
        success, status, settings = dao.settings.get_all()
        self.assertTrue(success)
        self.assertEquals("", status)
        self.assertIsNotNone(settings)
        self.assertEquals("10.0.16.1", settings["rad_ip"])
        self.assertEquals(1813, settings["rad_port"])

    def test_get(self):
        success, status, settings = dao.settings.get(1)
        self.assertFalse(success)
        self.assertTrue(status.startswith("Method"))

    def test_save(self):
        obj_dict = dao.settings.new()
        obj_dict["rad_secret"] = "qwerty"
        obj_dict["rad_ip"] = "1.1.1.1"
        sett_update_res = dao.settings.save(obj_dict)
        self.assertTrue(sett_update_res[0])

        success, status, settings = dao.settings.get_all()
        self.assertTrue(success)
        self.assertEquals(settings["rad_secret"], "qwerty")
        self.assertEquals(settings["rad_ip"], "1.1.1.1")

    def test_delete(self):
        success, status, settings = dao.settings.delete(1)
        self.assertFalse(success)
        self.assertTrue(status.startswith("Method"))


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
