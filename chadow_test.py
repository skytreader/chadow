import chadow
import json
import os
import unittest
import unittest.mock

from click.testing import CliRunner

DEFAULT_CONFIG = {
    "version": "0.1.0",
    "libraryMapping": {}
}

DEFAULT_CONFIG_MOCK_VALUE = json.dumps(DEFAULT_CONFIG)

class ChadowTests(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.full_config_path = os.path.join(chadow.APP_ROOT, chadow.CONFIG_NAME)

    def test_createlib(self):
        mo = unittest.mock.mock_open(read_data=DEFAULT_CONFIG_MOCK_VALUE)
        with unittest.mock.patch("chadow.open", mo) as mopen:
            self.runner.invoke(chadow.createlib, ["testlib"])
            mopen.assert_any_call(self.full_config_path, "r")
            mopen.assert_any_call(self.full_config_path, "w")

    def test_createlib_corrupted_config(self):
        mo = unittest.mock.mock_open(read_data="{")
        with unittest.mock.patch("chadow.open", mo) as mopen, unittest.mock.patch("chadow.os.mkdir") as mmkdir:
            self.runner.invoke(chadow.createlib, ["testlib"])
            mopen.assert_any_call(self.full_config_path, "rw+")
            mmkdir

if __name__ == "__main__":
    tests = unittest.TestLoader().loadTestsFromTestCase(ChadowTests)
    unittest.TextTestRunner(verbosity=2).run(tests)
