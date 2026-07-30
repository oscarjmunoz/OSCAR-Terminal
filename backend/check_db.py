import sqlite3

conn = sqlite3.connect(r"D:\OSCAR-Terminal\database\oscar.db")

cursor = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table';"
)

print(cursor.fetchall())

conn.close()