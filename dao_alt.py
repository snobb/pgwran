#!/usr/bin/env python
#
# dao.py
# Author: Alex Kozadaev (2014)
#

class GenericDaoObject(object):
    def get_keys(self):
        return ([name for name in self.__dict__.keys() if
                not name.startswith("__")])

    def get_values(self):
        return ([getattr(self, name) for name in self.__dict__.keys() if
                not name.startswith("__")])

    def __str__(self):


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


class ConnectionProfileDAO(object):
    pass


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
