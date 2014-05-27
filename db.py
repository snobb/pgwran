#!/usr/bin/env python
#
# db.py
# Author: Alex Kozadaev (2013)
#

import sqlite3


class DBConnector(object):
    """Connector prototype object"""
    def __init__(self):
        pass
    def connect_db(self):
        pass
    def begin_transaction(self):
        pass
    def commit(self):
        pass
    def rollback(self):
        pass
    def get_db(self):
        pass
    def insert_db(self, query, args):
        pass
    def query_db(self, query, args=(), one=False):
        pass
    def close_db(self):
        pass
    def init_db(self):
        pass



class Connection(object):
    """Connection storage object"""
    def __init__(self, name, description="", speed_down=2000, speed_up=2000,
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


    def __str__(self):
        return ("name: {}  speed_down: {}  speed_up: {}  speed_var: {} "
                "latency_up: {} latency_down: {}  latency_jitter: {} "
                "loss_down: {} loss_up: {}  loss_jitter: {} ").format(
                self.name, self.speed_down, self.speed_up, self.speed_var,
                self.latency_up, self.latency_down, self.latency_jitter,
                self.loss_down, self.loss_up, self.loss_jitter)



class Subscriber(object):
    """Subscriber storage object"""
    def __init__(self, name, ipaddr="", calling_id = "000000000000000",
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
        self.conn_id = conn_id
        self.enabled = enabled


    def __str__(self):
        return ("name: {}  ipaddr: {} calling_id: {}  called_id: {}  imsi: {}"
                "imei: {} loc_info: {} conn_id: {} enabled: {}").format(self.name,
                        self.ipaddr, self.calling_id, self.called_id, self.imsi,
                        self.imei, self.loc_info, self.conn_id, self.enabled)



class Settings(object):
    """Settings storage object"""
    def __init__(self, rad_ip, rad_port, rad_user, rad_pass,
            rad_secret):
        self.rad_ip = rad_ip
        self.rad_port = rad_port
        self.rad_user = rad_user
        self.rad_pass = rad_pass
        self.rad_secret = rad_secret

    def __str__(self):
        return ("{}\nrad_ip: {}\nrad_port: {}\nrad_user: "
                "{}\nrad_pass, rad_secret: {}").format(self.rad_ip,
                        self.rad_port, self.rad_user, self.rad_pass,
                        self.rad_secret)



class Client(object):
    """Client storage object"""
    def __init__(self, subscriber, connection, client_id = -1):
        self.client_id = client_id
        self.subscriber = subscriber
        self.connection = connection


    def __str__(self):
        return ("subscriber: {}\nconnection: {}").format(
                self.subscriber, self.connection)



class DBConnectorSQLite(DBConnector):
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


    def query_db(self, query, args=(), one=False):
        """Queries the database and returns a list of dictionaries."""
        cur = self.get_db().execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv



class DB(object):
    def __init__(self, connector):
        self.connector = connector


    def init_schema(self, fname="schema.sql"):
        """load the database schema"""
        self.connector.init_db(fname)


    def set_connection(self, connection):
        """add a connection to the db"""
        return self.connector.execute_db("""INSERT INTO connection(name,
                description, speed_down, speed_up, speed_var, latency_up,
                latency_down, latency_jitter, loss_down, loss_up, loss_jitter)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [connection.name, connection.description, connection.speed_down,
                    connection.speed_up, connection.speed_var,
                    connection.latency_up, connection.latency_down,
                    connection.latency_jitter, connection.loss_down,
                    connection.loss_up, connection.loss_jitter])


    def get_connection_by_name(self, name):
        """get a connection by name"""
        res = self.connector.query_db("""SELECT name, description, speed_down,
                speed_up, speed_var, latency_up, latency_down, latency_jitter,
                loss_down, loss_up, loss_jitter, conn_id FROM connection WHERE
                name = ?""", [name], True)
        return Connection(*res) if res else None


    def get_connection_by_id(self, conn_id):
        """get a connection by _id"""
        res = self.connector.query_db("""SELECT name, description, speed_down,
                speed_up, speed_var, latency_up, latency_down, latency_jitter,
                loss_down, loss_up, loss_jitter, conn_id FROM connection WHERE
                conn_id = ?""", [conn_id], True)
        return Connection(*res) if res else None


    def get_all_connections(self):
        """get a list of all connections"""
        res_all = self.connector.query_db("""SELECT name, description,
                speed_down, speed_up, speed_var, latency_up, latency_down,
                latency_jitter, loss_down, loss_up, loss_jitter, conn_id FROM
                connection""", [], False)
        if len(res_all) > 0:
            return [Connection(*res) for res in res_all]
        return None


    def delete_connection(self, conn_id):
        """delete a connection by ID"""
        return self.connector.execute_db("""DELETE FROM connection WHERE
                conn_id=?""", [conn_id])


    def update_connection(self, connection):
        """update the connection in the database"""
        return self.connector.execute_db("""UPDATE connection SET name = ?,
                description = ?, speed_down = ?, speed_up = ?, speed_var = ?,
                latency_up = ?, latency_down = ?, latency_jitter = ?, loss_down
                = ?, loss_up = ?, loss_jitter = ? WHERE conn_id = ?""",
                [connection.name, connection.description, connection.speed_down,
                connection.speed_up, connection.speed_var,
                connection.latency_up, connection.latency_down,
                connection.latency_jitter, connection.loss_down,
                connection.loss_up, connection.loss_jitter,
                connection.conn_id])


    def set_subscriber(self, subscriber):
        """add a subscriber to a DB"""
        return self.connector.execute_db("""INSERT INTO subscriber(name, ipaddr,
                calling_id, called_id, imsi, imei, loc_info, conn_id, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", [subscriber.name,
                subscriber.ipaddr, subscriber.calling_id, subscriber.called_id,
                subscriber.imsi, subscriber.imei, subscriber.loc_info,
                subscriber.conn_id, subscriber.enabled])


    def get_subscriber_by_name(self, name):
        """get a subscriber by name"""
        res = self.connector.query_db("""SELECT name, ipaddr, calling_id,
                called_id, imsi, imei, loc_info, subs_id, conn_id, enabled FROM
                subscriber WHERE name = ?""", [name], True)
        return Subscriber(*res) if res else None


    def get_subscriber_by_id(self, subs_id):
        """get a subscriber by name"""
        res = self.connector.query_db("""SELECT name, ipaddr, calling_id,
                called_id, imsi, imei, loc_info, subs_id, conn_id, enabled FROM
                subscriber WHERE subs_id = ?""", [subs_id], True)
        return Subscriber(*res) if res else None


    def update_subscriber(self, subscriber):
        """update a subscriber"""
        return self.connector.execute_db("""UPDATE subscriber SET name = ?,
                ipaddr = ?, calling_id = ?, called_id = ?, imsi = ?, imei = ?,
                loc_info = ?, conn_id = ?, enabled = ? WHERE subs_id = ?""",
                [subscriber.name, subscriber.ipaddr, subscriber.calling_id,
                    subscriber.called_id, subscriber.imsi, subscriber.imei,
                    subscriber.loc_info, subscriber.conn_id, subscriber.enabled,
                    subscriber.subs_id])


    def get_all_subscribers(self):
        """get list of all subscribers"""
        res_all = self.connector.query_db("""SELECT name, ipaddr, calling_id,
                called_id, imsi, imei, loc_info, subs_id, conn_id, enabled FROM
                subscriber""", [], False)
        if len(res_all) > 0:
            return [Subscriber(*res) for res in res_all]
        return None


    def delete_subscriber(self, subs_id):
        """delete a subscriber by _id"""
        return self.connector.execute_db("""DELETE FROM subscriber WHERE subs_id
                = ?""", [subs_id])


    def get_settings(self):
        """populate the settings object from the DB"""
        res = self.connector.query_db("""SELECT rad_ip, rad_port, rad_user,
                rad_pass, rad_secret FROM settings""", [], True)
        return Settings(*res) if res else None


    def update_settings(self, settings):
        """update settings in the dataBase"""
        return self.connector.execute_db("""UPDATE settings SET rad_ip = ?,
                rad_port = ?, rad_user = ?, rad_pass = ?, rad_secret = ?""",
                [settings.rad_ip, settings.rad_port, settings.rad_user,
                    settings.rad_pass, settings.rad_secret])


# vim: set ts=4 sts=4 sw=4 tw=80 ai smarttab et list
