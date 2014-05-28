#!/usr/bin/env python
#
# __init__.py
# Author: Alex Kozadaev (2013)
#

import sys
import unittest

sys.path.append("..")

if __name__ == '__main__':
    unittest.main()

for all_test_suite in unittest.defaultTestLoader.discover('.', pattern='*_tests.py'):
    for test_suite in all_test_suite:
        unittest.TextTestRunner().run(test_suite)

# vim: set ts=4 sts=4 sw=4 tw=80 ai smarttab et list
