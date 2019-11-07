import sqlite3

db = sqlite3.connect("list-keeper.db")
cur = db.cursor()

cur.execute("""
    DROP TABLE IF EXISTS users;
""")
print(cur.fetchall())

cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        name TEXT NOT NULL, 
        creation_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
print(cur.fetchall())

print(cur.execute("select sql from sqlite_master where type = 'table' and name = 'users';").fetchone()[0])
