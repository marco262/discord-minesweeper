import sqlite3
from json import dumps, loads
from typing import Iterable, List, Optional

VERSION_NEEDED = 3
TEST_MODE = False


DISPLAY_MODES = [
    "POST",   # Posts a new list every time a command is given (old behavior)
    "EDIT",   # Edits the previous list posted, except when doing ~newlist or ~list
    "UPDATE"  # Provides a single line update when a command is given. ~list is required to post full list
]


class Db:

    def __init__(self, filename="database_files/list-keeper.db", auto_commit=True):
        self.conn = sqlite3.connect(filename)
        self.cur = self.conn.cursor()
        self.check_version()
        self.auto_commit = auto_commit

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            try:
                if exc_type:
                    self.conn.rollback()
                elif self.auto_commit:
                    self.conn.commit()
            finally:
                self.conn.close()

    def check_version(self):
        sql = "SELECT version FROM version;"
        version = self.cur.execute(sql).fetchone()[0]
        if not version == VERSION_NEEDED:
            raise ValueError(f"Incorrect DB version: {version} != {VERSION_NEEDED}")

    def wipe_owner_data(self, owner_id):
        sql = f"""
        DELETE FROM owners WHERE id = {owner_id};
        DELETE FROM tasks WHERE owner_id = {owner_id};
        DELETE FROM lists WHERE owner_id = {owner_id};
        """
        self.cur.executescript(sql)

    def print_tables(self):
        import pandas
        tables = ["owners", "tasks", "lists"]
        pandas.set_option("display.width", None)
        for t in tables:
            print("="*20 + t + "="*20)
            print(pandas.read_sql_query(f"SELECT * FROM {t}", self.conn))
            print('')

    def add_owner(self, discord_id, user):
        sql = "INSERT OR IGNORE INTO owners (id, name) VALUES (?, ?)"
        self.cur.execute(sql, [discord_id, user])

    def get_owner_id(self, name):
        sql = "SELECT id FROM owners WHERE name=?"
        return self.cur.execute(sql, [name]).fetchone()[0]

    def get_display_mode(self, owner_id):
        sql = "SELECT display_mode FROM owners WHERE id=?"
        display_mode = self.cur.execute(sql, [owner_id]).fetchone()[0]
        if display_mode not in DISPLAY_MODES:
            raise ValueError(f"{display_mode} is not a valid display mode. Valid values are {DISPLAY_MODES}")
        return display_mode

    def set_display_mode(self, owner_id, display_mode):
        if display_mode not in DISPLAY_MODES:
            raise ValueError(f"{display_mode} is not a valid display mode. Valid values are {DISPLAY_MODES}")
        sql = "UPDATE owners SET display_mode=? WHERE id=?"
        self.cur.execute(sql, [display_mode, owner_id])

    def add_task(self, task_name, owner_id):
        sql = """
        INSERT INTO tasks (name, owner_id) VALUES (?, ?);
        """
        self.cur.execute(sql, [task_name, owner_id])
        return self.cur.lastrowid

    def add_tasks(self, task_names, owner_id):
        return [self.add_task(t, owner_id) for t in task_names]

    def rename_task(self, task_id, task_name):
        sql = """
        UPDATE tasks SET name = ? WHERE rowid = ?;
        """
        self.cur.execute(sql, [task_name, task_id])

    def filter_task_ids_by_name(self, task_ids, task_name) -> List[int]:
        """
        Takes
        :param task_ids:
        :param task_name: Task name to match against
        :param task_ids: List of task IDs to search through
        :return:
        """
        param_placeholders = ",".join("?" * len(task_ids))
        sql = f"""
        SELECT rowid FROM tasks
        WHERE 
          name LIKE ? AND
          rowid IN ({param_placeholders});
        """
        keyword = f"%{task_name}%"
        response = self.cur.execute(sql, [keyword] + task_ids).fetchall()
        return [x[0] for x in response]

    def get_task_name(self, task_id):
        return self.get_task_names([task_id])[0]

    def get_task_names(self, task_ids: Iterable):
        """
        :param task_ids: List of ids
        :return: List of str
        """
        sql = "SELECT name FROM tasks WHERE rowid = ?"
        response = []
        for task_id in task_ids:
            name = self.cur.execute(sql, [task_id]).fetchone()
            response.append(name[0])
        return response

    def get_task_state(self, task_id):
        return self.get_task_states([task_id])[0]

    def get_task_states(self, task_ids: Iterable):
        """
        :param task_ids: List of ids
        :return: List of str
        """
        sql = "SELECT state FROM tasks WHERE rowid = ?"
        response = []
        for task_id in task_ids:
            name = self.cur.execute(sql, [task_id]).fetchone()
            response.append(name[0])
        return response

    def get_tasks(self, task_ids: Iterable):
        """
        :param task_ids: List of ids
        :return: List of lists
        """
        sql = f"SELECT * FROM tasks WHERE rowid = ?"
        response = []
        for task_id in task_ids:
            task = self.cur.execute(sql, [task_id]).fetchone()
            response.append(task)
        column_names = [d[0] for d in self.cur.description]
        return [dict(zip(column_names, row)) for row in response]

    def start_task(self, task_id):
        sql = """
        UPDATE tasks
        SET 
            state = 'STARTED',
            started_ts = CURRENT_TIMESTAMP
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

    def stop_task(self, task_id):
        sql = """
        UPDATE tasks
        SET 
            state = 'NOT_STARTED',
            started_ts = NULL,
            time_spent_sec = time_spent_sec + 
                COALESCE((julianday(CURRENT_TIMESTAMP) - julianday(started_ts)) * 86400.0, 0)
        WHERE 
          rowid = ?;
        """
        self.cur.execute(sql, [task_id])

    def get_time_spent_sec(self, task_id):
        return self.get_time_spent_secs([task_id])[0]

    def get_time_spent_secs(self, task_ids: Iterable):
        """
        :param task_ids: List of ids
        :return: List of str
        """
        sql = "SELECT CAST(ROUND(time_spent_sec) AS INTEGER) FROM tasks WHERE rowid = ?"
        response = []
        for task_id in task_ids:
            time_spent_sec = self.cur.execute(sql, [task_id]).fetchone()
            response.append(time_spent_sec[0])
        return response

    def complete_task(self, task_id):
        sql = """
        UPDATE tasks
        SET 
            state = 'CHECKED',
            completed_ts = CURRENT_TIMESTAMP,
            time_spent_sec = time_spent_sec + 
                COALESCE((julianday(CURRENT_TIMESTAMP) - julianday(started_ts)) * 86400.0, 0)
        WHERE 
          rowid = ?;
        """
        self.cur.execute(sql, [task_id])

    def uncomplete_task(self, task_id):
        sql = """
        UPDATE tasks
        SET 
            state = 'NOT_STARTED',
            started_ts = NULL,
            completed_ts = NULL
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
          created_ts = CURRENT_TIMESTAMP,
          updated_ts = CURRENT_TIMESTAMP
        WHERE
          owner_id = ? 
        """
        self.cur.execute(sql, [json_list, owner_id])

    def get_list(self, owner_id):
        sql = "SELECT items, owner_id, created_ts, updated_ts FROM lists WHERE owner_id = ?"
        response = list(self.cur.execute(sql, [owner_id]).fetchone())
        response[0] = loads(response[0])
        return response

    def get_list_items(self, owner_id) -> Optional[List[int]]:
        sql = "SELECT items FROM lists WHERE owner_id = ?"
        response = self.cur.execute(sql, [owner_id]).fetchone()
        if response is None:
            return None
        return loads(response[0])

    def update_list_items(self, list_items, owner_id):
        sql = """
        UPDATE lists 
        SET
          items = ?,
          updated_ts = CURRENT_TIMESTAMP
        WHERE
          owner_id = ? 
        """
        json_list = dumps(list_items)
        self.cur.execute(sql, [json_list, owner_id])

    def get_last_message_id(self, owner_id, channel_id):
        sql = "SELECT last_messages FROM lists WHERE owner_id=?"
        last_messages = loads(self.cur.execute(sql, [owner_id]).fetchone()[0])
        return last_messages.get(str(channel_id))

    def set_last_message_id(self, owner_id, channel_id, message_id):
        sql = "SELECT last_messages FROM lists WHERE owner_id=?"
        last_messages = loads(self.cur.execute(sql, [owner_id]).fetchone()[0])
        last_messages[str(channel_id)] = message_id
        sql = "UPDATE lists SET last_messages=? WHERE owner_id=?"
        self.cur.execute(sql, [dumps(last_messages), owner_id])


if __name__ == "__main__":
    with Db(filename=r"..\..\database_files\list-keeper.db") as db:
        db.print_tables()
