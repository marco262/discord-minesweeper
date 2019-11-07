import os
import unittest

from src.db.db import Db


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
        self.db.add_owner(1234567, "Marco262")
        self.assertEqual(1234567, self.db.get_owner_id("Marco262"))

    def test_add_task(self):
        rowid = self.db.add_task("Spoon Spain", 1234567)
        retrieved_rowid = self.db.get_task_ids_by_name("Spain")
        self.assertEqual(rowid, retrieved_rowid)


if __name__ == "__main__":
    unittest.main()
