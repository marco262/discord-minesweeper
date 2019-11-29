import os
import unittest
from time import sleep
from unittest import mock

from src.db.db import Db
from src.list_bot import list_functions as e
from src.utils import ListBotError


class Owner:
    id = -1
    name = "FunctionalTestUser"


OWNER = Owner()


def build_context(message_content="") -> mock.MagicMock:
    m = mock.MagicMock()
    return m, OWNER, message_content


class TestListFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Change pwd to root folder, same as when main.py is run
        os.chdir("..")

    def setUp(self):
        pass

    def tearDown(self):
        with Db() as db:
            db.wipe_owner_data(OWNER.id)

    def test_new_list(self):
        actual, _, _ = e.new_list(*build_context("foo\nbar\nbaz"))
        expected = f"Created a new list for {OWNER.name}\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_show_list(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual, _, _ = e.show_list(*build_context())
        expected = f"{OWNER.name}'s list\n" \
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
        actual, _, _ = e.add_tasks(*build_context("bar\nbaz"))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_remove_task_by_pos(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual, _, _ = e.remove_tasks(*build_context("2"))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: baz    (2)"
        self.assertEqual(expected, actual)

    def test_remove_task_by_name(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual, _, _ = e.remove_tasks(*build_context("bar"))
        expected = f"{OWNER.name}'s list\n" \
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
        actual, _, _ = e.top(*build_context('spa'))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_large_square: spam    (1)\n" \
                   ":white_large_square: foo    (2)\n" \
                   ":white_large_square: bar    (3)\n" \
                   ":white_large_square: baz    (4)\n" \
                   ":white_large_square: splut    (5)"
        self.assertEqual(expected, actual)

    def test_reorder_bottom(self):
        e.new_list(*build_context("foo\nbar\nbaz\nspam\nsplut"))
        actual, _, _ = e.bottom(*build_context('bar'))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: baz    (2)\n" \
                   ":white_large_square: spam    (3)\n" \
                   ":white_large_square: splut    (4)\n" \
                   ":white_large_square: bar    (5)"
        self.assertEqual(expected, actual)

    def test_reorder_move(self):
        e.new_list(*build_context('foo\nbar\nbaz\nspam\ntake my "splut" for 2 times'))
        actual, _, _ = e.move(*build_context('my "splut" for 2 3'))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ':white_large_square: take my "splut" for 2 times    (3)\n' \
                   ":white_large_square: baz    (4)\n" \
                   ":white_large_square: spam    (5)"
        self.assertEqual(expected, actual)
        actual, _, _ = e.move(*build_context('"splut" 2'))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ':white_large_square: take my "splut" for 2 times    (2)\n' \
                   ':white_large_square: bar    (3)\n' \
                   ":white_large_square: baz    (4)\n" \
                   ":white_large_square: spam    (5)"
        self.assertEqual(expected, actual)
        actual, _, _ = e.move(*build_context('splut 4'))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ':white_large_square: bar    (2)\n' \
                   ':white_large_square: baz    (3)\n' \
                   ':white_large_square: take my "splut" for 2 times    (4)\n' \
                   ":white_large_square: spam    (5)"
        self.assertEqual(expected, actual)
        actual, _, _ = e.move(*build_context('"take" 1'))
        expected = f"{OWNER.name}'s list\n" \
                   ':white_large_square: take my "splut" for 2 times    (1)\n' \
                   ':white_large_square: foo    (2)\n' \
                   ':white_large_square: bar    (3)\n' \
                   ':white_large_square: baz    (4)\n' \
                   ":white_large_square: spam    (5)"
        self.assertEqual(expected, actual)

    def test_start_and_stop_task(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual, _, _ = e.start_task(*build_context("bar"))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":arrow_forward: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)
        actual, _, _ = e.stop_task(*build_context("bar"))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_start_two_tasks(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.start_task(*build_context("foo"))
        actual, _, _ = e.start_task(*build_context("bar"))
        expected = "You can only have one started task at a time."
        self.assertEqual(expected, actual)

    def test_already_started(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.start_task(*build_context("bar"))
        actual, _, _ = e.start_task(*build_context("bar"))
        expected = "That task is already started."
        self.assertEqual(expected, actual)

    def test_already_stopped(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual, _, _ = e.stop_task(*build_context("bar"))
        expected = "That task hasn't been started."
        self.assertEqual(expected, actual)

    def test_check_and_uncheck_task(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.start_task(*build_context("bar"))
        actual, _, _ = e.check_task(*build_context("bar"))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_check_mark: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)
        actual, _, _ = e.uncheck_task(*build_context("bar"))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_large_square: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_check_task_not_started(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual, _, _ = e.check_task(*build_context("bar"))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_large_square: foo    (1)\n" \
                   ":white_check_mark: bar    (2)\n" \
                   ":white_large_square: baz    (3)"
        self.assertEqual(expected, actual)

    def test_check_list(self):
        e.new_list(*build_context("foo\nbar\nbaz\nfweep\nslurp"))
        e.start_task(*build_context("foo"))
        actual, _, _ = e.check_list(*build_context("1 2 4"))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_check_mark: foo    (1)\n" \
                   ":white_check_mark: bar    (2)\n" \
                   ":white_large_square: baz    (3)\n" \
                   ":white_check_mark: fweep    (4)\n" \
                   ":white_large_square: slurp    (5)"
        self.assertEqual(expected, actual)

    def test_check_list_invalid_entry(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.start_task(*build_context("foo"))
        actual, _, _ = e.check_list(*build_context("1 2 fweep"))
        expected = "All arguments must be positions of tasks, not names."
        self.assertEqual(expected, actual)

    def test_check_list_item_not_in_list(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.start_task(*build_context("foo"))
        with self.assertRaisesRegex(ListBotError, "4 is not a valid list position."):
            e.check_list(*build_context("1 2 4"))

    def test_check_list_already_finished(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.check_task(*build_context("foo"))
        actual, _, _ = e.check_list(*build_context("1 2"))
        expected = "Task 1 has already been finished."
        self.assertEqual(expected, actual)

    def test_check_all(self):
        e.new_list(*build_context("foo\nbar\nbaz\nfweep\nslurp"))
        e.start_task(*build_context("foo"))
        e.check_task(*build_context("baz"))
        actual, _, _ = e.check_all(*build_context(""))
        expected = f"{OWNER.name}'s list\n" \
                   ":white_check_mark: foo    (1)\n" \
                   ":white_check_mark: bar    (2)\n" \
                   ":white_check_mark: baz    (3)\n" \
                   ":white_check_mark: fweep    (4)\n" \
                   ":white_check_mark: slurp    (5)"
        self.assertEqual(expected, actual)

    def test_uncheck_task_not_completed(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        actual, _, _ = e.uncheck_task(*build_context("bar"))
        expected = "That task hasn't been completed."
        self.assertEqual(expected, actual)

    @unittest.skip("test_time_spent_sec: Takes time to finish. Only test as needed.")
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
        actual, _, _ = e.task_time(*build_context())
        expected = f"{OWNER.name} times\n" \
                   f"foo: 4s\n" \
                   f"bar: 2s\n" \
                   f"baz: 0s\n" \
                   f"\n" \
                   f"Total time: 6s"
        self.assertEqual(expected, actual)

    def test_clear_tasks(self):
        e.new_list(*build_context("foo\nbar\nbaz"))
        e.start_task(*build_context("foo"))
        e.check_task(*build_context("foo"))
        e.start_task(*build_context("bar"))
        actual, _, _ = e.clear_checked_tasks(*build_context())
        expected = f"FunctionalTestUser's list\n" \
                   f":arrow_forward: bar    (1)\n" \
                   f":white_large_square: baz    (2)"
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
