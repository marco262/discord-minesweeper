import sqlite3
import sys


class Db:

    def __init__(self, filename="database_files/list-keeper.db", auto_commit=True):
        self.db = sqlite3.connect(filename)
        self.cur = self.db.cursor()
        self.auto_commit = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            try:
                if exc_type:
                    self.db.rollback()
                    print(exc_type, exc_val, exc_tb, file=sys.stderr)
                elif self.auto_commit:
                    self.db.commit()
            finally:
                self.db.close()

    def add_owner(self, discord_id, user):
        sql = "INSERT OR IGNORE INTO owners (id, name) VALUES (?, ?)"
        print(self.cur.execute(sql, [discord_id, user]).fetchall())

    def list_owners(self):
        sql = "SELECT * FROM owners"
        print(self.cur.execute(sql).fetchall())

    def get_owner_id(self, name):
        sql = "SELECT id FROM owners WHERE name=?"
        return self.cur.execute(sql, [name]).fetchone()[0]

