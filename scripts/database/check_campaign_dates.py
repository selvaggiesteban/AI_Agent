import sqlite3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

conn = sqlite3.connect('C:\\Users\\Esteban Selvaggi\\Desktop\\subagent-driven_development\\data\\inputs\\contacts.db')
c = conn.cursor()

c.execute('SELECT DISTINCT date FROM campaign ORDER BY date DESC LIMIT 20')
rows = c.fetchall()

with open('campaign_dates.txt', 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(str(r[0]) + '\n')

conn.close()
print("Done")