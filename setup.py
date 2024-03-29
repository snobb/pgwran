#!/usr/bin/env python
#
# { setup.py }
# Copyright (C) 2013 Alex Kozadaev [akozadaev at yahoo com]
#

import sys
import os
import glob
import distutils.sysconfig
import controller
from distutils.core import setup
import libradi


def create_config_file():
    with open("libradi/config.py", "w") as f:
        print >> f, "install_pfx = '{}'".format(
            distutils.sysconfig.PREFIX)


def delete_config_file():
    os.remove("libradi/config.py")


def main():
    create_config_file()
    setup(
        name=libradi.__name__,
        description=libradi.__doc__,
        author=libradi.__author__,
        author_email=libradi.__author_email__,
        license=("Alex Kozadaev <a.kozadaev at f5.com>\n\n"
                 "Copyright (c) 2013-2014, F5 Networks, Inc. All rights "
                 "reserved.\n\nNo part of this software may be reproduced or "
                 "transmitted in any\nform or by any means, electronic or "
                 "mechanical, for any purpose,\nwithout express written "
                 "permission of F5 Networks, Inc.\n"),
        version=controller.__version__,
        scripts=["radi.py", "controller.py"],
        py_modules=["libradi.dictionary", "libradi.radius",
                    "libradi.radtypes", "libradi.config", "netem",
                    "dao", "config", "sqlite_conn", "bottle"],
        data_files=[("share/pgwran/dict", glob.glob("dict/dictionary*")),
                    ("/share/pgwran/", "schema.sql"),
                    ("/share/pgwran/static", glob.glob("static/*"))]
    )
    delete_config_file()


if __name__ == "__main__":
    try:
        main()
    except IOError as e:
        print "ERROR: cannot access config.py"
        exit(1)

# vim: set ts=4 sts=4 sw=4 tw=80 ai smarttab et list
