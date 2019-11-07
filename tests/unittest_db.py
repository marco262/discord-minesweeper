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
        self.db.add_user(1234567, "Marco262")
        self.assertEqual(1234567, self.db.get_user_id("Marco262"))


if __name__ == "__main__":
    unittest.main()
