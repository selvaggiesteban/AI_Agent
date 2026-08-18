import sqlite3

conn = sqlite3.connect('data/inputs/contacts.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM main')
print('Total main:', cursor.fetchone()[0])

cursor.execute('SELECT COUNT(*) FROM lead')
print('Total lead:', cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM contact WHERE deliverability = 'valid'")
print('Valid emails:', cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM contact WHERE smtp_processed = '1' OR smtp_processed = 1")
print('Already SMTP processed:', cursor.fetchone()[0])

cursor.execute("SELECT DISTINCT country FROM main WHERE country IS NOT NULL AND country != '' LIMIT 20")
print('\nCountries:', [r[0] for r in cursor.fetchall()])

cursor.execute("SELECT DISTINCT city FROM main WHERE city IS NOT NULL AND city != '' AND city LIKE '%an%' LIMIT 30")
print('\nLanus-like cities:', [r[0] for r in cursor.fetchall()])

cursor.execute("SELECT DISTINCT province FROM main WHERE province IS NOT NULL AND province != '' LIMIT 20")
print('\nProvinces:', [r[0] for r in cursor.fetchall()])

# Check how tables relate
cursor.execute('SELECT m.id, l.primary_email, m.title, m.city, m.country FROM main m INNER JOIN lead l ON m.rowid = l.rowid LIMIT 3')
print('\nSample joined rows:')
for r in cursor.fetchall():
    print('  ', r)

# Count emails by country
cursor.execute("""
    SELECT m.country, COUNT(l.primary_email) 
    FROM main m 
    INNER JOIN lead l ON m.rowid = l.rowid 
    WHERE l.primary_email IS NOT NULL 
    GROUP BY m.country 
    ORDER BY COUNT(l.primary_email) DESC 
    LIMIT 10
""")
print('\nEmails by country:')
for r in cursor.fetchall():
    print('  ', r)

# Count emails by city containing Lanus
cursor.execute("""
    SELECT m.city, COUNT(l.primary_email)
    FROM main m 
    INNER JOIN lead l ON m.rowid = l.rowid 
    WHERE l.primary_email IS NOT NULL AND m.city LIKE '%Lan%'
    GROUP BY m.city
""")
print('\nEmails in Lanus area:')
for r in cursor.fetchall():
    print('  ', r)

# Entities with valid deliverability
cursor.execute("""
    SELECT COUNT(DISTINCT m.rowid)
    FROM main m 
    INNER JOIN lead l ON m.rowid = l.rowid 
    INNER JOIN contact c ON m.rowid = c.rowid
    WHERE l.primary_email IS NOT NULL AND c.deliverability = 'valid'
""")
print('\nValid deliverability contacts:', cursor.fetchone()[0])

conn.close()
