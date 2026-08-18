import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'data/inputs/contacts.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check None country with .ar emails - valid
cursor.execute('''
    SELECT 
        m.rowid,
        m.title,
        m.city,
        m.province,
        l.primary_email,
        c.deliverability
    FROM main m
    LEFT JOIN lead l ON m.rowid = l.rowid
    LEFT JOIN contact c ON m.rowid = c.rowid
    WHERE m.country IS NULL
      AND l.primary_email IS NOT NULL
      AND l.primary_email != ''
      AND l.primary_email LIKE '%.ar%'
      AND c.deliverability = 'valid'
      AND NOT EXISTS (
          SELECT 1 
          FROM campaign camp 
          WHERE camp.contact_rowid = m.rowid
      )
    ORDER BY m.rowid
''')
results = cursor.fetchall()
print(f'None country .ar valid never contacted: {len(results)}')
print('\nFirst 50:')
for r in results[:50]:
    print(f'  RowID: {r[0]} | Email: {r[4][:50] if r[4] else "NULL"} | Nombre: {r[1][:30] if r[1] else "NULL"} | Ciudad: {r[2]}, {r[3]}')

# Check Argentina (with 'Argentina' as country) never contacted valid
cursor.execute('''
    SELECT COUNT(*)
    FROM main m
    LEFT JOIN lead l ON m.rowid = l.rowid
    LEFT JOIN contact c ON m.rowid = c.rowid
    WHERE m.country = 'Argentina'
      AND l.primary_email IS NOT NULL
      AND l.primary_email != ''
      AND c.deliverability = 'valid'
      AND NOT EXISTS (
          SELECT 1 
          FROM campaign camp 
          WHERE camp.contact_rowid = m.rowid
      )
''')
print(f'\nArgentina (country=Argentina) valid never contacted: {cursor.fetchone()[0]}')

# Total AR + Argentina valid never contacted
cursor.execute('''
    SELECT COUNT(*)
    FROM main m
    LEFT JOIN lead l ON m.rowid = l.rowid
    LEFT JOIN contact c ON m.rowid = c.rowid
    WHERE (m.country = 'AR' OR m.country = 'Argentina')
      AND l.primary_email IS NOT NULL
      AND l.primary_email != ''
      AND c.deliverability = 'valid'
      AND NOT EXISTS (
          SELECT 1 
          FROM campaign camp 
          WHERE camp.contact_rowid = m.rowid
      )
''')
print(f'AR + Argentina valid never contacted: {cursor.fetchone()[0]}')

# Add None country .ar emails to the mix
cursor.execute('''
    SELECT COUNT(*)
    FROM main m
    LEFT JOIN lead l ON m.rowid = l.rowid
    LEFT JOIN contact c ON m.rowid = c.rowid
    WHERE (
        (m.country = 'AR' OR m.country = 'Argentina')
        OR (m.country IS NULL AND l.primary_email LIKE '%.ar%')
      )
      AND l.primary_email IS NOT NULL
      AND l.primary_email != ''
      AND c.deliverability = 'valid'
      AND NOT EXISTS (
          SELECT 1 
          FROM campaign camp 
          WHERE camp.contact_rowid = m.rowid
      )
''')
print(f'AR + Argentina + None/.ar valid never contacted: {cursor.fetchone()[0]}')

conn.close()
