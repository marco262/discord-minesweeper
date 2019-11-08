import sqlite3
import sys
from json import dumps, loads
from typing import Iterable


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
        self.cur.execute(sql, [discord_id, user])

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

    def rename_task(self, task_id, task_name):
        sql = """
        UPDATE tasks SET name = ? WHERE rowid = ?;
        """
        self.cur.execute(sql, [task_name, task_id])

    def get_task_ids_by_name(self, task_name, owner_id):
        sql = """
        SELECT rowid FROM tasks
        WHERE 
          name LIKE ? AND
          owner_id = ?;
        """
        response = self.cur.execute(sql, ['%' + task_name + '%', owner_id]).fetchall()
        return [x[0] for x in response]

    def get_task_name(self, task_id):
        sql = """
        SELECT name FROM tasks
        WHERE rowid=?
        """
        return self.cur.execute(sql, [task_id]).fetchone()[0]

    def get_task_names(self, task_ids: Iterable):
        """
        :param task_ids: List of ids
        :return: List of str
        """
        param_placeholders = ",".join("?"*len(task_ids))
        sql = f"SELECT name FROM tasks WHERE rowid IN ({param_placeholders})"
        response = self.cur.execute(sql, task_ids).fetchall()
        return [x[0] for x in response]

    def get_tasks(self, task_ids: Iterable):
        """
        :param task_ids: List of ids
        :return: List of lists
        """
        param_placeholders = ",".join("?"*len(task_ids))
        sql = f"SELECT * FROM tasks WHERE rowid IN ({param_placeholders})"
        return self.cur.execute(sql, task_ids).fetchall()

    def start_task(self, task_id):
        sql = """
        UPDATE tasks
        SET started_ts = CURRENT_TIMESTAMP
        WHERE 
          rowid = ?;
        """
        self.cur.execute(sql, [task_id])

    def get_task_start_time(self, task_id):
        """
        :param task_id:
        :return: Timestamp of format %Y-%m-%d %H:%M:%S
        """
        sql = """
        SELECT 
          started_ts
        FROM tasks
        WHERE
          rowid = ?;
        """
        return self.cur.execute(sql, [task_id]).fetchone()[0]

    def complete_task(self, task_id):
        sql = """
        UPDATE tasks
        SET completed_ts = CURRENT_TIMESTAMP
        WHERE 
          rowid = ?;
        """
        self.cur.execute(sql, [task_id])

    def get_task_complete_time(self, task_id):
        """
        :param task_id:
        :return: Timestamp of format %Y-%m-%d %H:%M:%S
        """
        sql = """
        SELECT 
          completed_ts
        FROM tasks
        WHERE
          rowid = ?;
        """
        return self.cur.execute(sql, [task_id]).fetchone()[0]

    def new_list(self, list_items, owner_id):
        """
        :param owner_id:
        :param list_items: List of ints
        :return:
        """
        sql = """
        INSERT INTO lists (items, owner_id) VALUES (?, ?);
        """
        json_list = dumps(list_items)
        try:
            self.cur.execute(sql, [json_list, owner_id])
            return
        except sqlite3.IntegrityError:
            pass

        sql = """
        UPDATE lists 
        SET
          items = ?,
          created_ts = CURRENT_TIMESTAMP
        WHERE
          owner_id = ? 
        """
        self.cur.execute(sql, [json_list, owner_id])

    def get_list(self, owner_id):
        sql = "SELECT * FROM lists WHERE owner_id = ?"
        response = list(self.cur.execute(sql, [owner_id]).fetchone())
        response[0] = loads(response[0])
        return response
