#!/usr/bin/env python
#
# radi.py
# Author: Aleksei Kozadaev (2013)
#

import getopt, sys
import struct, socket
import pickle, hashlib

__version__ = "0.03"

# Radius-Request
#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |     Code      |  Identifier   |            Length             |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                                                               |
#   |                     Request Authenticator                     |
#   |                                                               |
#   |                                                               |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |  Attributes ...
#   +-+-+-+-+-+-+-+-+-+-+-+-+-

# Regular AVP
#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |     Type      |    Length     |             Value
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#              Value (cont)         |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# String VSA (normally encapsulated in a AVP)
#    0                   1                   2
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |     Type      |    Length     |  String ...
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# Radius accounting header templates
RADIUS_HDR_TMPL="!BBH16s"
RADIUS_AVP_TMPL="!BB%ss"

# actions
START, STOP = range(1, 3) # also ACCT_STATUS_TYPE start/stop

# Attributes
AVP_TYPE = {
    "User-Name" : 1,
    "NAS-IP-Address" : 4,
    "Framed-Protocol" : 7,
    "Framed-IP-Address" : 8,
    "Framed-IP-Netmask" : 9,
    "Vendor_Specific" : 26,
    "Called-Station-Id" : 30,
    "Calling-Station-Id" : 31,
    "Acct-Status-Type" : 40,
    "NAS-IPv6-Address" : 95,
    "Framed-IPv6-Prefix" : 97,

    # Vendor specific (26)
    "3GPP-IMSI" : 1,
    "3GPP-IMEISV" : 20,
    "3GPP-User-Location-Info" : 22
}

__verbose__ = False     # enabling verbose logging

# Constants
FRAMED_PROTO_PPP = 1
PICKLED_FILE_NAME = "./.%s.dat" % __file__

class Config(object):
    """config storage object"""
    def __init__(self):
        self.radius_dest = "127.0.0.1"
        self.radius_port = 1813
        self.radius_secret = "secret"
        self.username = "johndoe"
        self.imsi = "12345678901234"
        self.imei = "45678901234567"
        self.framed_ip ="10.0.0.1"
        self.framed_mask = 32
        self.calling_id = "00441234987654"
        self.called_id = "web.apn"
        self.subs_loc_info = struct.pack("!BBBBHH",
                1,      # Location Type (SAI (1))
                0x62,   # 2 octets MCC (Germany (262))
                0x02,   # 1 octet MCC / 1 MNC
                0x10,   # 2 octets MNC (T-Mobile (10))
                0xffff, # LAC
                0xffff) # CI
        self.delay = 1
        self.action = START


    def update(self, config):
        """merge the current object with 'config' dictionary"""
        self.__dict__.update(config)



class RadiusAvp(object):
    """Radius avp implementations"""
    def __init__(self, avp_type, avp_value, allow_child=True):
        self.vsa_child = None
        self.avp_type = AVP_TYPE[avp_type]
        if allow_child and avp_type.startswith("3GPP"):
            self.avp_type = 26                   # Vendor_Specific
            self.avp_value = IntegerType(10415)  # 3GPP
            self.vsa_child = RadiusAvp(avp_type, avp_value, False)
            self.avp_length = 6 + len(self.vsa_child)
        else:
            self.avp_value = avp_value
            self.avp_length = 2 + len(self.avp_value)


    def dump(self):
        """dump the binary representation of the AVP"""
        value = struct.pack(RADIUS_AVP_TMPL % len(self.avp_value),
                self.avp_type,
                len(self),
                self.avp_value.dump())
        if self.vsa_child:
            return "".join((value, self.vsa_child.dump()))
        return value


    def __len__(self):
        return self.avp_length


    def __str__(self):
        avp = "AVP: Type:{%d}  Length:{%d}  Value:{%s}\n" % (
                self.avp_type,
                len(self),
                str(self.avp_value))
        if self.vsa_child:
                return "".join((avp, "`- %s" % str(self.vsa_child)))
        return avp



class RadiusAcctRequest(object):
    """Radius accounting request object"""
    def __init__(self, secret):
        self.code = 4
        self.pid = 0xf5
        self.length = 20    # length so far
        self.secret = secret
        self.avp_list = []


    def add_avp(self, avp):
        """add an AVP class to the list of the packets AVPs"""
        if avp and isinstance(avp, RadiusAvp):
            self.avp_list.append(avp)
            self.length += len(avp)


    def get_all_avps_contents(self):
        """return binary contents of all AVPs in the requests"""
        return "".join([avp.dump() for avp in self.avp_list])


    def compute_authenticator(self, avps):
        """gets the avp binary contents as an argument and returns computed
        authenticator of the radius request"""
        if not avps:
            raise ValueError("AVPs contents isn't defined")
        header = struct.pack(RADIUS_HDR_TMPL,
                self.code,
                self.pid,
                len(self),
                bytes(IntegerType(0, length=4)))
        packet = "".join([header, avps, self.secret])
        return hashlib.md5(packet).digest()


    def dump(self):
        """dump binary version of the Radius Request packet payload
        including AVPs"""
        avps = self.get_all_avps_contents()
        auth = self.compute_authenticator(avps)
        header = struct.pack(RADIUS_HDR_TMPL,
                self.code,
                self.pid,
                len(self),
                auth)
        return "".join([header, avps])


    def __len__(self):
        return self.length


    def __str__(self):
        auth = self.compute_authenticator(self.get_all_avps_contents())
        header = "HEADER:  Code:{%d}  PID{%d}  Length:{%d}  Auth{%s}\n" % (
                self.code, self.pid, len(self), auth.encode("hex"))
        avps = "".join([str(avp) for avp in self.avp_list])
        return "".join((header, avps))



class AddressType(object):
    """IP ip_string data type"""
    def __init__(self, ip_string, is_ipv6=False):
        if type(ip_string) != str:
            raise ValueError("String expected")

        self.family = socket.AF_INET6 if is_ipv6 else socket.AF_INET
        self.ip_string = ip_string

        try:
            self.bin_ip_string = socket.inet_pton(self.family, ip_string)
        except socket.error:
            raise ValueError("Invalid IP ip_string")


    def __str__(self):
        return self.ip_string


    def __len__(self):
        return len(self.bin_ip_string)


    def dump(self):
        return bytes(self.bin_ip_string)



class TextType(object):
    """Text data type"""
    def __init__(self, value):
        if not value:
            raise ValueError("Empty strings are not allowed (rfc2866)")
        if type(value) != str:
            raise ValueError("String expected")
        self.value = value


    def __len__(self):
        return len(self.value)


    def __str__(self):
        return str(self.value)


    def dump(self):
        return struct.pack("!%ss" % len(self.value), self.value)



class IntegerType(object):
    """Integer data type"""
    def __init__(self, value, length=1):
        """length is set in 4byte chunks. eg. length = 4 == 16bytes"""
        if type(value) != int:
            raise ValueError("Integer expected")
        self.value = value
        self.length = length


    def __len__(self):
        return self.length * 4


    def __str__(self):
        return str(self.value)


    def dump(self):
        values = [self.value >> (n*32) & 0xffffffff
                for n in range(self.length-1, -1, -1)]
        return struct.pack("!%dL" % len(values), *values)



class ByteType(object):
    """Byte data type"""
    def __init__(self, value):
        if type(value) != int:
            raise ValueError("Integer expected")
        if value < 0 or value > 0xff:
            raise ValueError("byte - type overflow")
        self.value = value


    def __len__(self):
        return 1


    def __str__(self):
        return str(self.value)


    def dump(self):
        """dump binary value"""
        return struct.pack("!B", self.value)



class ContainerType(object):
    """Container type allowing to join several values together"""
    def __init__(self, *args):
        self.values = args


    def __len__(self):
        return sum([len(value) for value in self.values])


    def __str__(self):
        return "".join([str(value) for value in self.values])


    def dump(self):
        """dump binary representation of the contained values"""
        values_binary = "".join([value.dump() for value in self.values])
        return bytes(values_binary)


def is_ipv6(address):
    """returns true if the IP is IPv6"""
    return (":" in address)


def create_packet(config):
    """generate a binary version of the packet based on the current config"""
    rad = RadiusAcctRequest(config.radius_secret)
    rad.add_avp(RadiusAvp("User-Name", TextType(config.username)))
    rad.add_avp(RadiusAvp("Acct-Status-Type", IntegerType(config.action)))

    if is_ipv6(config.radius_dest):
        rad.add_avp(RadiusAvp("NAS-IPv6-Address",
            AddressType(config.radius_dest, True)))
    else:
        rad.add_avp(RadiusAvp("NAS-IP-Address",
            AddressType(config.radius_dest)))

    if is_ipv6(config.framed_ip):
        rad.add_avp(RadiusAvp("Framed-IPv6-Prefix",
            ContainerType(
                ByteType(0),
                ByteType(config.framed_mask),
                AddressType(config.framed_ip, True))))
    else:
        rad.add_avp(RadiusAvp("Framed-IP-Address",
            AddressType(config.framed_ip)))
        rad.add_avp(RadiusAvp("Framed-IP-Netmask",
            AddressType(bits_to_ip4mask(config.framed_mask))))

    rad.add_avp(RadiusAvp("Framed-Protocol", IntegerType(FRAMED_PROTO_PPP)))
    rad.add_avp(RadiusAvp("Calling-Station-Id", TextType(config.calling_id)))
    rad.add_avp(RadiusAvp("Called-Station-Id", TextType(config.called_id)))

    rad.add_avp(RadiusAvp("3GPP-User-Location-Info",
        TextType(config.subs_loc_info)))

    rad.add_avp(RadiusAvp("3GPP-IMSI", TextType(config.imsi)))
    rad.add_avp(RadiusAvp("3GPP-IMEISV", TextType(config.imei)))

    debug(str(rad))

    return bytes(rad.dump())


def bits_to_ip4mask(num_bits):
    """convert integer number of bits in ipv4 netmask to string representation
    of the mask. Eg. '255.255.255.0'"""
    if 0 <= num_bits <= 32:
        bits = 0xffffffff ^ ((1 << (32 - num_bits)) - 1)
        ip4_bytes = [str((bits >> 8*n) & 0xff) for n in range(3, -1, -1)]
        return ".".join(ip4_bytes)
    else:
        raise ValueError("invalid IPv4 mask specified")


def send_packet(destTuple, packet):
    """send the packet to the network"""
    if is_ipv6(destTuple[0]):
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IP_MULTICAST_TTL, 20)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20)
    sock.sendto(packet, destTuple)
    sock.close()


def start_stop_session(config):
    """send start/stop session based on action in the config"""
    send_packet((config.radius_dest, config.radius_port), create_packet(config))


def debug(message, force=False):
    """debug output - printed only if the verbose config option is set"""
    global __verbose__
    if __verbose__ or force:
        print message

# vim: set ts=4 sts=4 sw=4 tw=80 ai smarttab et list
