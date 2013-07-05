#!/usr/bin/env python
"""
Script to facilitate confirmation of DNS changes on a staging DNS server, comparing to prod.

Requirements:
- pydns from <http://pydns.sourceforge.net/>

See example_dns_test.py for usage - this should be called as a module from that script.

By Jason Antman <jason@jasonantman.com>

ToDo: flag to confirm against prod once live

"""

import DNS
import dnstest_checks


config = {}


def do_dns_tests(tests, test_server, prod_server, default_domain, have_reverse=True):
    """
    Run all DNS tests

    param tests: dict with keys 'added',
    """

    if 'added' in tests:
        check_added_names(tests['added'], test_server, prod_server, default_domain, have_reverse)
    if 'removed' in tests:
        check_removed_names(tests['removed'], test_server, prod_server, default_domain, have_reverse)
    if 'changed' in tests:
        check_changed_names(tests['changed'], test_server, prod_server, default_domain, have_reverse)
    return
