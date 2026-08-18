import sqlite3

conn = sqlite3.connect('C:\\Users\\Esteban Selvaggi\\Desktop\\subagent-driven_development\\data\\inputs\\contacts.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM lead l JOIN contact ct ON l.rowid=ct.rowid WHERE l.primary_email IS NOT NULL AND l.primary_email != "" AND ct.deliverability = "valid"')
print(f'Total deliverability=valid: {c.fetchone()[0]}')

c.execute('SELECT COUNT(DISTINCT contact_rowid) FROM campaign')
print(f'Contactos en tabla campaign: {c.fetchone()[0]}')

c.execute('''
    SELECT COUNT(*) FROM main m
    JOIN lead l ON m.rowid = l.rowid
    JOIN contact ct ON m.rowid = ct.rowid
    LEFT JOIN campaign cp ON m.rowid = cp.contact_rowid
    WHERE l.primary_email IS NOT NULL AND l.primary_email != ""
    AND ct.deliverability = "valid"
    AND cp.contact_rowid IS NULL
''')
print(f'SIN campaña (LEFT JOIN): {c.fetchone()[0]}')

c.execute('SELECT COUNT(*) FROM lead l JOIN contact ct ON l.rowid=ct.rowid WHERE l.primary_email IS NOT NULL AND ct.deliverability="valid" AND (ct.smtp_processed IS NULL OR ct.smtp_processed="0")')
print(f'smtp_processed=0: {c.fetchone()[0]}')

conn.close()