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

    def test_show_list_no_user(self):
        expected = "I don't have a list assigned to FunctionalTestUser. " \
                   "Check ~help newlist to see how to create your own todo list."
        with self.assertRaisesRegex(ListBotError, expected):
            e.show_list(*build_context())

    def test_add_tasks(self):
        e.new_list(*build_context("foo"))
        actual = e.add_tasks(*build_context("bar\nbaz"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_remove_task_by_pos(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual = e.remove_tasks(*build_context("2"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: baz    (2)"
        self.assertEqual(expected, actual)

    def test_remove_task_by_name(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual = e.remove_tasks(*build_context("bar"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: baz    (2)"
        self.assertEqual(expected, actual)

    def test_remove_task_multiple_values(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        with self.assertRaisesRegex(ListBotError, f'Multiple items found matching "ba":\nbar\nbaz'):
            e.remove_tasks(*build_context("ba"))

    def test_remove_task_no_value(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        with self.assertRaisesRegex(ListBotError, f'Couldn\'t find any list item matching "spam"'):
            e.remove_tasks(*build_context("spam"))

    def test_reorder_top(self):
        e.new_list(*build_context("foo\nbar\nbaz\nspam\nsplut"))
        actual = e.top(*build_context('spa'))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: spam    (1)\n" \
                   ":white_large_square: foo    (2)\n" \
                   ":white_large_square: bar    (3)\n" \
                   ":white_large_square: baz    (4)\n" \
                   ":white_large_square: splut    (5)"
        self.assertEqual(expected, actual)

    def test_reorder_bottom(self):
        e.new_list(*build_context("foo\nbar\nbaz\nspam\nsplut"))
        actual = e.bottom(*build_context('bar'))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: baz    (2)\n" \
                   ":white_large_square: spam    (3)\n" \
                   ":white_large_square: splut    (4)\n" \
                   ":white_large_square: bar    (5)"
        self.assertEqual(expected, actual)

    def test_reorder_move(self):
        e.new_list(*build_context('foo\nbar\nbaz\nspam\ntake my "splut" for 2 times'))
        actual = e.move(*build_context('my "splut" for 2 3'))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ':white_large_square: take my "splut" for 2 times    (3)\n' \
                   ":white_large_square: baz    (4)\n" \
                   ":white_large_square: spam    (5)"
        self.assertEqual(expected, actual)
        actual = e.move(*build_context('"splut" 2'))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ':white_large_square: take my "splut" for 2 times    (2)\n' \
                   ':white_large_square: bar    (3)\n' \
                   ":white_large_square: baz    (4)\n" \
                   ":white_large_square: spam    (5)"
        self.assertEqual(expected, actual)
        actual = e.move(*build_context('splut 4'))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ':white_large_square: bar    (2)\n' \
                   ':white_large_square: baz    (3)\n' \
                   ':white_large_square: take my "splut" for 2 times    (4)\n' \
                   ":white_large_square: spam    (5)"
        self.assertEqual(expected, actual)
        actual = e.move(*build_context('"take" 1'))
        expected = f"{OWNER_NAME}'s list\n" \
                   ':white_large_square: take my "splut" for 2 times    (1)\n' \
                   ':white_large_square: foo    (2)\n' \
                   ':white_large_square: bar    (3)\n' \
                   ':white_large_square: baz    (4)\n' \
                   ":white_large_square: spam    (5)"
        self.assertEqual(expected, actual)

    def test_start_and_stop_task(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual = e.start_task(*build_context("bar"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":arrow_forward: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)
        actual = e.stop_task(*build_context("bar"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_start_two_tasks(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.start_task(*build_context("foo"))
        actual = e.start_task(*build_context("bar"))
        expected = "You can only have one started task at a time."
        self.assertEqual(expected, actual)

    def test_already_started(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.start_task(*build_context("bar"))
        actual = e.start_task(*build_context("bar"))
        expected = "That task is already started."
        self.assertEqual(expected, actual)

    def test_already_stopped(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual = e.stop_task(*build_context("bar"))
        expected = "That task hasn't been started."
        self.assertEqual(expected, actual)

    def test_check_and_uncheck_task(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.start_task(*build_context("bar"))
        actual = e.check_task(*build_context("bar"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_check_mark: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)
        actual = e.uncheck_task(*build_context("bar"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_check_task_not_started(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual = e.check_task(*build_context("bar"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_check_mark: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_check_all(self):
        e.new_list(*build_context("foo\nbar\nbaz\nfweep\nslurp"))
        e.start_task(*build_context("foo"))
        actual = e.check_all(*build_context("1 2 4"))
        expected = f"{OWNER_NAME}'s list\n" \
                   ":white_check_mark: foo    (1)\n" \
                   ":white_check_mark: bar    (2)\n" \
                   ":white_large_square: baz    (3)\n" \
                   ":white_check_mark: fweep    (4)\n" \
                   ":white_large_square: slurp    (5)"
        self.assertEqual(expected, actual)

    def test_check_all_invalid_entry(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.start_task(*build_context("foo"))
        actual = e.check_all(*build_context("1 2 fweep"))
        expected = "All arguments must be positions of tasks, not names."
        self.assertEqual(expected, actual)

    def test_check_all_item_not_in_list(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.start_task(*build_context("foo"))
        with self.assertRaisesRegex(ListBotError, "4 is not a valid list position."):
            e.check_all(*build_context("1 2 4"))

    def test_check_all_already_finished(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.check_task(*build_context("foo"))
        actual = e.check_all(*build_context("1 2"))
        expected = "Task 1 has already been finished."
        self.assertEqual(expected, actual)

    def test_uncheck_task_not_completed(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual = e.uncheck_task(*build_context("bar"))
        expected = "That task hasn't been completed."
        self.assertEqual(expected, actual)

    def test_time_spent_sec(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.start_task(*build_context("foo"))
        sleep(2)
        e.stop_task(*build_context("foo"))
        e.start_task(*build_context("bar"))
        sleep(2)
        e.check_task(*build_context("bar"))
        e.start_task(*build_context("foo"))
        sleep(2)
        e.check_task(*build_context("foo"))
        actual = e.task_time(*build_context())
        expected = f"{OWNER_ID} times" \
                   f"foo: 4s" \
                   f"bar: 2s" \
                   f"baz: 0s" \
                   f"" \
                   f"Total time: 6s"

    def test_clear_tasks(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.start_task(*build_context("foo"))
        e.check_task(*build_context("foo"))
        e.start_task(*build_context("bar"))
        actual = e.clear_checked_tasks(*build_context())
        expected = f"FunctionalTestUser's list\n" \
                   f":arrow_forward: bar    (1)\n" \
                   f":white_large_square: baz    (2)"
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
