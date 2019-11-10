import os
import unittest
from unittest import mock

from src.db import db
from src.list_bot import list_engine as e

OWNER_ID = 1234567
OWNER_NAME = "Marco262"


def build_context(message_content="") -> mock.MagicMock:
    m = mock.MagicMock()
    m.author.id = OWNER_ID
    m.author.name = OWNER_NAME
    m.message.content = message_content
    return m


class TestListFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Change pwd to root folder, same as when main.py is run
        os.chdir("..")
        db.TEST_MODE = True

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_new_list(self):
        c = build_context("~newlist\nfoo\nbar\nbaz")
        expected = "Created a new list for Marco262\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, e.new_list(c))


if __name__ == "__main__":
    unittest.main()
