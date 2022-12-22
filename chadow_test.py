import argparse
import chadow
import copy
import json
import os
import traceback
import unittest
import unittest.mock
import sys
import string

from chadow import DirectoryIndex, ExitCodes
from click.testing import CliRunner

DEFAULT_CONFIG = {
    "version": "0.1.0",
    "libraryMapping": {}
}

DEFAULT_CONFIG_MOCK_VALUE = json.dumps(DEFAULT_CONFIG, indent=2)

class DirectoryIndexTests(unittest.TestCase):

    def test_hash_and_equality(self):
        index1 = DirectoryIndex("test")
        index2 = DirectoryIndex("test")

        for letter in string.ascii_lowercase:
            index1.add_to_index(letter)

        for letter in string.ascii_lowercase[::-1]:
            index2.add_to_index(letter)

        self.assertEqual(index1, index2)
        self.assertEqual(hash(index1), hash(index2))

class ChadowTests(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.full_config_path = os.path.join(chadow.APP_ROOT, chadow.CONFIG_NAME)

    def _verify_call(self, click_fn, args, expected_return=0):
        result = self.runner.invoke(click_fn, args)

        if result.exception is not None:
            traceback.print_exception(*result.exc_info)
        self.assertEqual(result.exit_code, expected_return)

        return result.output

class CreateLibTests(ChadowTests):

    @unittest.mock.patch("chadow.json.dump")
    def test_createlib(self, mock_json_dump):
        mo = unittest.mock.mock_open(read_data=DEFAULT_CONFIG_MOCK_VALUE)
        with unittest.mock.patch("chadow.open", mo) as mopen, unittest.mock.patch("chadow.os.mkdir") as mmkdir:
            self._verify_call(chadow.createlib, ["testlib"])
            mopen.assert_any_call(self.full_config_path, "r")
            mopen.assert_any_call(self.full_config_path, "w")
            mmkdir.assert_any_call(os.path.join(chadow.APP_ROOT, "testlib"))
            updated_config = copy.deepcopy(DEFAULT_CONFIG)
            updated_config["libraryMapping"]["testlib"] = chadow.make_default_lib("filename")
            mock_json_dump.assert_called_with(updated_config, unittest.mock.ANY)

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
        self._verify_call(chadow.deletelib, ["testlib"], ExitCodes.STATE_CONFLICT.value)
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

    @unittest.mock.patch("chadow.json.dump")
    @unittest.mock.patch("chadow.os.mkdir")
    def test_regsector(self, mock_mkdir, mock_json_dump):
        _mock_open = unittest.mock.mock_open(read_data=json.dumps(self.config))
        with unittest.mock.patch("chadow.open", _mock_open) as mock_open:
            self._verify_call(chadow.regsector, ["testlib", "sector1"])
            mock_mkdir.assert_called_once_with(chadow.make_sector_dirname("testlib", "sector1"))
            self.config["libraryMapping"]["testlib"]["sectors"]["sector1"] = []
            mock_json_dump.assert_any_call(self.config, unittest.mock.ANY)

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
                ExitCodes.INVALID_ARG.value
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
                ExitCodes.STATE_CONFLICT.value
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
                ExitCodes.STATE_CONFLICT.value
            )
            mock_mkdir.assert_not_called()

class RegMediaTests(ChadowTests):

    def setUp(self):
        super().setUp()
        self.config = copy.deepcopy(DEFAULT_CONFIG)
        self.config["libraryMapping"]["testlib"] = chadow.make_default_lib("filename")
        self.config["libraryMapping"]["testlib"]["sectors"]["sector1"] = []

    @unittest.mock.patch("chadow.json.dump")
    @unittest.mock.patch("chadow.os.path.isdir")
    @unittest.mock.patch("chadow.os.mkdir")
    def test_regmedia(self, mock_mkdir, mock_isdir, mock_json_dump):
        mock_isdir.return_value = True
        _mock_open = unittest.mock.mock_open(read_data=json.dumps(self.config))
        with unittest.mock.patch("chadow.open", _mock_open) as mock_open:
            self._verify_call(chadow.regmedia, ["testlib", "sector1", "/media/testpath"])
            self.config["libraryMapping"]["testlib"]["sectors"]["sector1"].append("/media/testpath")
            mock_json_dump.assert_any_call(self.config, unittest.mock.ANY)
            mock_isdir.assert_called_with(chadow.make_sector_dirname("testlib", "sector1"))
            mock_open.assert_any_call("/media/testpath/.chadow-metadata", "w+")

    @unittest.mock.patch("chadow.os.path.isfile")
    @unittest.mock.patch("chadow.json.dump")
    @unittest.mock.patch("chadow.os.path.isdir")
    @unittest.mock.patch("chadow.os.mkdir")
    def test_regmedia_metadata_exists(self, mock_mkdir, mock_isdir, mock_json_dump, mock_isfile):
        mock_isfile.return_value = True
        mock_isdir.return_value = True
        _mock_open = unittest.mock.mock_open(read_data=json.dumps(self.config))
        with unittest.mock.patch("chadow.open", _mock_open) as mock_open:
            self._verify_call(
                chadow.regmedia,
                ["testlib", "sector1", "/media/testpath"],
                ExitCodes.STATE_CONFLICT.value
            )

    @unittest.mock.patch("chadow.json.dump")
    @unittest.mock.patch("chadow.os.path.isdir")
    @unittest.mock.patch("chadow.os.mkdir")
    def test_regmedia_directory_dne(self, mock_mkdir, mock_isdir, mock_json_dump):
        mock_isdir.return_value = False
        _mock_open = unittest.mock.mock_open(read_data=json.dumps(self.config))
        with unittest.mock.patch("chadow.open", _mock_open) as mock_open:
            self._verify_call(
                chadow.regmedia,
                ["testlib", "sector1", "/media/testpath"],
                ExitCodes.STATE_CONFLICT.value
            )

    @unittest.mock.patch("chadow.json.dump")
    @unittest.mock.patch("chadow.os.path.isdir")
    @unittest.mock.patch("chadow.os.mkdir")
    def test_regmedia_reserved_char(self, mock_mkdir, mock_isdir, mock_json_dump):
        _mock_open = unittest.mock.mock_open(read_data=json.dumps(self.config))
        with unittest.mock.patch("chadow.open", _mock_open) as mock_open:
            path = chadow.PATH_SEPARATOR_REPLACEMENT.join(("/media/test", "path"))
            self._verify_call(
                chadow.regmedia,
                ["testlib", "sector1", path],
                ExitCodes.INVALID_ARG.value
            )
            mock_mkdir.assert_not_called()
            mock_isdir.assert_not_called()
            mock_json_dump.assert_not_called()
            mock_open.assert_not_called()

class IndexTests(ChadowTests):

    def setUp(self):
        super().setUp()
        self.config = copy.deepcopy(DEFAULT_CONFIG)
        self.config["libraryMapping"]["testlib"] = chadow.make_default_lib("filename")
        self.sector_path = os.path.join("media", "ehd", "photos")
        self.config["libraryMapping"]["testlib"]["sectors"]["sector1"] = [self.sector_path]
        self.mock_directory_structure = iter([
            (
                self.sector_path,
                [
                    "summer",
                    "winter"
                ],
                [
                    "photo1.jpg",
                    "photo2.JPG"
                ]
            ),
            (
                os.path.join(self.sector_path, "summer"),
                [
                    "vacation"
                ],
                [
                    "flowers.jpg",
                    "invitation.png"
                ]
            ),
            (
                os.path.join(self.sector_path, "summer", "vacation"),
                [],
                [
                    "party.jpg",
                    "fireflies.RAW",
                    "food.jpg"
                ]
            ),
            (
                os.path.join(self.sector_path, "winter"),
                [],
                [
                    "christmas.jpg",
                    "snow.jpg"
                ]
            )
        ])

    def __construct_expected_index(self):
        index = chadow.DirectoryIndex(self.sector_path, is_top_level=True)
        for _file in ["photo1.jpg", "photo2.JPG"]:
            index.add_to_index(_file)

        summer_index = chadow.DirectoryIndex("summer", is_top_level=False)
        for _file in ["flowers.jpg", "invitation.png"]:
            summer_index.add_to_index(_file)

        summer_vacation_index = chadow.DirectoryIndex(
            "vacation",
            is_top_level=False
        )
        for _file in ["party.jpg", "fireflies.RAW", "food.jpg"]:
            summer_vacation_index.add_to_index(_file)

        summer_index.add_to_index(summer_vacation_index)
        index.add_to_index(summer_index)

        winter_index = chadow.DirectoryIndex("winter", is_top_level=False)
        for _file in ["christmas.jpg", "snow.jpg"]:
            winter_index.add_to_index(_file)
        index.add_to_index(winter_index)

        return index

    @unittest.mock.patch("chadow.os.walk")
    def test_index(self, mock_os_walk):
        _mock_open = unittest.mock.mock_open(read_data=json.dumps(self.config))
        mock_os_walk.return_value = self.mock_directory_structure
        with unittest.mock.patch("chadow.open", _mock_open) as mock_open:
            output = self._verify_call(
                chadow.index,
                ["testlib", "sector1", self.sector_path, "--verbose"]
            )
            created_index = chadow.DirectoryIndex.construct_from_dict(
                json.loads(output)
            )
            print(created_index.to_json())
            print(self.__construct_expected_index().to_json())
            self.assertEqual(self.__construct_expected_index(), created_index)
            mock_os_walk.assert_called()
    
    @unittest.mock.patch("chadow.os.walk")
    def test_unregistered_media(self, mock_os_walk):
        self.config["libraryMapping"]["testlib"]["sectors"]["sector1"] = []
        _mock_open = unittest.mock.mock_open(read_data=json.dumps(self.config))
        with unittest.mock.patch("chadow.open", _mock_open) as mock_open:
            self._verify_call(
                chadow.index,
                ["testlib", "sector1", self.sector_path],
                ExitCodes.STATE_CONFLICT.value
            )
            mock_os_walk.assert_not_called()
    
    @unittest.mock.patch("chadow.os.walk")
    def test_nonexistent_lib(self, mock_os_walk):
        _mock_open = unittest.mock.mock_open(read_data=DEFAULT_CONFIG_MOCK_VALUE)
        with unittest.mock.patch("chadow.open", _mock_open) as mock_open:
            self._verify_call(
                chadow.index,
                ["testlib", "sector1", self.sector_path],
                ExitCodes.INVALID_CONFIG.value
            )
            mock_os_walk.assert_not_called()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="chadow test suite",
        description="tests for the chadow back-up system"
    )
    parser.add_argument("-s", "--suite", required=False, type=str)
    args = vars(parser.parse_args())
    has_no_suite = args.get("suite") is None
    tests_to_run = (
        sys.modules[__name__]
        if has_no_suite else
        getattr(sys.modules[__name__], args["suite"])
    )
    tests = (
        unittest.TestLoader().loadTestsFromModule(tests_to_run)
        if has_no_suite else
        unittest.TestLoader().loadTestsFromTestCase(tests_to_run)
    )
    unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(tests)
