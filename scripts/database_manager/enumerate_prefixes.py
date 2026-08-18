import csv
from collections import Counter
import re
import os

def enumerate_prefixes():
    # Ruta corregida basada en la búsqueda
    file_path = r"C:\Users\Esteban Selvaggi\Downloads\Contactos\contactos_google\contacts.csv"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} no existe.")
        return

    generic_set = {
        'info', 'ventas', 'admin', 'contact', 'contacto', 'hola', 'comercial', 
        'soporte', 'support', 'mail', 'office', 'webmaster', 'newsletter',
        'marketing', 'recepcion', 'facturacion', 'billing', 'press', 'prensa',
        'ventas1', 'ventas2', 'administracion', 'ventas3', 'info1', 'gerencia'
    }

    prefixes = []
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('E-mail 1 - Value', '').strip()
            if email and '@' in email:
                prefix = email.split('@')[0].lower()
                prefixes.append(prefix)

    counts = Counter(prefixes)
    
    print("--- RESUMEN DE PREFIJOS ENCONTRADOS ---")
    print(f"Total de correos con prefijo: {len(prefixes)}")
    print(f"Prefijos únicos: {len(counts)}")
    
    print("\n--- TOP 15 PREFIJOS GENÉRICOS (Departamentos/Empresas) ---")
    generic_found = {p: c for p, c in counts.items() if p in generic_set}
    for p, c in sorted(generic_found.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"{p:<20} | {c} ocurrencias")

    print("\n--- TOP 15 PREFIJOS POTENCIALES NOMBRES (Individuos) ---")
    individual_found = {p: c for p, c in counts.items() if p not in generic_set and len(p) > 2}
    for p, c in sorted(individual_found.items(), key=lambda x: x[1], reverse=True)[:15]:
        # Mostrar solo si tiene estructura de nombre (letras y puntos/guiones)
        if re.match(r'^[a-z\.\-_]+$', p):
            print(f"{p:<20} | {c} ocurrencias")

if __name__ == "__main__":
    enumerate_prefixes()
