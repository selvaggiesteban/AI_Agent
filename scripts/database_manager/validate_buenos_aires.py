"""
Valida emails de Buenos Aires que tienen deliverability='invalid'.
Verifica sintaxis y registros DNS/MX del dominio.
Actualiza contacts.db con nuevos resultados.
"""

import sqlite3
import re
import dns.resolver
import sys
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = "data/inputs/contacts.db"

def is_valid_syntax(email):
    """Verifica sintaxis básica del email."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def has_mx_records(domain):
    """Verifica si el dominio tiene registros MX."""
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return len(answers) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, Exception):
        return False

def has_a_records(domain):
    """Verifica si el dominio tiene registros A (fallback si no tiene MX)."""
    try:
        answers = dns.resolver.resolve(domain, 'A')
        return len(answers) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, Exception):
        return False

def validate_email(email):
    """Valida un email completo: sintaxis + DNS."""
    result = {
        'email': email,
        'syntax_valid': False,
        'domain_exists': False,
        'mx_records': False,
        'deliverability': 'invalid'
    }
    
    # Check syntax
    if not is_valid_syntax(email):
        return result
    
    result['syntax_valid'] = True
    
    # Extract domain
    domain = email.split('@')[1]
    
    # Check if domain exists (MX or A records)
    if has_mx_records(domain):
        result['domain_exists'] = True
        result['mx_records'] = True
        result['deliverability'] = 'valid'
    elif has_a_records(domain):
        result['domain_exists'] = True
        result['deliverability'] = 'valid'
    
    return result

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all AR Buenos Aires invalid contacts
    cursor.execute('''
        SELECT 
            m.rowid,
            l.primary_email,
            c.deliverability
        FROM main m
        LEFT JOIN lead l ON m.rowid = l.rowid
        LEFT JOIN contact c ON m.rowid = c.rowid
        WHERE m.country = 'AR'
          AND (m.province LIKE '%Buenos%' OR m.city LIKE '%Buenos%')
          AND l.primary_email IS NOT NULL
          AND l.primary_email != ''
          AND c.deliverability = 'invalid'
          AND NOT EXISTS (
              SELECT 1 
              FROM campaign camp 
              WHERE camp.contact_rowid = m.rowid
          )
    ''')
    
    contacts = cursor.fetchall()
    print(f'Total contactos a validar: {len(contacts)}')
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated = 0
    valid_count = 0
    invalid_count = 0
    error_count = 0
    
    for i, (rowid, email, old_deliverability) in enumerate(contacts):
        if not email:
            continue
        
        # Clean email (take first one if multiple)
        email = email.strip().lower().split(',')[0].split('/')[0].strip()
        
        # Skip obviously invalid emails
        if not email or '@' not in email or len(email) < 5:
            error_count += 1
            continue
        
        try:
            result = validate_email(email)
            
            if result['deliverability'] != old_deliverability:
                cursor.execute('''
                    UPDATE contact 
                    SET deliverability = ?, last_validation_date = ?
                    WHERE rowid = ?
                ''', (result['deliverability'], now, rowid))
                updated += 1
            
            if result['deliverability'] == 'valid':
                valid_count += 1
            else:
                invalid_count += 1
            
            if (i + 1) % 50 == 0:
                print(f'  Procesados {i+1}/{len(contacts)}: {valid_count} valid, {invalid_count} invalid')
                conn.commit()
        
        except Exception as e:
            error_count += 1
            continue
    
    conn.commit()
    
    print(f'\n--- RESULTADO ---')
    print(f'Total procesados: {len(contacts)}')
    print(f'Actualizados: {updated}')
    print(f'Valid: {valid_count}')
    print(f'Invalid: {invalid_count}')
    print(f'Errores: {error_count}')
    
    # Verify new counts
    cursor.execute('''
        SELECT COUNT(*)
        FROM main m
        LEFT JOIN lead l ON m.rowid = l.rowid
        LEFT JOIN contact c ON m.rowid = c.rowid
        WHERE m.country = 'AR'
          AND (m.province LIKE '%Buenos%' OR m.city LIKE '%Buenos%')
          AND l.primary_email IS NOT NULL
          AND l.primary_email != ''
          AND c.deliverability = 'valid'
          AND NOT EXISTS (
              SELECT 1 
              FROM campaign camp 
              WHERE camp.contact_rowid = m.rowid
          )
    ''')
    new_valid = cursor.fetchone()[0]
    print(f'\nNuevos contactos válidos Buenos Aires: {new_valid}')
    
    conn.close()
    return updated, valid_count

if __name__ == "__main__":
    print("=== Validación emails Buenos Aires ===\n")
    updated, valid = main()
    print(f"\n=== COMPLETADO: {updated} actualizados, {valid} válidos ===")
