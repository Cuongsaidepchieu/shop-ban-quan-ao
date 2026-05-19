import sqlite3
import os
path = 'store.db'
print('exists', os.path.exists(path))
con = sqlite3.connect(path)
cur = con.cursor()
try:
    cur.execute('SELECT id, name, email, is_admin FROM users')
    rows = cur.fetchall()
    print(rows)
except Exception as e:
    print('error', e)
finally:
    con.close()
