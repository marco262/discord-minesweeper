import os
import unittest
from datetime import datetime

from src.db.db import Db

OWNER_ID1 = -1
OWNER_NAME1 = "FunctionalTestUser1"
OWNER_ID2 = -2
OWNER_NAME2 = "FunctionalTestUser2"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def epoch_to_ts(epoch: int) -> str:
    return dt_to_ts(epoch_to_dt(epoch))


def epoch_to_dt(epoch: int) -> datetime:
    return datetime.fromtimestamp(epoch)


def ts_to_epoch(ts: str) -> int:
    return int(ts_to_dt(ts).timestamp())


def ts_to_dt(ts: str, fmt=TIME_FORMAT) -> datetime:
    return datetime.strptime(ts, fmt)


def dt_to_epoch(dt: datetime) -> int:
    return int(dt.timestamp())


def dt_to_ts(dt: datetime) -> str:
    return dt.strftime(TIME_FORMAT)


def now_epoch() -> int:
    return dt_to_epoch(now_dt())


def now_ts() -> str:
    return dt_to_ts(now_dt())


def now_dt() -> datetime:
    return datetime.utcnow()


class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Change pwd to root folder, same as when main.py is run
        os.chdir("..")

    def setUp(self):
        self.db = Db()

    def tearDown(self):
        self.db.conn.rollback()
        self.db.conn.close()

    def test_add_user(self):
        self.db.add_owner(OWNER_ID1, OWNER_NAME1)
        self.assertEqual(OWNER_ID1, self.db.get_owner_id(OWNER_NAME1))

    def test_add_user_twice(self):
        self.db.add_owner(OWNER_ID1, OWNER_NAME1)
        self.db.add_owner(OWNER_ID1, OWNER_NAME2)
        self.assertEqual(OWNER_ID1, self.db.get_owner_id(OWNER_NAME1))

        sql = "SELECT COUNT(*) FROM owners WHERE name=?"
        self.assertEqual(1, self.db.cur.execute(sql, [OWNER_NAME1]).fetchone()[0])
        self.assertEqual(0, self.db.cur.execute(sql, [OWNER_NAME2]).fetchone()[0])

    def test_get_display_mode(self):
        self.db.add_owner(OWNER_ID1, OWNER_NAME1)
        self.assertEqual("EDIT", self.db.get_display_mode(OWNER_ID1))
        self.db.set_display_mode(OWNER_ID1, "POST")
        self.assertEqual("POST", self.db.get_display_mode(OWNER_ID1))
        with self.assertRaisesRegex(ValueError, r"^BAD_VALUE is not a valid display mode. Valid values are "
                                                r"\['POST', 'EDIT', 'UPDATE'\]$"):
            self.db.set_display_mode(OWNER_ID1, "BAD_VALUE")
        # Set display_mode to a bad value
        sql = "UPDATE owners SET display_mode=? WHERE id=?"
        self.db.cur.execute(sql, ["BAD_VALUE", OWNER_ID1])
        with self.assertRaisesRegex(ValueError, r"^BAD_VALUE is not a valid display mode. Valid values are "
                                                r"\['POST', 'EDIT', 'UPDATE'\]$"):
            self.db.get_display_mode(OWNER_ID1)

    def test_add_task(self):
        rowid = self.db.add_task("Spoon Spain", OWNER_ID1)
        retrieved_rowid = self.db.filter_task_ids_by_name([rowid], "spain")
        self.assertEqual(rowid, retrieved_rowid[0])

    def test_add_multiple_tasks(self):
        rowids = self.db.add_tasks(["Spoon Spain", "Spank Spain", "Split Spain", "Flog France"], OWNER_ID1)
        retrieved_rowids = self.db.filter_task_ids_by_name([rowids[0], rowids[2], rowids[3]], "spain")
        self.assertEqual(rowids[0], retrieved_rowids[0])
        self.assertEqual(rowids[2], retrieved_rowids[1])
        self.assertEqual(2, len(retrieved_rowids))

    def test_get_task_name(self):
        rowid1 = self.db.add_task("Spoon Spain", OWNER_ID1)
        rowid2 = self.db.add_task("Spank Spain", OWNER_ID1)
        self.assertEqual("Spoon Spain", self.db.get_task_name(rowid1))
        self.assertEqual("Spank Spain", self.db.get_task_name(rowid2))

    def test_get_task_names(self):
        rowid1 = self.db.add_task("Spoon Spain", OWNER_ID1)
        rowid2 = self.db.add_task("Spank Spain", OWNER_ID1)
        rowid3 = self.db.add_task("Splain Spain", OWNER_ID1)
        self.assertEqual(['Spoon Spain', 'Splain Spain'], self.db.get_task_names([rowid1, rowid3]))

    def test_rename_task(self):
        rowid = self.db.add_task("Spoon Spain", OWNER_ID1)
        self.db.rename_task(rowid, "Fork France")
        self.assertEqual("Fork France", self.db.get_task_name(rowid))

    def test_start_task(self):
        rowid = self.db.add_task("Spoon Spain", OWNER_ID1)
        self.assertEqual("NOT_STARTED", self.db.get_task_state(rowid))
        self.db.start_task(rowid)
        self.assertEqual("STARTED", self.db.get_task_state(rowid))
        started_time = ts_to_epoch(self.db.get_task_start_time(rowid))
        # Accept any epoch that's within one second of the current epoch.
        self.assertAlmostEqual(now_epoch(), started_time, delta=1)

    def test_stop_task(self):
        rowid = self.db.add_task("Spoon Spain", OWNER_ID1)
        five_seconds_ago = epoch_to_ts(now_epoch() - 5)
        sql = """
        UPDATE tasks
        SET 
            state = 'STARTED',
            started_ts = ?
        WHERE 
          rowid = ?;
        """
        self.db.cur.execute(sql, [five_seconds_ago, rowid])
        self.assertEqual("STARTED", self.db.get_task_state(rowid))
        self.db.stop_task(rowid)
        self.assertEqual("NOT_STARTED", self.db.get_task_state(rowid))
        self.assertIsNone(self.db.get_task_start_time(rowid))
        self.assertAlmostEqual(5, self.db.get_time_spent_sec(rowid), delta=1)

    def test_complete_task(self):
        rowid = self.db.add_task("Spoon Spain", OWNER_ID1)
        five_seconds_ago = epoch_to_ts(now_epoch() - 5)
        sql = """
        UPDATE tasks
        SET 
            state = 'STARTED',
            started_ts = ?
        WHERE 
          rowid = ?;
        """
        self.db.cur.execute(sql, [five_seconds_ago, rowid])
        self.assertEqual("STARTED", self.db.get_task_state(rowid))
        self.db.complete_task(rowid)
        self.assertEqual("CHECKED", self.db.get_task_state(rowid))
        completed_time = ts_to_epoch(self.db.get_task_complete_time(rowid))
        # Accept any epoch that's within one second of the current epoch.
        self.assertAlmostEqual(now_epoch(), completed_time, delta=1)
        self.assertAlmostEqual(5, self.db.get_time_spent_sec(rowid), delta=1)

    def test_complete_task_not_started(self):
        rowid = self.db.add_task("Spoon Spain", OWNER_ID1)
        five_seconds_ago = epoch_to_ts(now_epoch() - 5)
        sql = "UPDATE tasks SET started_ts = ? WHERE rowid = ?;"
        self.db.cur.execute(sql, [five_seconds_ago, rowid])
        self.db.complete_task(rowid)
        self.assertEqual(5, self.db.get_time_spent_sec(rowid))

    def test_uncomplete_task(self):
        rowid = self.db.add_task("Spoon Spain", OWNER_ID1)
        self.db.complete_task(rowid)
        self.assertIsNotNone(self.db.get_task_complete_time(rowid))
        self.db.uncomplete_task(rowid)
        self.assertIsNone(self.db.get_task_complete_time(rowid))

    def test_get_tasks(self):
        rowid1 = self.db.add_task("Spoon Spain", OWNER_ID1)
        rowid2 = self.db.add_task("Spank Spain", OWNER_ID1)
        rowid3 = self.db.add_task("Splain Spain", OWNER_ID1)
        self.db.start_task(rowid1)
        self.db.complete_task(rowid1)
        self.db.start_task(rowid2)
        current_time = now_ts()
        expected_result = [
            {'name': 'Spoon Spain',
             'owner_id': OWNER_ID1,
             'state': 'CHECKED',
             'created_ts': current_time,
             'started_ts': current_time,
             'completed_ts': current_time,
             'time_spent_sec': 0},
            {'name': 'Spank Spain',
             'owner_id': OWNER_ID1,
             'state': 'STARTED',
             'created_ts': current_time,
             'started_ts': current_time,
             'completed_ts': None,
             'time_spent_sec': 0},
            {'name': 'Splain Spain',
             'owner_id': OWNER_ID1,
             'state': 'NOT_STARTED',
             'created_ts': current_time,
             'started_ts': None,
             'completed_ts': None,
             'time_spent_sec': 0}
        ]
        self.assertEqual(expected_result, self.db.get_tasks([rowid1, rowid2, rowid3]))
        self.assertEqual(["CHECKED", "STARTED", "NOT_STARTED"], self.db.get_task_states([rowid1, rowid2, rowid3]))

    def test_get_list_items_no_list(self):
        self.assertIsNone(self.db.get_list_items(OWNER_ID1))

    def test_add_new_list(self):
        self.db.new_list([1, 2, 3], OWNER_ID1)
        current_time = now_ts()
        retrieved_list = self.db.get_list(OWNER_ID1)
        self.assertEqual([[1, 2, 3], OWNER_ID1, current_time, current_time], retrieved_list)
        retrieved_list = self.db.get_list_items(OWNER_ID1)
        self.assertEqual([1, 2, 3], retrieved_list)

    def test_add_and_replace_new_list(self):
        self.db.new_list([1, 2, 3], OWNER_ID1)
        self.db.new_list([4, 5, 6], OWNER_ID1)
        retrieved_list = self.db.get_list_items(OWNER_ID1)
        self.assertEqual([4, 5, 6], retrieved_list)

    def test_update_list(self):
        self.db.new_list([1, 2, 3], OWNER_ID1)
        self.db.update_list_items([7, 8, 9], OWNER_ID1)
        retrieved_list = self.db.get_list_items(OWNER_ID1)
        self.assertEqual([7, 8, 9], retrieved_list)

    def test_get_last_message_id(self):
        self.db.new_list([1, 2, 3], OWNER_ID1)
        channel_name1 = "channel_name1"
        last_message_id1 = 1111111
        channel_name2 = "channel_name2"
        last_message_id2 = 2222222
        self.assertIsNone(self.db.get_last_message_id(OWNER_ID1, channel_name1))
        self.db.set_last_message_id(OWNER_ID1, channel_name1, last_message_id1)
        self.assertEqual(last_message_id1, self.db.get_last_message_id(OWNER_ID1, channel_name1))
        self.assertIsNone(self.db.get_last_message_id(OWNER_ID1, channel_name2))
        self.db.set_last_message_id(OWNER_ID1, channel_name2, last_message_id2)
        self.assertEqual(last_message_id1, self.db.get_last_message_id(OWNER_ID1, channel_name1))
        self.assertEqual(last_message_id2, self.db.get_last_message_id(OWNER_ID1, channel_name2))


if __name__ == "__main__":
    unittest.main()
