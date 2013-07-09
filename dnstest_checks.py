"""
Logic for checking desired DNS configuration against actual configuration
on prod and test servers.
"""

from dnstest_dns import DNStestDNS


class DNStestChecks:
    """
    Methods for checking actual DNS against the desired state.

    Each method returns a dict with the following keys:
    - result: Boolean, True if the test is considered a success, False otherwise
    - message: String, the overall status message, human-readable text
    - secondary: list of strings, describing sub-test steps
    - warnings: list of strings, of any non-critical warnings generated
    {'result': None, 'message': None, 'secondary': [], 'warnings': []}
    """


    config = None
    DNS = None


    def __init__(self, config):
        """
        init
        """
        self.config = config
        self.DNS = DNStestDNS()

    def check_removed_name(self, n):
        """
        Run tests for removed names
        """
        res = {'result': None, 'message': None, 'secondary': [], 'warnings': []}
        name = n
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + self.config.default_domain

        # resolve with both test and prod
        qt = self.DNS.resolve_name(name, self.config.server_test)
        qp = self.DNS.resolve_name(name, self.config.server_prod)
        if 'status' in qp:
            res['result'] = False
            res['message'] = "%s got status %s from PROD - cannot remove a name that doesn't exist (PROD)" % (n, qp['status'])
            return res
        # else we got an answer, it's there, just look for removal

        if 'status' in qt and qt['status'] == "NXDOMAIN":
            res['result'] = True
            res['message'] =  "%s removed, got status NXDOMAIN (TEST)" % (n)
            res['secondary'].append("PROD value was %s (PROD)" % qp['answer']['data'])
            # check for any leftover reverse lookups
            rev = self.DNS.lookup_reverse(qp['answer']['data'], self.config.server_test)
            if 'answer' in rev:
                res['warnings'].append("%s appears to still have reverse DNS set to %s (TEST)" % (n, rev['answer']['data']))
        elif 'status' in qt:
            res['result'] = False
            res['message'] = "%s returned status %s (TEST)" % (n, qt['status'])
        else:
            res['result'] = False
            res['message'] = "%s returned valid answer, not removed (TEST)" % n
        return res


    def check_renamed_name(self, n, newn):
        """
        Run tests for renamed names (same value, record name changes)
        """
        res = {'result': None, 'message': None, 'secondary': [], 'warnings': []}
        name = n
        newname = newn
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + self.config.default_domain
        if newname.find('.') == -1:
            newname = newname + self.config.default_domain

        # resolve with both test and prod
        qt = self.DNS.resolve_name(newname, self.config.server_test)
        qp = self.DNS.resolve_name(name, self.config.server_prod)
        if 'status' in qp:
            res['result'] = False
            res['message'] =  "%s got status %s from PROD - cannot change a name that doesn't exist (PROD)" % (n, qp['status'])
            return res
        # else we got an answer, it's there, check that it's right

        if 'status' in qt:
            res['result'] = False
            res['message'] = "%s got status %s (TEST)" % (newn, qt['status'])
            return res

        # got valid answers for both, check them
        if qt['answer']['data'] != qp['answer']['data']:
            res['result'] = False
            res['message'] = "%s => %s rename is bad, resolves to %s in TEST and %s in PROD" % (n, newn, qt['answer']['data'], qp['answer']['data'])
        else:
            # data matches, looks good
            res['result'] = True
            res['message'] =  "rename %s => %s (TEST)" % (n, newn)
            # check for any leftover reverse lookups
            if qt['answer']['typename'] == 'A' or qp['answer']['typename'] == 'A':
                rev = self.DNS.lookup_reverse(qt['answer']['data'], self.config.server_test)
                if 'answer' in rev:
                    if rev['answer']['data'] == newn or rev['answer']['data'] == newname:
                        res['secondary'].append("reverse DNS is set correctly for %s (TEST)" % qt['answer']['data'])
                    else:
                        res['warnings'].append("%s appears to still have reverse DNS set to %s (TEST)" % (n, rev['answer']['data']))
                else:
                    res['warnings'].append("no reverse DNS appears to be set for %s (TEST)" % qt['answer']['data'])
        return res


    def check_added_name(self, n, value):
        """
        Run tests for added names
        """
        res = {'result': None, 'message': None, 'secondary': [], 'warnings': []}
        name = n
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + self.config.default_domain

        target = value
        if target.find('.') == -1:
            target = target + self.config.default_domain

        # resolve with both test and prod
        qt = self.DNS.resolve_name(name, self.config.server_test)
        qp = self.DNS.resolve_name(name, self.config.server_prod)
        # make sure PROD returns NXDOMAIN, since it's a new record
        if 'status' in qp:
            if qp['status'] != 'NXDOMAIN':
                res['result'] = False
                res['message'] =  "prod server returned status %s for name %s (PROD)" % (qp['status'], n)
                return res
        else:
            res['result'] = False
            res['message'] =  "new name %s returned valid result from prod server (PROD)" % n
            return res

        # check the answer we got back from TEST
        if 'answer' in qt:
            if qt['answer']['data'] == value or qt['answer']['data'] == target:
                res['result'] = True
                res['message'] = "%s => %s (TEST)" % (n, value)
                res['secondary'].append("PROD server returns NXDOMAIN for %s (PROD)" % n)
            else:
                res['result'] = False
                res['message'] = "%s resolves to %s instead of %s (TEST)" % (n, qt['answer']['data'], value)
                res['secondary'].append("PROD server returns NXDOMAIN for %s (PROD)" % n)
            # check reverse DNS if we say to
            if self.config.have_reverse_dns and qt['answer']['typename'] == 'A':
                rev = self.DNS.lookup_reverse(value, self.config.server_test)
                if 'status' in rev:
                    res['warnings'].append("REVERSE NG: got status %s for name %s (TEST)" % (rev['status'], value))
                elif rev['answer']['data'] == n or rev['answer']['data'] == name:
                    res['secondary'].append("REVERSE OK: %s => %s (TEST)" % (value, rev['answer']['data']))
                else:
                    res['warnings'].append("REVERSE NG: got answer %s for name %s (TEST)" % (rev['answer']['data'], value))
        else:
            res['result'] = False
            res['message'] = "status %s for name %s (TEST)" % (qt['status'], n)
        return res
