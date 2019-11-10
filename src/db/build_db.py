import os
import sqlite3


def open_db():
    os.makedirs("../../database_files/", exist_ok=True)
    db = sqlite3.connect("../../database_files/list-keeper.db")
    cur = db.cursor()
    return db, cur


def get_version(cur):
    sql = "SELECT version FROM version"
    try:
        version = cur.execute(sql).fetchone()[0]
    except sqlite3.OperationalError:
        return 0
    else:
        return version


def set_version(cur, v):
    sql = "UPDATE version SET version = ?"
    cur.execute(sql, [v])
    print(f"Set version to {v}")


def drop_tables(cur):
    print("Dropping all tables in database...")

    sql = """
        DROP TABLE IF EXISTS version;
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS tasks;
        DROP TABLE IF EXISTS lists;
    """
    cur.executescript(sql)


def create_tables(cur):
    if get_version(cur) >= 1:
        print("Skipping creating tables...")
        return

    print("Creating tables...")

    # Create version table and initialize with 0
    sql = """
    CREATE TABLE IF NOT EXISTS version (
        version INTEGER PRIMARY KEY
    );
    INSERT INTO version (version) VALUES (0);
    """
    cur.executescript(sql)

    sql = """
    CREATE TABLE IF NOT EXISTS owners (
        id INTEGER PRIMARY KEY, 
        name TEXT NOT NULL, 
        created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS tasks (
        name TEXT NOT NULL, 
        owner_id INTEGER NOT NULL,
        state TEXT NOT NULL DEFAULT NOT_STARTED,
        created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        started_ts TIMESTAMP DEFAULT NULL,
        completed_ts TIMESTAMP DEFAULT NULL,
        time_spent_sec INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS lists (
        items TEXT NOT NULL,
        owner_id INTEGER NOT NULL UNIQUE,
        created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cur.executescript(sql)

    set_version(cur, 1)


if __name__ == "__main__":
    db, cur = open_db()
    # drop_tables(cur)
    create_tables(cur)
    db.commit()
    db.close()
