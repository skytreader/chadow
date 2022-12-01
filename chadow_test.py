import chadow
import copy
import json
import os
import traceback
import unittest
import unittest.mock
import sys

from chadow import ExitCodes
from click.testing import CliRunner

DEFAULT_CONFIG = {
    "version": "0.1.0",
    "libraryMapping": {}
}

DEFAULT_CONFIG_MOCK_VALUE = json.dumps(DEFAULT_CONFIG, indent=2)

class ChadowTests(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.full_config_path = os.path.join(chadow.APP_ROOT, chadow.CONFIG_NAME)

    def __verify_call(self, click_fn, args, expected_return=0):
        result = self.runner.invoke(click_fn, args)

        if result.exception is not None:
            traceback.print_exception(*result.exc_info)
        self.assertEqual(result.exit_code, expected_return)

    def test_createlib(self):
        mo = unittest.mock.mock_open(read_data=DEFAULT_CONFIG_MOCK_VALUE)
        with unittest.mock.patch("chadow.open", mo) as mopen, unittest.mock.patch("chadow.os.mkdir") as mmkdir:
            self.__verify_call(chadow.createlib, ["testlib"])
            mopen.assert_any_call(self.full_config_path, "r")
            mopen.assert_any_call(self.full_config_path, "w")
            mmkdir.assert_any_call(os.path.join(chadow.APP_ROOT, "testlib"))

    def test_createlib_corrupted_config(self):
        mo = unittest.mock.mock_open(read_data="{")
        with unittest.mock.patch("chadow.open", mo) as mopen:
            self.__verify_call(chadow.createlib, ["testlib"], ExitCodes.INVALID_CONFIG.value)
            mopen.assert_any_call(self.full_config_path, "r")

    @unittest.mock.patch("chadow.os.mkdir")
    @unittest.mock.patch("chadow.open", new_callable=unittest.mock.mock_open, read_data=DEFAULT_CONFIG_MOCK_VALUE)
    def test_createlib_corrupted_config_force_recreate(self, open_mock, mkdir_mock):
        self.__verify_call(chadow.createlib, ["testlib", "--force"])
        open_mock.assert_any_call(self.full_config_path, "r")
        open_mock.assert_any_call(self.full_config_path, "w")
        mkdir_mock.assert_any_call(os.path.join(chadow.APP_ROOT, "testlib"))

    @unittest.mock.patch("chadow.os.mkdir")
    def test_createlib_dupename(self, mkdir_mock):
        config = copy.deepcopy(DEFAULT_CONFIG)
        config["libraryMapping"]["testlib"] = {
            "sectors": {},
            "comparator": "filename"
        }
        mo = unittest.mock.mock_open(read_data=json.dumps(config))
        with unittest.mock.patch("chadow.open", mo) as mopen:
            self.__verify_call(chadow.createlib, ["testlib"], ExitCodes.STATE_CONFLICT.value)
            mopen.assert_any_call(self.full_config_path, "r")
            mkdir_mock.assert_not_called()

    @unittest.skip("")
    @unittest.mock.patch("chadow.open", new_callable=unittest.mock.mock_open)
    def test_deletelib(self, open_mock):
        self.runner.invoke(chadow.createlib, ["testlib"])
        self.runner.invoke(chadow.deletelib, ["testlib"])

if __name__ == "__main__":
    tests = unittest.TestLoader().loadTestsFromTestCase(ChadowTests)
    unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(tests)
