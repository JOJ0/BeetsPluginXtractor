#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/12/20, 11:42 PM
#  License: See LICENSE.txt

import os

from beets.library import Item
from beets.util import displayable_path

from beetsplug.xtractor import about
from beetsplug.xtractor.command import XtractorCommand

from test.helper import TestHelper, Assertions, \
    PLUGIN_NAME, PLUGIN_SHORT_DESCRIPTION, \
    PACKAGE_NAME, PACKAGE_TITLE, PLUGIN_VERSION, \
    capture_log

plg_log_ns = 'beets.{}'.format(PLUGIN_NAME)


def _normalize_test_path(path):
    return os.path.normpath(displayable_path(path).removeprefix('\\\\?\\'))


class CompletionTest(TestHelper, Assertions):
    """Test invocation of the plugin and basic package health.
    """

    def test_about_descriptor_file(self):
        self.assertTrue(hasattr(about, "__author__"))
        self.assertTrue(hasattr(about, "__email__"))
        self.assertTrue(hasattr(about, "__copyright__"))
        self.assertTrue(hasattr(about, "__license__"))
        self.assertTrue(hasattr(about, "__version__"))
        self.assertTrue(hasattr(about, "__status__"))
        self.assertTrue(hasattr(about, "__PACKAGE_TITLE__"))
        self.assertTrue(hasattr(about, "__PACKAGE_NAME__"))
        self.assertTrue(hasattr(about, "__PACKAGE_DESCRIPTION__"))
        self.assertTrue(hasattr(about, "__PACKAGE_URL__"))
        self.assertTrue(hasattr(about, "__PLUGIN_NAME__"))
        self.assertTrue(hasattr(about, "__PLUGIN_ALIAS__"))
        self.assertTrue(hasattr(about, "__PLUGIN_SHORT_DESCRIPTION__"))

    def test_application(self):
        output = self.runcli()
        self.assertIn(PLUGIN_NAME, output)
        self.assertIn(PLUGIN_SHORT_DESCRIPTION, output)

    def test_application_plugin_list(self):
        output = self.runcli("version")
        self.assertIn("plugins: {0}".format(PLUGIN_NAME), output)

    def test_run_plugin(self):
        with capture_log(plg_log_ns) as logs:
            self.runcli(PLUGIN_NAME)
        self.assertIn("xtractor: No items to process", "\n".join(logs))

    def test_plugin_version(self):
        with capture_log(plg_log_ns) as logs:
            self.runcli(PLUGIN_NAME, "--version")

        versioninfo = "{pt}({pn}) plugin for Beets: v{ver}".format(
            pt=PACKAGE_TITLE,
            pn=PACKAGE_NAME,
            ver=PLUGIN_VERSION
        )
        self.assertIn(versioninfo, "\n".join(logs))

    def test_get_input_path_for_item_with_absolute_path(self):
        path = self.lib_path(b"absolute.flac")
        with open(path, "wb"):
            pass

        item = Item(path=path)
        cmd = XtractorCommand(self.config[PLUGIN_NAME])
        cmd.lib = self.lib

        self.assertEqual(os.path.normpath(path.decode()), _normalize_test_path(cmd._get_input_path_for_item(item)))

    def test_get_input_path_for_item_with_relative_path(self):
        relative_path = b"nested/relative.flac"
        absolute_path = self.lib_path(relative_path)
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
        with open(absolute_path, "wb"):
            pass

        item = Item(path=relative_path)
        cmd = XtractorCommand(self.config[PLUGIN_NAME])
        cmd.lib = self.lib

        self.assertEqual(os.path.normpath(absolute_path.decode()), _normalize_test_path(cmd._get_input_path_for_item(item)))
