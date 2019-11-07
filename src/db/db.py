import sqlite3
import sys


class Db:

    def __init__(self, filename="list-keeper.db"):
        self.db = sqlite3.connect(filename)
        self.cur = self.db.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            try:
                if exc_type:
                    self.db.rollback()
                    print(exc_type, exc_val, exc_tb, file=sys.stderr)
                else:
                    self.db.commit()
            finally:
                self.db.close()

    def add_user(self, discord_id, user):
        sql = "INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)"
        print(self.cur.execute(sql, [discord_id, user]).fetchall())

    def list_users(self):
        sql = "SELECT * FROM users"
        print(self.cur.execute(sql).fetchall())

    def get_user_id(self, name):
        sql = "SELECT id FROM users WHERE name=?"
        return self.cur.execute(sql, [name]).fetchone()[0]


if __name__ == "__main__":
    with Db() as db:
        db.add_user(1234567, "Marco262")
        print(db.get_user_id("Marco262"))