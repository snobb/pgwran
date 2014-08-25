#!/usr/bin/env python
#
# netem.py
# Author: Alex Kozadaev (2014)
#

import dao
import os

phys_in_iface = None
in_iface = "ifb0"
out_iface = None
class_registry = {}

def commit(commands):
    os.system(";".join(commands))

def load_ingress_prerequisites():
    """make sure the kernel modules and interfaces are ready"""
    cmd = []
    cmd.append("modprobe ifb")
    cmd.append("ip link set ifb0 up")

    return cmd

def create_ingress_egress():
    """initialize the ingress queues"""
    cmd = []
    # egress
    cmd.append("tc qdisc add dev {} handle 1: root " \
            "htb".format(out_iface))

    # ingress
    cmd.append("tc qdisc add dev {} ingress".format(phys_in_iface))
    cmd.append("tc filter add dev {} parent ffff: protocol ip prio " \
            "50 u32 match u32 0 0 action mirred egress redirect " \
            "dev ifb0".format(phys_in_iface))
    cmd.append("tc qdisc add dev ifb0 handle 1: root htb")
    return cmd

def clear_filters():
    """remove all filters"""
    cmd = []
    for iface in [in_iface, out_iface]:
        cmd.append("tc filter del dev {} pref 3".format(iface))
    return cmd

def clear_all():
    """clear all the queues"""
    cmd = []
    cmd.append("tc qdisc del dev {} root".format(out_iface))
    cmd.append("tc qdisc del dev {} ingress".format(phys_in_iface))
    cmd.append("tc qdisc del dev {} root".format(in_iface))
    return cmd

def netem_make_command(iface, classid, handle, delay=0, jitter=0,
        delay_corr=0, distribution="", loss=0, loss_corr=0, bandwidth=0):
    """generate a set of netem commands based on the given parameters"""
    delay_cmd = ""
    if delay > 0:
        buf = ["delay {}ms".format(delay)]
        if jitter > 0 or delay_corr > 0:
            buf.append("{}ms".format(str(jitter)))
        if delay_corr > 0:
            buf.append("{}%".format(str(delay_corr)))
        if distribution in ("normal", "pareto", "paretonormal"):
            buf.append("distribution {}".format(distribution))
        delay_cmd = " ".join(buf)

    loss_cmd = ""
    if loss > 0:
        buf = ["loss {}%".format(float(loss))]
        if loss_corr > 0:
            buf.append("{}%".format(float(loss_corr)))
        loss_cmd = " ".join(buf)

    bandwidth_cmd = ""
    if bandwidth > 0:
        bandwidth_cmd = "rate {bandwidth}kbit ceil {bandwidth}kbit " \
                        "burst 0 cburst 0".format(bandwidth=bandwidth)

    prefix = "tc qdisc add dev {iface}".format(iface=iface)

    cmd = []
    if bandwidth_cmd != "":
        cmd.append("tc class add dev {iface} parent 1:1 classid 1:{classid} " \
                "htb {bandwidth_cmd}".format(iface=iface, classid=classid,
                    bandwidth_cmd=bandwidth_cmd))
    if (delay_cmd != "" or loss_cmd != ""):
        cmd.append("{prefix} parent 1:{parent} handle {handle}: " \
                "netem {loss_cmd} {delay_cmd}".format(prefix=prefix,
                    parent=classid, handle=handle, loss_cmd=loss_cmd,
                    delay_cmd=delay_cmd))

    return cmd

def setup_connections(connections):
    """create a connection class for every connection in the connections
    (egress and egress)
    Also register the connid->classid mapping"""
    egress_classid = 10
    ingress_classid = 10
    egress_handle = 10
    ingress_handle = 10

    cmd = create_ingress_egress()

    for conn in connections:
        egress_cmd = netem_make_command(out_iface,
                egress_classid, egress_handle, delay=conn.latency_up,
                jitter=conn.latency_jitter, loss=conn.loss_up,
                loss_corr=conn.loss_jitter, bandwidth=conn.speed_up)
        ingress_cmd = netem_make_command(in_iface,
                ingress_classid, ingress_handle, delay=conn.latency_down,
                jitter=conn.latency_jitter, loss=conn.loss_down,
                loss_corr=conn.loss_jitter, bandwidth=conn.speed_down)

        cmd.extend(egress_cmd)
        cmd.extend(ingress_cmd)

        class_registry[conn.conn_id] = {
                "egress_classid": egress_classid,
                "ingress_classid": ingress_classid,
                "egress_handle": egress_handle,
                "ingress_handle": ingress_handle,
                }
        egress_classid += 1
        ingress_classid += 1
        egress_handle += 10
        ingress_handle += 10

    return cmd

def add_filter(connid, src_ip):
    cmd = []
    if connid in class_registry:
        egress_classid = class_registry[connid]["egress_classid"]
        ingress_classid = class_registry[connid]["ingress_classid"]

        # egress filter
        cmd.append("tc filter add dev {iface} protocol ip parent 1: " \
                "prio 3 u32 match ip src {src_ip} flowid " \
                "1:{classid}".format(iface=out_iface, src_ip=src_ip,
                    classid=egress_classid))
        # ingress filter
        cmd.append("tc filter add dev {iface} protocol ip parent 1: " \
                "prio 3 u32 match ip dst {src_ip} flowid " \
                "1:{classid}".format(iface=in_iface, src_ip=src_ip,
                    classid=ingress_classid))

    return cmd

def initialize(connections, outif, inif):
    cmd = []
    global phys_in_iface, out_iface
    phys_in_iface, out_iface = inif, outif
    cmd.extend(load_ingress_prerequisites())
    cmd.extend(setup_connections(connections))

    return cmd

# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
