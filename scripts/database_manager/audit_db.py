import sqlite3
from core.paths import INPUTS_DIR

DB_PATH = INPUTS_DIR / "contacts.db"

def audit_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- AUDITORÍA GENERAL DE BASE DE DATOS ---")
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM main")
    print(f"Total de registros en DB: {cursor.fetchone()[0]}")
    
    # Registros contactados (campaigns no es nulo)
    cursor.execute("SELECT COUNT(*) FROM main WHERE campaigns IS NOT NULL")
    print(f"Total contactados (alguna vez): {cursor.fetchone()[0]}")
    
    # Registros con emails secundarios
    cursor.execute("SELECT COUNT(*) FROM main WHERE other_emails IS NOT NULL AND other_emails != ''")
    print(f"Total con emails secundarios: {cursor.fetchone()[0]}")
    
    # Registros contactados Y con emails secundarios
    cursor.execute("SELECT COUNT(*) FROM main WHERE campaigns IS NOT NULL AND other_emails IS NOT NULL AND other_emails != ''")
    print(f"Contactados con emails secundarios: {cursor.fetchone()[0]}")
    
    # Desglose por país de los contactados con secundarios
    cursor.execute("""
        SELECT country, COUNT(*) 
        FROM main 
        WHERE campaigns IS NOT NULL 
        AND other_emails IS NOT NULL AND other_emails != ''
        GROUP BY country
    """)
    print("\nDesglose por País (Contactados con Secundarios):")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
        
    # Desglose por sector (top 10) de los contactados con secundarios
    cursor.execute("""
        SELECT sector, COUNT(*) 
        FROM main 
        WHERE campaigns IS NOT NULL 
        AND other_emails IS NOT NULL AND other_emails != ''
        GROUP BY sector
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)
    print("\nTop 10 Sectores (Contactados con Secundarios):")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()

if __name__ == "__main__":
    audit_db()
