"""
tests for dnstest_config.py

The latest version of this package is available at:
<https://github.com/jantman/pydnstest>

##################################################################################
Copyright 2013 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of pydnstest.

    pydnstest is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pydnstest is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
##################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/pydnstest> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
##################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

"""

import pytest
import sys
import os
import shutil
import os.path
import os

# conditional imports for packages with different names in python 2 and 3
if sys.version_info[0] == 3:
    import configparser as ConfigParser
    from configparser import ParsingError
else:
    import ConfigParser
    from ConfigParser import ParsingError

from pydnstest.config import DnstestConfig


class TestConfigMethods:
    """
    Class to test the configuration-related methods in dnstest_config
    """

    @pytest.fixture
    def save_user_config(self, request):
        """
        Rename any existing configuration files prior to testing
        """
        if os.path.exists("dnstest.ini"):
            shutil.move(os.path.abspath("dnstest.ini"), os.path.abspath("dnstest.ini.pretest"))
        if os.path.exists(os.path.expanduser("~/.dnstest.ini")):
            shutil.move(os.path.expanduser("~/.dnstest.ini"), os.path.expanduser("~/.dnstest.ini.pretest"))
        request.addfinalizer(self.restore_user_config)

    def restore_user_config(self):
        """
        Remove any config files generated by testing, and restore previous configs
        """
        # teardown
        if os.path.exists("dnstest.ini"):
            os.remove("dnstest.ini")
        if os.path.exists(os.path.expanduser("~/.dnstest.ini")):
            os.remove(os.path.expanduser("~/.dnstest.ini"))

        if os.path.exists("dnstest.ini.pretest"):
            shutil.move(os.path.abspath("dnstest.ini.pretest"), os.path.abspath("dnstest.ini"))
        if os.path.exists(os.path.expanduser("~/.dnstest.ini.pretest")):
            shutil.move(os.path.expanduser("~/.dnstest.ini.pretest"), os.path.expanduser("~/.dnstest.ini"))
        return True

    def test_find_no_config_file(self, save_user_config):
        dc = DnstestConfig()
        assert dc.find_config_file() == None

    def write_conf_file(self, path, contents):
        fh = open(path, 'w')
        fh.write(contents)
        fh.close()
        return

    def test_find_main_config_file(self, save_user_config):
        dc = DnstestConfig()
        fpath = os.path.abspath("dnstest.ini")
        self.write_conf_file(fpath, "test_find_main_config_file")
        assert dc.find_config_file() == fpath

    def test_find_dot_config_file(self, save_user_config):
        dc = DnstestConfig()
        fpath = os.path.expanduser("~/.dnstest.ini")
        self.write_conf_file(fpath, "test_find_dot_config_file")
        assert dc.find_config_file() == fpath

    def test_parse_example_config_file(self, save_user_config):
        dc = DnstestConfig()
        fpath = os.path.abspath("dnstest.ini.example")
        dc.load_config(fpath)
        assert dc.server_prod == '1.2.3.4'
        assert dc.server_test == '1.2.3.5'
        assert dc.default_domain == '.example.com'
        assert dc.have_reverse_dns == True
        assert dc.ignore_ttl == False
        assert dc.sleep == 0.0
        assert dc.asDict() == {'default_domain': '.example.com', 'have_reverse_dns': True,
                               'servers': {'prod': '1.2.3.4', 'test': '1.2.3.5'}, 'ignore_ttl': False, 'sleep': 0.0}

    def test_parse_bad_config_file(self, save_user_config):
        fpath = os.path.abspath("dnstest.ini")
        contents = """
[servers]
blarg

"""
        self.write_conf_file(fpath, contents)
        dc = DnstestConfig()
        with pytest.raises(ParsingError):
            dc.load_config(fpath)

    def test_parse_empty_config_file(self, save_user_config):
        dc = DnstestConfig()
        fpath = os.path.abspath("dnstest.ini")
        contents = ""
        self.write_conf_file(fpath, contents)
        dc.load_config(fpath)
        assert dc.server_prod == ''
        assert dc.server_test == ''
        assert dc.default_domain == ''
        assert dc.have_reverse_dns == True
        assert dc.ignore_ttl == False
        assert dc.sleep == 0.0
