from datetime import datetime
import os
import unittest

from src.db.db import Db


OWNER_ID = 1234567
OWNER_ID2 = 7654321
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def ts_to_dt(ts, fmt=TIME_FORMAT):
    return datetime.strptime(ts, fmt)


def ts_to_epoch(ts):
    return ts_to_dt(ts).timestamp()


class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Change pwd to root folder, same as when main.py is run
        os.chdir("..")

    def setUp(self):
        self.db = Db()

    def tearDown(self):
        self.db.db.rollback()
        self.db.db.close()

    def test_add_user(self):
        self.db.add_owner(OWNER_ID, "Marco262")
        self.assertEqual(OWNER_ID, self.db.get_owner_id("Marco262"))

    def test_add_user_twice(self):
        self.db.add_owner(OWNER_ID, "Marco262")
        self.db.add_owner(OWNER_ID, "Marco263")
        self.assertEqual(OWNER_ID, self.db.get_owner_id("Marco262"))

        sql = "SELECT COUNT(*) FROM owners WHERE name=?"
        self.assertEqual(1, self.db.cur.execute(sql, ["Marco262"]).fetchone()[0])
        self.assertEqual(0, self.db.cur.execute(sql, ["Marco263"]).fetchone()[0])

    def test_add_task(self):
        rowid = self.db.add_task("Spoon Spain", OWNER_ID)
        retrieved_rowid = self.db.get_task_ids_by_name("Spain", OWNER_ID)
        self.assertEqual(rowid, retrieved_rowid[0])

    def test_add_multiple_tasks(self):
        rowid1 = self.db.add_task("Spoon Spain", OWNER_ID)
        rowid2 = self.db.add_task("Spank Spain", OWNER_ID)
        rowid3 = self.db.add_task("Spank Spain", OWNER_ID2)
        retrieved_rowids = self.db.get_task_ids_by_name("Spain", OWNER_ID)
        self.assertEqual(rowid1, retrieved_rowids[0])
        self.assertEqual(rowid2, retrieved_rowids[1])
        self.assertEqual(2, len(retrieved_rowids))

    def test_get_task_name(self):
        rowid1 = self.db.add_task("Spoon Spain", OWNER_ID)
        rowid2 = self.db.add_task("Spank Spain", OWNER_ID)
        self.assertEqual("Spoon Spain", self.db.get_task_name(rowid1))
        self.assertEqual("Spank Spain", self.db.get_task_name(rowid2))

    def test_get_task_names(self):
        rowid1 = self.db.add_task("Spoon Spain", OWNER_ID)
        rowid2 = self.db.add_task("Spank Spain", OWNER_ID)
        rowid3 = self.db.add_task("Splain Spain", OWNER_ID)
        self.assertEqual(['Spoon Spain', 'Splain Spain'], self.db.get_task_names([rowid1, rowid3, 5, 7]))

    def test_rename_task(self):
        rowid = self.db.add_task("Spoon Spain", OWNER_ID)
        self.db.rename_task(rowid, "Fork France")
        self.assertEqual("Fork France", self.db.get_task_name(rowid))

    def test_start_task(self):
        rowid = self.db.add_task("Spoon Spain", OWNER_ID)
        self.db.start_task(rowid)
        current_time = datetime.utcnow()
        started_time = ts_to_dt(self.db.get_task_start_time(rowid))
        # Accept any epoch that's within one second of the current epoch.
        delta = (current_time - started_time).total_seconds()
        self.assertLessEqual(delta, 1)

    def test_complete_task(self):
        rowid = self.db.add_task("Spoon Spain", OWNER_ID)
        self.db.complete_task(rowid)
        current_time = datetime.utcnow()
        completed_time = ts_to_dt(self.db.get_task_complete_time(rowid))
        # Accept any epoch that's within one second of the current epoch.
        delta = (current_time - completed_time).total_seconds()
        self.assertLessEqual(delta, 1)

    def test_get_tasks(self):
        rowid1 = self.db.add_task("Spoon Spain", OWNER_ID)
        rowid2 = self.db.add_task("Spank Spain", OWNER_ID)
        rowid3 = self.db.add_task("Splain Spain", OWNER_ID)
        self.db.start_task(rowid1)
        self.db.complete_task(rowid1)
        self.db.start_task(rowid2)
        current_time = datetime.utcnow().strftime(TIME_FORMAT)
        expected_result = [
            ('Spoon Spain', '1234567', current_time, current_time, current_time),
            ('Spank Spain', '1234567', current_time, current_time, None),
            ('Splain Spain', '1234567', current_time, None, None)
        ]
        self.assertEqual(expected_result, self.db.get_tasks([rowid1, rowid2, rowid3]))


if __name__ == "__main__":
    unittest.main()
