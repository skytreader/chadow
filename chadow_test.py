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

    def _verify_call(self, click_fn, args, expected_return=0):
        result = self.runner.invoke(click_fn, args)

        if result.exception is not None:
            traceback.print_exception(*result.exc_info)
        self.assertEqual(result.exit_code, expected_return)

class CreateLibTests(ChadowTests):

    def test_createlib(self):
        mo = unittest.mock.mock_open(read_data=DEFAULT_CONFIG_MOCK_VALUE)
        with unittest.mock.patch("chadow.open", mo) as mopen, unittest.mock.patch("chadow.os.mkdir") as mmkdir:
            self._verify_call(chadow.createlib, ["testlib"])
            mopen.assert_any_call(self.full_config_path, "r")
            mopen.assert_any_call(self.full_config_path, "w")
            mmkdir.assert_any_call(os.path.join(chadow.APP_ROOT, "testlib"))

    def test_createlib_corrupted_config(self):
        mo = unittest.mock.mock_open(read_data="{")
        with unittest.mock.patch("chadow.open", mo) as mopen:
            self._verify_call(chadow.createlib, ["testlib"], ExitCodes.INVALID_CONFIG.value)
            mopen.assert_any_call(self.full_config_path, "r")

    @unittest.mock.patch("chadow.os.mkdir")
    @unittest.mock.patch("chadow.open", new_callable=unittest.mock.mock_open, read_data=DEFAULT_CONFIG_MOCK_VALUE)
    def test_createlib_corrupted_config_force_recreate(self, open_mock, mkdir_mock):
        self._verify_call(chadow.createlib, ["testlib", "--force"])
        open_mock.assert_any_call(self.full_config_path, "r")
        open_mock.assert_any_call(self.full_config_path, "w")
        mkdir_mock.assert_any_call(os.path.join(chadow.APP_ROOT, "testlib"))

    @unittest.mock.patch("chadow.os.mkdir")
    def test_createlib_dupename(self, mkdir_mock):
        config = copy.deepcopy(DEFAULT_CONFIG)
        config["libraryMapping"]["testlib"] = chadow.make_default_lib("filename")
        mo = unittest.mock.mock_open(read_data=json.dumps(config))
        with unittest.mock.patch("chadow.open", mo) as mopen:
            self._verify_call(chadow.createlib, ["testlib"], ExitCodes.STATE_CONFLICT.value)
            mopen.assert_any_call(self.full_config_path, "r")
            mkdir_mock.assert_not_called()

class DeleteLibTests(ChadowTests):

    @unittest.mock.patch("chadow.os.rmdir")
    @unittest.mock.patch("chadow.json.dump")
    def test_deletelib(self, mock_json_dump, mock_rmdir):
        config = copy.deepcopy(DEFAULT_CONFIG)
        config["libraryMapping"]["testlib"] = chadow.make_default_lib("filename")
        mo = unittest.mock.mock_open(read_data=json.dumps(config))
        with unittest.mock.patch("chadow.open", mo) as mopen:
            self._verify_call(chadow.deletelib, ["testlib"])
            mock_json_dump.assert_called_with(DEFAULT_CONFIG, unittest.mock.ANY)
            mopen.assert_any_call(self.full_config_path, "rw")
            mock_rmdir.assert_called_once_with(os.path.join(chadow.APP_ROOT, "testlib"))

    @unittest.mock.patch("chadow.os.rmdir")
    @unittest.mock.patch("chadow.json.dump")
    @unittest.mock.patch("chadow.open", new_callable=unittest.mock.mock_open, read_data=DEFAULT_CONFIG_MOCK_VALUE)
    def test_deletelib_nonexistent_lib(self, open_mock, mock_json_dump, mock_rmdir):
        self._verify_call(chadow.deletelib, ["testlib"], chadow.ExitCodes.STATE_CONFLICT.value)
        mock_json_dump.assert_not_called()
        open_mock.assert_any_call(self.full_config_path, "rw")
        mock_rmdir.assert_called_once_with(os.path.join(chadow.APP_ROOT, "testlib"))

    @unittest.mock.patch("chadow.os.rmdir")
    @unittest.mock.patch("chadow.json.dump")
    def test_deletelib_nonexistent_directory(self, mock_json_dump, mock_rmdir):
        # This is technically not necessary but we still want to ensure that
        # rmdir is called.
        mock_rmdir.side_effect = FileNotFoundError()
        config = copy.deepcopy(DEFAULT_CONFIG)
        config["libraryMapping"]["testlib"] = chadow.make_default_lib("filename")
        mo = unittest.mock.mock_open(read_data=json.dumps(config))
        with unittest.mock.patch("chadow.open", mo) as mopen:
            self._verify_call(chadow.deletelib, ["testlib"])
            mock_json_dump.assert_called_with(DEFAULT_CONFIG, unittest.mock.ANY)
            mopen.assert_any_call(self.full_config_path, "rw")
            mock_rmdir.assert_called_once_with(os.path.join(chadow.APP_ROOT, "testlib"))

class RegSectorTests(ChadowTests):

    def setUp(self):
        super().setUp()
        self.config = copy.deepcopy(DEFAULT_CONFIG)
        self.config["libraryMapping"]["testlib"] = chadow.make_default_lib("filename")

    @unittest.mock.patch("chadow.os.mkdir")
    def test_regsector(self, mock_mkdir):
        _mock_open = unittest.mock.mock_open(read_data=json.dumps(self.config))
        with unittest.mock.patch("chadow.open", _mock_open) as mock_open:
            self._verify_call(chadow.regsector, ["testlib", "sector1"])
            mock_mkdir.assert_called_once_with(chadow.make_sector_dirname("testlib", "sector1"))

    @unittest.mock.patch("chadow.os.mkdir")
    def test_regsector_illegal_char(self, mock_mkdir):
        _mock_open = unittest.mock.mock_open(read_data=json.dumps(self.config))
        with unittest.mock.patch("chadow.open", _mock_open) as mock_open:
            self._verify_call(
                chadow.regsector,
                [
                    "testlib",
                    os.path.join("sector", "1")
                ],
                chadow.ExitCodes.INVALID_ARG.value
            )
            mock_mkdir.assert_not_called()

    @unittest.mock.patch("chadow.os.mkdir")
    def test_regsector_dupename(self, mock_mkdir):
        self.config["libraryMapping"]["testlib"]["sectors"]["sector1"] = []
        _mock_open = unittest.mock.mock_open(read_data=json.dumps(self.config))
        with unittest.mock.patch("chadow.open", _mock_open) as mock_open:
            self._verify_call(
                chadow.regsector,
                [
                    "testlib",
                    "sector1"
                ],
                chadow.ExitCodes.STATE_CONFLICT.value
            )
            mock_mkdir.assert_not_called()

    @unittest.mock.patch("chadow.os.mkdir")
    def test_regsector_existing_state_conflict(self, mock_mkdir):
        self.config["libraryMapping"]["testlib"]["sectors"] = []
        _mock_open = unittest.mock.mock_open(read_data=json.dumps(self.config))
        with unittest.mock.patch("chadow.open", _mock_open) as mock_open:
            self._verify_call(
                chadow.regsector,
                [
                    "testlib",
                    "sector1"
                ],
                chadow.ExitCodes.STATE_CONFLICT.value
            )
            mock_mkdir.assert_not_called()

if __name__ == "__main__":
    tests = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(tests)
