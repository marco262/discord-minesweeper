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

    def add_task(self, task_name, owner_id):
        sql = """
        INSERT INTO tasks (name, owner_id) VALUES (?, ?);
        """
        self.cur.execute(sql, [task_name, owner_id])
        return self.cur.lastrowid

    def get_task_ids_by_name(self, task_name, owner_id):
        sql = """
        SELECT rowid FROM tasks
        WHERE 
          name LIKE ? AND
          owner_id = ?;
        """
        return self.cur.execute(sql, ['%' + task_name + '%', owner_id]).fetchall()

    def start_task(self, task_id, owner_id):
        sql = """
        UPDATE tasks
        SET started_ts = CURRENT_TIMESTAMP
        WHERE 
          rowid = ? AND
          owner_id = ?;
        """
        self.cur.execute(sql, [task_id, owner_id])

    def get_task_start_time(self, task_id, owner_id):
        """
        :param task_id:
        :param owner_id:
        :return: Timestamp of format %Y-%m-%d %H:%M:%S
        """
        sql = """
        SELECT 
          started_ts
        FROM tasks
        WHERE
          rowid = ? AND
          owner_id = ?;
        """
        return self.cur.execute(sql, [task_id, owner_id]).fetchone()[0]

    def complete_task(self, task_id, owner_id):
        sql = """
        UPDATE tasks
        SET completed_ts = CURRENT_TIMESTAMP
        WHERE 
          rowid = ? AND
          owner_id = ?;
        """
        self.cur.execute(sql, [task_id, owner_id])

    def get_task_complete_time(self, task_id, owner_id):
        """
        :param task_id:
        :param owner_id:
        :return: Timestamp of format %Y-%m-%d %H:%M:%S
        """
        sql = """
        SELECT 
          completed_ts
        FROM tasks
        WHERE
          rowid = ? AND
          owner_id = ?;
        """
        return self.cur.execute(sql, [task_id, owner_id]).fetchone()[0]
