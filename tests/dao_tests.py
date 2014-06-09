#!/usr/bin/env python
#
# dao_tests.py
# Author: Alex Kozadaev (2014)
#


import os
import unittest
import dao

dao.initialize(":memory:", "tests/schema.sql")


class SubscriberDaoTest(unittest.TestCase):
    def setUp(self):
        dao.connector.get_db()
        self.dao = dao.SubscriberDao()

    def tearDown(self):
        dao.connector.close()

    def test_get_all(self):
        success, status, subs = self.dao.get_all()
        self.assertTrue(success)
        self.assertNotEquals(0, len(subs))
        self.assertEquals(4, len(subs))

        # self.assertEquals(subs[1].name, "3G")
        # self.assertEquals(subs[1].latency_up, 50)
        # self.assertEquals(subs[2].name, "2.5G")
        # self.assertEquals(subs[2].speed_up, 59.3)



class ConnProfDaoTest(unittest.TestCase):
    def setUp(self):
        dao.connector.get_db()
        self.dao = dao.ConnectionProfileDao()


    def tearDown(self):
        dao.connector.close()


    def test_get_all(self):
        success, status, conns = self.dao.get_all()
        self.assertTrue(success)
        self.assertNotEquals(0, len(conns))
        self.assertEquals(4, len(conns))

        self.assertEquals(conns[1].name, "3G")
        self.assertEquals(conns[1].latency_up, 100)
        self.assertEquals(conns[2].name, "2.5G")
        self.assertEquals(conns[2].speed_up, 59.3)


    def test_save_update(self):
        success, status, data = self.dao.get_all()
        self.assertTrue(success)
        conn = data[0]
        conn_id = conn.conn_id
        conn.name = "test"
        conn.speed_up = 101
        conn.loss_down = 202
        update_res = self.dao.save(conn)
        self.assertEquals("", update_res[1])
        self.assertTrue(update_res[0])

        success, status, conn = self.dao.get(conn_id)
        self.assertTrue(success)
        self.assertEquals(conn_id, conn.conn_id)
        self.assertEquals("test", conn.name);
        self.assertEquals(101, conn.speed_up);
        self.assertEquals(202, conn.loss_down);


    def test_save_insert(self):
        conn = dao.ConnectionProfile()
        conn.name = "test"
        conn.speed_up = 101
        conn.loss_down = 202
        success, status, ins_data = self.dao.save(conn)
        self.assertTrue(success)

        conns = self.dao.get_all()[2]
        self.assertEquals(5, len(conns))
        for conn in conns:
            if conn.name == "test":
                found = True
                self.assertTrue(ins_data > 0)
                self.assertEquals(101, conn.speed_up);
                self.assertEquals(202, conn.loss_down);
        self.assertTrue(found)


    def test_delete(self):
        success, _, data = self.dao.get_all()
        self.assertTrue(success)
        obj = data[1]
        conn_id = obj.conn_id
        conn_len = len(data)

        success, _, data = self.dao.delete(conn_id)
        self.assertTrue(success)

        success, _, data = self.dao.get_all()
        self.assertTrue(success)
        self.assertEquals(conn_len-1, len(data))

        success, _, data = self.dao.get(conn_id)
        self.assertTrue(success)
        self.assertEquals(None, data)


class SubscriberProfDaoTest(unittest.TestCase):
    def setUp(self):
        dao.initialize(":memory:", "tests/schema.sql")
        self.dao = dao.SubscriberProfileDao()

    def tearDown(self):
        dao.connector.close()


    def test_get_all(self):
        success, status, subs = self.dao.get_all()
        self.assertTrue(success)
        self.assertNotEquals(0, len(subs))
        self.assertEquals(4, len(subs))

        self.assertEquals(subs[0].name, "Marie")
        self.assertEquals(subs[2].name, "Linus")


    def test_save_update(self):
        success, status, subs = self.dao.get_all()
        self.assertTrue(success)
        subs = subs[1]
        subs.name = "test"
        subs.imsi = "1234"
        subs.called_id = "4567"
        update_res = self.dao.save(subs)
        self.assertTrue(update_res[0])

        subs_id = subs.subs_id

        success, status, subs = self.dao.get(subs_id)
        self.assertTrue(success)
        self.assertEquals(subs_id, subs.subs_id)
        self.assertEquals("test", subs.name);
        self.assertEquals("1234", subs.imsi);
        self.assertEquals("4567", subs.called_id);


    def test_save_insert(self):
        subs = dao.SubscriberProfile(
                 name="test_aaa",
                 imsi=2345,
                 calling_id=3456,
                 loc_info="f5f5")
        insert_res = self.dao.save(subs)
        self.assertTrue(insert_res[0])
        new_id = insert_res[2]
        self.assertTrue(new_id > 0)

        found = False
        success, status, subs = self.dao.get_all()
        self.assertTrue(success)
        self.assertEquals(5, len(subs))
        for sub in subs:
            if sub.subs_id == new_id:
                found = True
                self.assertEquals(new_id, sub.subs_id)
                self.assertEquals(2345, int(sub.imsi));
                self.assertEquals(3456, int(sub.calling_id));
                self.assertEquals("f5f5", sub.loc_info);
        self.assertTrue(found)


    def test_delete(self):
        success, _, data = self.dao.get_all()
        self.assertTrue(success)
        obj = data[1]
        subs_id = obj.subs_id
        subs_len = len(data)

        success, _, data = self.dao.delete(subs_id)
        self.assertTrue(success)

        success, _, data = self.dao.get_all()
        self.assertTrue(success)
        self.assertEquals(subs_len-1, len(data))

        success, _, data = self.dao.get(subs_id)
        self.assertTrue(success)
        self.assertEquals(None, data)


class SettingsDaoTest(unittest.TestCase):
    def setUp(self):
        dao.connector.get_db()
        self.dao = dao.SettingsDao()


    def tearDown(self):
        dao.connector.close()


    def test_get_all(self):
        success, status, settings = self.dao.get()
        self.assertTrue(success)
        self.assertEquals("", status)
        self.assertIsNotNone(settings)
        self.assertEquals("10.0.16.1", settings.rad_ip)
        self.assertEquals(1813, settings.rad_port)


    def test_save(self):
        sett_update_res = self.dao.save(
                dao.Settings(rad_secret="qwerty", rad_ip="1.1.1.1"))
        self.assertTrue(sett_update_res[0])

        success, status, settings = self.dao.get_all()
        self.assertTrue(success)
        self.assertEquals(settings.rad_secret, "qwerty");
        self.assertEquals(settings.rad_ip, "1.1.1.1");

# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
