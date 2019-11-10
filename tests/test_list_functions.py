import os
import unittest
from unittest import mock

from src.db.db import Db
from src.list_bot import list_engine as e

OWNER_ID = -1
OWNER_NAME = "FunctionalTestUser"


def build_context(message_content="") -> mock.MagicMock:
    m = mock.MagicMock()
    return m, OWNER_ID, OWNER_NAME, message_content


class TestListFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Change pwd to root folder, same as when main.py is run
        os.chdir("..")

    def setUp(self):
        pass

    def tearDown(self):
        with Db() as db:
            db.wipe_owner_data(OWNER_ID)

    def test_new_list(self):
        actual = e.new_list(*build_context("foo\nbar\nbaz"))
        expected = f"Created a new list for {OWNER_NAME}\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_show_list(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual = e.show_list(*build_context())
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_add_tasks(self):
        e.new_list(*build_context("foo"))
        actual = e.add_tasks(*build_context("bar\nbaz"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
