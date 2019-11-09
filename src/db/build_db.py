import os
import sqlite3


def open_db():
    os.makedirs("../../database_files/", exist_ok=True)
    db = sqlite3.connect("../../database_files/list-keeper.db")
    cur = db.cursor()
    return db, cur


def drop_tables(cur):
    sql = """
    DROP TABLE IF EXISTS users;
    """
    print(cur.execute(sql).fetchall())

    sql = """
    DROP TABLE IF EXISTS tasks;
    """
    print(cur.execute(sql).fetchall())

    sql = """
    DROP TABLE IF EXISTS lists;
    """
    print(cur.execute(sql).fetchall())


def create_tables(cur):
    sql = """
    CREATE TABLE IF NOT EXISTS owners (
        id INTEGER PRIMARY KEY, 
        name TEXT NOT NULL, 
        created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    print(cur.execute(sql).fetchall())

    sql = """
    CREATE TABLE IF NOT EXISTS tasks (
        name TEXT NOT NULL, 
        owner_id INTEGER NOT NULL,
        state TEXT NOT NULL DEFAULT NOT_STARTED,
        created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        started_ts TIMESTAMP DEFAULT NULL,
        completed_ts TIMESTAMP DEFAULT NULL,
        time_spent_sec INTEGER DEFAULT 0
    );
    """
    print(cur.execute(sql).fetchall())

    sql = """
    CREATE TABLE IF NOT EXISTS lists (
        items TEXT NOT NULL,
        owner_id INTEGER NOT NULL UNIQUE,
        created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    print(cur.execute(sql).fetchall())

    print(cur.execute("select sql from sqlite_master where type = 'table' and name = 'owners';").fetchone()[0])
    print(cur.execute("select sql from sqlite_master where type = 'table' and name = 'tasks';").fetchone()[0])
    print(cur.execute("select sql from sqlite_master where type = 'table' and name = 'lists';").fetchone()[0])


if __name__ == "__main__":
    db, cur = open_db()
    drop_tables(cur)
    create_tables(cur)
    db.commit()
    db.close()
