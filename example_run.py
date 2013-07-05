#!/usr/bin/env python
"""
Sample configuration/run script for dns_test.py
"""

import os.path
import platform
from dnstest import do_dns_tests

tests = {}

# new records that were added - A or CNAME
tests['added'] = {}
tests['added']['newhostname'] = '1.2.3.4'
tests['added']['newcname'] = 'newhostname'

# one A or CNAME added, another removed, with the same value
tests['changed'] = {}
tests['changed']['oldname'] = 'newname'

# records that were removed - A or CNAME
tests['removed'] = []
tests['removed'] = ['removedname1', 'removedname2']

print "# output generated by dns_test.py running with config file %s on %s" % (os.path.abspath(__file__), platform.node())

do_dns_tests(tests, SERVER_TEST, SERVER_PROD, DEFAULT_DOMAIN, HAVE_REVERSE_DNS)
