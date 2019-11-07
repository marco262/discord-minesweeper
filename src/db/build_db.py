import sqlite3

db = sqlite3.connect("list-keeper.db")
cur = db.cursor()

sql = """
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tasks;
"""
print(cur.execute(sql).fetchall())

sql = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, 
    name TEXT NOT NULL, 
    creation_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
print(cur.execute(sql).fetchall())

sql = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL, 
    creation_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_ts TIMESTAMP DEFAULT NULL,
    completed_ts TIMESTAMP DEFAULT NULL
);
"""
print(cur.execute(sql).fetchall())

# print(cur.execute("select sql from sqlite_master where type = 'table' and name = 'users';").fetchone()[0])
