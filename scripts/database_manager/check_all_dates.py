import sqlite3

conn = sqlite3.connect('C:\\Users\\Esteban Selvaggi\\Desktop\\subagent-driven_development\\data\\inputs\\contacts.db')
c = conn.cursor()

c.execute('SELECT DISTINCT date FROM campaign ORDER BY date DESC')
rows = c.fetchall()

with open('all_dates.txt', 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(str(r[0]) + '\n')

conn.close()
print("Done")