import sqlite3
from flask_bcrypt import Bcrypt
from flask import Flask

app = Flask(__name__)
bcrypt = Bcrypt(app)

con = sqlite3.connect('store.db')
cur = con.cursor()
cur.execute('SELECT id FROM users WHERE email = ?', ('admin@shop.com',))
if cur.fetchone():
    print('admin already exists')
else:
    password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
    cur.execute('INSERT INTO users (name, email, password_hash, is_admin) VALUES (?, ?, ?, ?)', ('Admin Shop', 'admin@shop.com', password_hash, 1))
    con.commit()
    print('admin created')
con.close()
