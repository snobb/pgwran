#!/usr/bin/env python
#
# config.py
# Author: Alex Kozadaev (2014)
#

# == configuration ============================================================
listen_address  = "0.0.0.0"
listen_port     = 8088

database        = "database.db"
db_schema       = "schema.sql"
egress_iface    = "eth2"
ingress_iface   = "eth1"

debug           = True
reloader        = True

# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
