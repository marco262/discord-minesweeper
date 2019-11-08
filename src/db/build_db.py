import os
import sqlite3

os.makedirs("../../database_files/", exist_ok=True)
db = sqlite3.connect("../../database_files/list-keeper.db")
cur = db.cursor()

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
    created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_ts TIMESTAMP DEFAULT NULL,
    completed_ts TIMESTAMP DEFAULT NULL
);
"""
print(cur.execute(sql).fetchall())

sql = """
CREATE TABLE IF NOT EXISTS lists (
    items TEXT NOT NULL,
    owner_id INTEGER NOT NULL UNIQUE,
    created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
print(cur.execute(sql).fetchall())


print(cur.execute("select sql from sqlite_master where type = 'table' and name = 'owners';").fetchone()[0])
print(cur.execute("select sql from sqlite_master where type = 'table' and name = 'tasks';").fetchone()[0])
print(cur.execute("select sql from sqlite_master where type = 'table' and name = 'lists';").fetchone()[0])
