#!/usr/bin/env python
#
# dao.py
# Author: Alex Kozadaev (2014)
#

import sqlite3
import sqlite_connector as connector

class ConnectDB(object):
    def __init__(self):
        pass

    def __call__(self, func):
        def wrapped(*args, **kwargs):
            try:
                self.db.execute("PRAGMA foreign_keys=ON");
                self.db.execute("BEGIN TRANSACTION")
                kwargs["db"] = self
                func(*args, **kwargs)
                self.db.commit()
            except sqlite3.Error as e:
                self.db.rollback()
                raise Exception(e.message)
            finally:
                if self.db:
                    self.db.close()
        return wrapped


    @property
    def db(self):
        db = connector.get_db()
        if not db:
            raise ValueError("ERROR: db was not initialized")
        return db


    def execute_db(self, query, args):
        """Insert into the table"""
        self.db.execute(query, args)


    def query_db(self, query, args=(), one=False):
        """Queries the database and returns a list of rows"""
        print "loading here"
        cur = self.db.execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv



class GenericDaoObject(object):
    def get_keys(self):
        return ([name for name in self.__dict__.keys() if
                not name.startswith("__")])

    def get_values(self):
        return ([getattr(self, name) for name in self.__dict__.keys() if
                not name.startswith("__")])

    def __str__(self):
        str_list = []
        for k, v in zip(self.get_keys(), self.get_values()):
            str_list.append("{}: {}".format(k, v))
        return ", ".join(str_list)


class ConnectionProfile(GenericDaoObject):
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

        self.__id__ = "conn_id"
        self.__table__ = "conn_profile"


class GenericDaoInterface():
    def get_all():
        raise NotImplementedError()
    def get(obj_id):
        raise NotImplementedError()
    def save(obj):
        raise NotImplementedError()
    def delete(obj):
        raise NotImplementedError()


class ConnectionProfileDAO(GenericDaoInterface):
    def get_all():
        pass
    def get(obj_id):
        pass
    def save(obj):
        pass
    def delete(obj):
        pass


class ConnectionProfileDAO(GenericDaoInterface):
    def get_all():
        pass
    def get(obj_id):
        pass
    def save(obj):
        pass
    def delete(obj):
        pass


if __name__ == "__main__":
    connector.initialize("test.db", "schema.sql")

    @ConnectDB()
    def test_db(*args, **kwargs):
        db = kwargs["db"]
        values = db.query_db("select * from conn_profile")
        for val in values:
            print val

    test_db()


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
