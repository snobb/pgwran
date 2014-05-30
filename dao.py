#!/usr/bin/env python
#
# dao.py
# Author: Alex Kozadaev (2014)
#

import sqlite3

class GenericDaoObject(object):
    def get_dict(self):
        return self.__dict__

    def set_dict(self, values):
        self.__dict__ = values

    def get_fields(self):
        return self.get_dict().keys()

    def get_values(self):
        return self.get_dict().values()

    def __str__(self):
        template = ": {}  ".join(self.get_fields())
        return template.format(self.get_dict.values())


class Connection(GenericDaoObject):
    """Connection storage object"""
    def __init__(self, name="New", description="", speed_down=2000, speed_up=2000,
                speed_var=100, latency_up=200, latency_down=200,
                latency_jitter=100, loss_down=0.01, loss_up=0.01,
                loss_jitter=0.005, conn_id=-1):
        self.conn_id = conn_id
        self.name = name
        self.description = description
        self.speed_down = speed_down
        self.speed_up = speed_up
        self.speed_var = speed_var
        self.latency_up = latency_up
        self.latency_down = latency_down
        self.latency_jitter = latency_jitter
        self.loss_down = loss_down
        self.loss_up = loss_up
        self.loss_jitter = loss_jitter


class Subscriber(GenericDaoObject):
    """Subscriber storage object"""
    def __init__(self, name="new", ipaddr="", calling_id = "000000000000000",
            called_id = "web.apn", imsi = "90000000000000",
            imei = "012345678901234", loc_info = "f5f5", subs_id=-1, conn_id=0,
            enabled=False):
        self.subs_id = subs_id
        self.name = name
        self.ipaddr = ipaddr
        self.calling_id = calling_id
        self.called_id = called_id
        self.imsi = imsi
        self.imei = imei
        self.loc_info = loc_info


    def __str__(self):
        return ("name: {}  ipaddr: {} calling_id: {}  called_id: {}  imsi: {}"
                "imei: {} loc_info: {}").format(self.name, self.ipaddr,
                        self.calling_id, self.called_id, self.imsi, self.imei,
                        self.loc_info)


class Settings(GenericDaoObject):
    """Settings storage object"""
    def __init__(self, rad_ip="", rad_port=1813, rad_user="", rad_pass="",
            rad_secret=""):
        self.rad_ip = rad_ip
        self.rad_port = rad_port
        self.rad_user = rad_user
        self.rad_pass = rad_pass
        self.rad_secret = rad_secret

    def __str__(self):
        return ("rad_ip: {} rad_port: {} rad_user: rad_pass {}, "
                "rad_secret: {}").format(self.rad_ip, self.rad_port,
                        self.rad_user, self.rad_pass, self.rad_secret)


class Client(GenericDaoObject):
    """Client storage object"""
    def __init__(self, subscriber, connection, enabled=True, client_id = -1):
        self.client_id = client_id
        self.subscriber = subscriber
        self.connection = connection
        self.enabled = enabled


    def __str__(self):
        return ("subscriber: {} connection: {} enabled: {}").format(
                self.subscriber, self.connection, self.enabled)


class DaoConnectorSQLite(object):
    """SQLite connector"""
    def __init__(self, dbname):
        self.dbname = dbname
        self.db = None


    def connect_db(self):
        """Connects to the specific database."""
        rv = sqlite3.connect(self.dbname, check_same_thread = False)
        rv.row_factory = sqlite3.Row
        return rv


    def get_db(self):
        """Opens a new database connection if there is none yet for the
        current application context."""
        if not self.db:
            self.db = self.connect_db()
            self.db.execute("PRAGMA foreign_keys=ON");
        return self.db


    def begin_transaction(self):
        """begin a transaction"""
        db = self.get_db()
        db.execute("BEGIN TRANSACTION")


    def commit(self):
        """commit transaction"""
        db = self.get_db()
        db.commit()


    def rollback(self):
        """rollback current transaction"""
        db = self.get_db()
        db.rollback()


    def close_db(self):
        """Closes the database again at the end of the request."""
        if self.db:
            self.db.close()


    def init_db(self, fname="schema.sql"):
        """Creates the database tables."""
        db = self.get_db()
        with open(fname, "r") as f:
            db.cursor().executescript(f.read())


    def execute_db(self, query, args):
        """Insert into the table"""
        try:
            db = self.get_db()
            db.execute(query, args)
        except sqlite3.Error as e:
            return False, e
        return True, None

    def execute_db_list(self, queries, args):
        try:
            db = self.get_db()
            db.execute("BEGIN TRANSACTION")
            for query in queries:
                db.execute(query, args)
            db.commit()
        except sqlite3.Error as e:
            db.rollback()
            return False, e
        return True, None


    def query_db(self, query, args=(), one=False):
        """Queries the database and returns a list of dictionaries."""
        cur = self.get_db().execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv


    def query_object(self, obj_class, table, filters=None):
        fields = obj_class().get_fields()
        query = "SELECT {} FROM {}".format(",".join(fields), table)
        if filters:
            query += "WHERE {}".format(filters)

        values = []
        res_all = self.query_db(query, [], False)
        if len(res_all):
            for res in res_all:
                obj_instance = obj_class()
                obj_instance.set_dict(dict(zip(fields, res)))
                values.append(obj_instance)
            return values
        return None


    def update_object(self, obj, table, filters=None):
        fields = obj.get_fields()
        query = "UPDATE {} SET {}=?".format(table, "=?,".join(fields))
        if filters:
            query += "WHERE {}".format(filters)
        return self.execute_db(query, obj.get_values())


class Dao(object):
    def __init__(self, connector):
        self.connector = connector


    def init_schema(self, fname="schema.sql"):
        """load the database schema"""
        self.connector.init_db(fname)


    def get_all_conn_profiles(self):
        return self.connector.query_object(Connection, "conn_profile")


    def get_all_subs_profiles(self):
        return self.connector.query_object(Subscriber, "subs_profile")


    def get_settings(self):
        settings = self.connector.query_object(Settings, "settings");
        if settings and len(settings) > 0:
            return settings[0]
        return None


    def update_settings(self, settings):
        return self.connector.update_object(settings, "settings")



# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
