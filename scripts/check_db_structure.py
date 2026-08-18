import sqlite3

DB = "data/inputs/contacts.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

# Schema
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", [r[0] for r in c.fetchall()])

# Main columns
c.execute("PRAGMA table_info(main)")
print("\nmain columns:", [(r[1], r[2]) for r in c.fetchall()])

# Lead columns
c.execute("PRAGMA table_info(lead)")
print("\nlead columns:", [(r[1], r[2]) for r in c.fetchall()])

# Join check
c.execute("""
    SELECT m.rowid, m.title, m.city, m.province, m.country, l.primary_email 
    FROM main m 
    INNER JOIN lead l ON m.rowid = l.rowid 
    WHERE l.primary_email IS NOT NULL AND m.city LIKE '%Lan%' 
    LIMIT 5
""")
print("\nLanus contacts sample:")
for r in c.fetchall():
    print(f"  rowid={r[0]}, title={r[1]}, city={r[2]}, prov={r[3]}, country={r[4]}, email={r[5]}")

# Count Lanus
c.execute("""
    SELECT COUNT(*) FROM main m 
    INNER JOIN lead l ON m.rowid = l.rowid 
    WHERE l.primary_email IS NOT NULL AND m.city LIKE '%Lan%'
""")
print(f"\nLanus total: {c.fetchone()[0]}")

# Count valid deliverability
c.execute("""
    SELECT COUNT(*) FROM contact WHERE deliverability='valid'
""")
print(f"Valid deliverability: {c.fetchone()[0]}")

# All countries with counts
c.execute("""
    SELECT m.country, COUNT(*) as cnt FROM main m 
    INNER JOIN lead l ON m.rowid = l.rowid 
    WHERE l.primary_email IS NOT NULL 
    GROUP BY m.country ORDER BY cnt DESC LIMIT 15
""")
print("\nTop countries:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

conn.close()
