import sqlite3

conn = sqlite3.connect('C:\\Users\\Esteban Selvaggi\\Desktop\\subagent-driven_development\\data\\inputs\\contacts.db')
c = conn.cursor()

# Contactos con smtp_processed=0 que están en campaign table con fechas agosto 2026
c.execute('''
    SELECT COUNT(DISTINCT cp.contact_rowid) 
    FROM campaign cp
    JOIN contact ct ON cp.contact_rowid = ct.ROWID
    WHERE (ct.smtp_processed IS NULL OR ct.smtp_processed = "0")
    AND (cp.date LIKE "2026-08-%" OR cp.date LIKE "06/08/2026%" OR cp.date LIKE "05/08/2026%" OR cp.date LIKE "07/08/2026%" OR cp.date LIKE "1 Jun 2026%")
''')
print(f'smtp_processed=0 contactados semana 3-7 ago: {c.fetchone()[0]}')

# Total smtp_processed=0
c.execute('SELECT COUNT(*) FROM lead l JOIN contact ct ON l.rowid=ct.rowid WHERE l.primary_email IS NOT NULL AND ct.deliverability="valid" AND (ct.smtp_processed IS NULL OR ct.smtp_processed="0")')
print(f'Total smtp_processed=0: {c.fetchone()[0]}')

# smtp_processed=0 NO en campaign reciente
c.execute('''
    SELECT COUNT(*) FROM lead l
    JOIN contact ct ON l.rowid = ct.rowid
    LEFT JOIN campaign cp ON l.rowid = cp.contact_rowid
        AND (cp.date LIKE "2026-08-%" OR cp.date LIKE "06/08/2026%" OR cp.date LIKE "05/08/2026%" OR cp.date LIKE "07/08/2026%" OR cp.date LIKE "1 Jun 2026%")
    WHERE l.primary_email IS NOT NULL
    AND ct.deliverability = "valid"
    AND (ct.smtp_processed IS NULL OR ct.smtp_processed = "0")
    AND cp.contact_rowid IS NULL
''')
print(f'smtp_processed=0 NO contactados semana 3-7 ago: {c.fetchone()[0]}')

conn.close()