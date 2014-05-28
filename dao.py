#!/usr/bin/env python
#
# dao.py
# Author: Alex Kozadaev (2014)
#


class GenericDaoObject(object):

    def get_dict(self):
        return self.__dict__

    def get_fields(self):
        return self.get_dict().keys()


class Connection(GenericDaoObject):
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


class Subscriber(GenericDaoObject):
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
        self.enabled = enabled


    def __str__(self):
        return ("name: {}  ipaddr: {} calling_id: {}  called_id: {}  imsi: {}"
                "imei: {} loc_info: {}").format(self.name, self.ipaddr,
                        self.calling_id, self.called_id, self.imsi, self.imei,
                        self.loc_info))


class Settings(GenericDaoObject):
    """Settings storage object"""
    def __init__(self, rad_ip, rad_port, rad_user, rad_pass,
            rad_secret):
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


class Dao(object):
    def __init__(self, connector):
        self.connector = connector


    def init_schema(self, fname="schema.sql"):
        """load the database schema"""
        self.connector.init_db(fname)


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
