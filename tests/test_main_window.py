import datetime
import os
import sys
import unittest
from unittest.mock import patch, mock_open

from libs.trnd import TRND
from libs import consts
from libs import utils


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        consts.RESOURCE_FOLDER = os.path.join('..', consts.RESOURCE_FOLDER)
        cls.program = TRND()

    def test_update_app(self):
        consts.GITHUB_API_LINK_RELEASES = 'https://google.com'
        consts.VERSION = 0.0

        def execute_update_test():
            pass

        self.program.app.window.execute_update = execute_update_test

        result, message = self.program.app.window.update_app()
        print(message)
        self.assertTrue(result)
