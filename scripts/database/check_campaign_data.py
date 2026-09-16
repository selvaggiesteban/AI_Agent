import sqlite3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

conn = sqlite3.connect('C:\\Users\\Esteban Selvaggi\\Desktop\\subagent-driven_development\\data\\inputs\\contacts.db')
c = conn.cursor()

c.execute('SELECT * FROM campaign LIMIT 10')
rows = c.fetchall()
for r in rows:
    print(r)

conn.close()