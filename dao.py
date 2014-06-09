#!/usr/bin/env python
#
# dao.py
# Author: Alex Kozadaev (2014)
#

import sqlite3
import sqlite_connector as connector


def initialize(db_name, db_schema):
    """initialize connector wrapper"""
    connector.initialize(db_name, db_schema)



class Transaction(object):
    """Transaction Decorator class"""
    def __init__(self):
        """constructor for the transaction"""
        pass


    def __call__(self, func):
        """wrap the function and do the transaction handling"""
        def wrapped(*args, **kwargs):
            success, status, data = True, "", None
            try:
                connector.begin_transaction()
                data = func(*args, **kwargs)
                connector.commit()
            except Exception as e:
                success = False
                status = e.message
                connector.rollback()
            return (success, status, data)
        return wrapped



class GenericDaoImpl(object):
    @Transaction()
    def get_all(self, table=None):
        """get all objects"""
        cls = self.__obj_class__
        child = cls()
        obj_list = connector.query_db(
                child.get_select_query(table=table), [])
        if len(obj_list):
            return [cls(**(dict(zip(child.get_keys(), obj)))) for obj in obj_list]
        return None


    @Transaction()
    def get(self, obj_id):
        """get the objects with id - obj_id"""
        cls = self.__obj_class__
        child = cls()
        obj = connector.query_db(
                child.get_select_query(True), [obj_id], True)
        if obj:
            return cls(**(dict(zip(child.get_keys(), obj))))
        return None


    @Transaction()
    def save(self, obj):
        """save the object. If the object's ID -1 insert else update."""
        obj_id = getattr(obj, obj.get_id_name())
        if obj_id == -1:    # Insert
            new_obj_id = connector.execute_db(
                    obj.get_insert_query(),
                    obj.get_values(has_id=False))
        else:               # Update
            new_obj_id = connector.execute_db(
                    obj.get_update_query(),
                    obj.get_values(has_id=False) + [obj_id])
        return new_obj_id


    @Transaction()
    def delete(self, obj_id):
        """delete the object"""
        obj = self.__obj_class__()
        connector.execute_db(
                obj.get_delete_query(),
                [obj_id])



class GenericDaoObject(object):
    __table__   = "GenericTable"
    __id_name__ = None

    def get_dict(self):
        fields = self.__dict__
        return {k:v for k, v in fields.items() if
                not k.startswith("__")}


    def get_keys(self, has_id=True):
        """get list of field names of the object"""
        fields = self.get_dict()
        if not has_id:
            fields.pop(self.get_id_name())
        return ([name for name in fields.keys() if
                not name.startswith("__")])


    def get_values(self, has_id=True):
        """get the values of the object fields in the same order as in
        get_keys()"""
        fields = self.get_dict()
        if not has_id:
            fields.pop(self.get_id_name())
        return ([getattr(self, name) for name in fields.keys() if
                not name.startswith("__")])


    def get_insert_query(self):
        """get the object related INSERT query"""
        keys = self.get_keys(has_id=False)
        return "INSERT INTO {}({}) VALUES ({})".format(
                self.get_table_name(),
                ",".join(keys),
                ",".join(["?"] * len(keys))
                )


    def get_update_query(self):
        """get the object related UPDATE query"""
        return "UPDATE {} SET {}=? WHERE {}=?".format(
                self.get_table_name(),
                "=?,".join(self.get_keys(has_id=False)),
                self.get_id_name())


    def get_select_query(self, filtered=False, table=None):
        """get the object related SELECT query"""
        query_filter = ""
        if not table:
            table = self.get_table_name()
        if filtered:
            query_filter = "WHERE {}=?".format(self.get_id_name())
        return "SELECT {} FROM {} {}".format(
                ",".join(self.get_keys()), table, query_filter)


    def get_delete_query(self):
        """get the object related DELETE query"""
        return "DELETE FROM {} WHERE {}=?".format(
                self.get_table_name(),
                self.get_id_name())


    def get_table_name(self):
        """get table name"""
        return self.__class__.__table__


    def get_id_name(self):
        """get id name"""
        return self.__class__.__id_name__


    def __str__(self):
        """string representation of the class"""
        str_list = []
        for k, v in zip(self.get_keys(), self.get_values()):
            str_list.append("{}: {}".format(k, v))
        return ", ".join(str_list)



class Subscriber(GenericDaoObject):
    """Subscriber storage object"""
    __table__   = "subscriber"
    __id_name__ = "subs_id"

    def __init__(self, subs_id=-1, conn_id=0, enabled=0, name=None):
        self.subs_id = subs_id
        self.conn_id = conn_id
        self.enabled = enabled
        self.name = name


    def get_dict(self):
        return {"subs_id": self.subs_id,
                "conn_id": self.conn_id,
                "enabled": self.enabled,
                "name": self.name}


    def get_update_query(self):
        fields = self.get_keys()
        fields.remove("name")
        return "UPDATE {} SET {}=? WHERE {}=?".format(
                self.get_table_name(),
                "=?,".join(fields),
                self.get_id_name())



class SubscriberProfile(GenericDaoObject):
    """Subscriber profile storage object"""
    __table__   = "subs_profile"
    __id_name__ = "subs_id"

    def __init__(self, name="New", ipaddr="", calling_id = "000000000000000",
            called_id = "web.apn", imsi = "90000000000000",
            imei = "012345678901234", loc_info = "f5f5", subs_id=-1):
        self.subs_id = subs_id
        self.name = name
        self.ipaddr = ipaddr
        self.calling_id = calling_id
        self.called_id = called_id
        self.imsi = imsi
        self.imei = imei
        self.loc_info = loc_info



class ConnectionProfile(GenericDaoObject):
    """Connection Profile storage object"""
    __table__   = "conn_profile"
    __id_name__ = "conn_id"

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



class Settings(GenericDaoObject):
    """Settings storage object"""
    __table__   = "settings"
    __id_name__ = None

    def __init__(self, rad_ip="", rad_port=1813, rad_user="", rad_pass="",
            rad_secret=""):
        self.rad_ip = rad_ip
        self.rad_port = rad_port
        self.rad_user = rad_user
        self.rad_pass = rad_pass
        self.rad_secret = rad_secret


    def get_update_query(self):
        """get the object related UPDATE query"""
        return "UPDATE {} SET {}=?".format(
                self.__table__,
                "=?,".join(self.get_keys()))



class SubscriberDao(GenericDaoImpl):
    __obj_class__ = Subscriber

    def get_all(self):
        return super(SubscriberDao, self).get_all(table="subscriber_view")


    @Transaction()
    def save(self, obj):
        """save the object. If the object's ID -1 insert else update."""
        obj_id = getattr(obj, obj.get_id_name())
        fields = obj.get_dict()
        fields.pop("name")
        fields.pop("subs_id")
        query = "UPDATE {} SET {}=? WHERE {}=?".format(
                obj.get_table_name(),
                "=?,".join(fields),
                obj.get_id_name())
        return connector.execute_db(query, fields.values() + [obj_id])



class ConnectionProfileDao(GenericDaoImpl):
    __obj_class__ = ConnectionProfile



class SubscriberProfileDao(GenericDaoImpl):
    __obj_class__ = SubscriberProfile

    @Transaction()
    def save(self, obj):
        obj_id = getattr(obj, obj.get_id_name())
        items = obj.get_dict()
        if obj_id == -1:    # Insert
            new_obj_id = connector.execute_db(
                    obj.get_insert_query(),
                    obj.get_values(has_id=False))

            # adding subscriber as well
            subscriber = Subscriber(subs_id=new_obj_id)
            res = SubscriberDao().save(subscriber)
            return new_obj_id
        else:               # Update
            new_obj_id = connector.execute_db(
                    obj.get_update_query(),
                    obj.get_values(has_id=False) + [obj_id])
        return new_obj_id



class SettingsDao(GenericDaoImpl):
    __obj_class__ = Settings

    @Transaction()
    def get_all(self):
        """get_all: return the only available row"""
        cls = self.__obj_class__
        child = cls()
        obj = connector.query_db(
                child.get_select_query(), [], True)
        if obj:
            return cls(**(dict(zip(child.get_keys(), obj))))


    def get(self, obj_id=None):
        """get: this action does not make sense for this object"""
        return self.get_all()


    @Transaction()
    def save(self, obj):
        """save the object"""
        connector.execute_db(obj.get_update_query(), obj.get_values())


    def delete(self, obj):
        """delete: this action does not make sense for this object"""
        raise NotImplementedError("not applicable for this object")


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
