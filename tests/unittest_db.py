import os
import unittest

from src.db.db import Db


OWNER_ID = 1234567
OWNER_ID2 = 7654321

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
        retrieved_rowid = self.db.get_task_ids_by_name("Spain")
        self.assertEqual(rowid, retrieved_rowid)

    def test_add_multiple_tasks(self):
        rowid1 = self.db.add_task("Spoon Spain", OWNER_ID)
        rowid2 = self.db.add_task("Spank Spain", OWNER_ID)
        rowid3 = self.db.add_task("Spank Spain", OWNER_ID2)
        retrieved_rowids = self.db.get_task_ids_by_name("Spain", OWNER_ID)
        self.assertEqual((rowid1,), retrieved_rowids[0])
        self.assertEqual((rowid2,), retrieved_rowids[1])
        self.assertEqual(2, len(retrieved_rowids))


if __name__ == "__main__":
    unittest.main()
