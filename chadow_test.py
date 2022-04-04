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

    def test_createlib(self):
        mo = unittest.mock.mock_open(read_data= DEFAULT_CONFIG_MOCK_VALUE)
        with unittest.mock.patch("chadow.open", mo) as mopen:
            self.runner.invoke(chadow.createlib, ["testlib"])
            mopen.assert_any_call(os.path.join(chadow.APP_ROOT, chadow.CONFIG_NAME), "r")

if __name__ == "__main__":
    tests = unittest.TestLoader().loadTestsFromTestCase(ChadowTests)
    unittest.TextTestRunner(verbosity=2).run(tests)
