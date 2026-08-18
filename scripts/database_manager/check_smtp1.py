import sqlite3

conn = sqlite3.connect('C:\\Users\\Esteban Selvaggi\\Desktop\\subagent-driven_development\\data\\inputs\\contacts.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM lead l JOIN contact ct ON l.rowid=ct.rowid WHERE l.primary_email IS NOT NULL AND l.primary_email != "" AND ct.deliverability="valid" AND ct.smtp_processed = "1"')
print(f'smtp_processed=1 total: {c.fetchone()[0]}')

conn.close()