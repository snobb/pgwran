#!/usr/bin/env python
#
# logger.py
# Author: Alex Kozadaev (2014)
#

import sys
import time

class Logger(object):
    def __init__(self, logger=sys.stdout):
        self.logger = logger
        pass

    def log(self, msg):
        print >>self.logger, "{} {}: {}".format(
                time.strftime("%y/%m/%d %H:%M:%S", time.localtime()),
                sys.argv[0],
                msg)

    def __call__(self, func):
        def wrapped(*args, **kwargs):
            if len(kwargs):
                kwargs_list = ["{}={}".format(k,v) for n in iter(kwargs)]
                self.log("start function {}: {}".format(func.__name__,
                    ", ".join(args), ", ".join(kwargs_list)))
            ret = func(*args, **kwargs)
            self.log("exit function {}: {}".format(func.__name__, ret))
        return wrapped


# vim: ts=4 sts=4 sw=4 tw=80 ai smarttab et fo=rtcq list
