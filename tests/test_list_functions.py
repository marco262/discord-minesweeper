import os
import unittest
from time import sleep
from unittest import mock

from src.db.db import Db
from src.list_bot import list_engine as e
from src.utils import ListBotError

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
        actual = e.newlist(*build_context("foo\nbar\nbaz"))
        expected = f"Created a new list for {OWNER_NAME}\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_show_list(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        actual = e.show_list(*build_context())
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_add_tasks(self):
        e.newlist(*build_context("foo"))
        actual = e.add(*build_context("bar\nbaz"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_remove_task_by_pos(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        actual = e.remove(*build_context("2"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: baz    (2)"
        self.assertEqual(expected, actual)

    def test_remove_task_by_name(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        actual = e.remove(*build_context("bar"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: baz    (2)"
        self.assertEqual(expected, actual)

    def test_remove_task_multiple_values(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        with self.assertRaisesRegex(ListBotError, f'Multiple items found matching "ba":\nbar\nbaz'):
            e.remove(*build_context("ba"))

    def test_remove_task_no_value(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        with self.assertRaisesRegex(ListBotError, f'Couldn\'t find any list item matching "spam"'):
            e.remove(*build_context("spam"))

    def test_reorder_top(self):
        e.newlist(*build_context("foo\nbar\nbaz\nspam\nsplut"))
        actual = e.top(*build_context('spa'))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: spam    (1)\n" \
                   ":white_large_square: foo    (2)\n" \
                   ":white_large_square: bar    (3)\n" \
                   ":white_large_square: baz    (4)\n" \
                   ":white_large_square: splut    (5)"
        self.assertEqual(expected, actual)

    def test_reorder_bottom(self):
        e.newlist(*build_context("foo\nbar\nbaz\nspam\nsplut"))
        actual = e.bottom(*build_context('bar'))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: baz    (2)\n" \
                   ":white_large_square: spam    (3)\n" \
                   ":white_large_square: splut    (4)\n" \
                   ":white_large_square: bar    (5)"
        self.assertEqual(expected, actual)

    def test_reorder_move(self):
        e.newlist(*build_context("foo\nbar\nbaz\nspam\nsplut"))
        actual = e.move(*build_context('"splut" 3'))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: splut    (3)\n" \
                   ":white_large_square: baz    (4)\n" \
                   ":white_large_square: spam    (5)"
        self.assertEqual(expected, actual)

    def test_start_and_stop_task(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        actual = e.start(*build_context("bar"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":arrow_forward: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)
        actual = e.stop(*build_context("bar"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_start_two_tasks(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        e.start(*build_context("foo"))
        actual = e.start(*build_context("bar"))
        expected = "You can only have one started task at a time."
        self.assertEqual(expected, actual)

    def test_already_started(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        e.start(*build_context("bar"))
        actual = e.start(*build_context("bar"))
        expected = "That task is already started."
        self.assertEqual(expected, actual)

    def test_already_stopped(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        actual = e.stop(*build_context("bar"))
        expected = "That task hasn't been started."
        self.assertEqual(expected, actual)

    def test_check_and_uncheck_task(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        e.start(*build_context("bar"))
        actual = e.check(*build_context("bar"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_check_mark: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)
        actual = e.uncheck(*build_context("bar"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_check_task_not_started(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        actual = e.check(*build_context("bar"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_check_mark: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_uncheck_task_not_completed(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        actual = e.uncheck(*build_context("bar"))
        expected = "That task hasn't been completed."
        self.assertEqual(expected, actual)

    def test_time_spent_sec(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        e.start(*build_context("foo"))
        sleep(2)
        e.stop(*build_context("foo"))
        e.start(*build_context("bar"))
        sleep(2)
        e.check(*build_context("bar"))
        e.start(*build_context("foo"))
        sleep(2)
        e.check(*build_context("foo"))
        actual = e.tasktime(*build_context())
        expected = f"{OWNER_ID} times" \
                   f"foo: 4s" \
                   f"bar: 2s" \
                   f"baz: 0s" \
                   f"" \
                   f"Total time: 6s"

    def test_clear_tasks(self):
        e.newlist(*build_context("foo\nbar\nbaz"))
        e.start(*build_context("foo"))
        e.check(*build_context("foo"))
        e.start(*build_context("bar"))
        actual = e.clear(*build_context())
        expected = f"FunctionalTestUser's list\n" \
                   f":arrow_forward: bar    (1)\n" \
                   f":white_large_square: baz    (2)"
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
