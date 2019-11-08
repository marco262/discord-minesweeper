from datetime import datetime
import os
import unittest

from src.db.db import Db


OWNER_ID = 1234567
OWNER_ID2 = 7654321


def ts_to_dt(ts, fmt="%Y-%m-%d %H:%M:%S"):
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

    def test_start_task(self):
        rowid = self.db.add_task("Spoon Spain", OWNER_ID)
        self.db.start_task(rowid, OWNER_ID)
        current_time = datetime.utcnow()
        started_time = ts_to_dt(self.db.get_task_start_time(rowid, OWNER_ID))
        # Accept any epoch that's within one second of the current epoch.
        delta = (current_time - started_time).total_seconds()
        self.assertLessEqual(delta, 1)

    def test_complete_task(self):
        rowid = self.db.add_task("Spoon Spain", OWNER_ID)
        self.db.complete_task(rowid, OWNER_ID)
        current_time = datetime.utcnow()
        completed_time = ts_to_dt(self.db.get_task_complete_time(rowid, OWNER_ID))
        # Accept any epoch that's within one second of the current epoch.
        delta = (current_time - completed_time).total_seconds()
        self.assertLessEqual(delta, 1)


if __name__ == "__main__":
    unittest.main()
