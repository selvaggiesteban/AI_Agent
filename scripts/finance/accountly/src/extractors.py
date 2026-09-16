import pdfplumber
import re
import os
from datetime import datetime

def parse_money(text):
    """Convierte texto de moneda ($ 1.234,56 o 1.234,56) a float."""
    if not text: return 0.0
    clean = text.replace('$', '').replace(' ', '')
    clean = clean.replace('.', '').replace(',', '.')
    if clean.endswith('-'):
        clean = '-' + clean[:-1]
    try:
        return float(clean)
    except ValueError:
        return 0.0

def process_arca_files(directory):
    data = []
    print(f"Procesando ARCA en: {directory}")
    if not os.path.exists(directory): return []

    files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    for filename in files:
        path = os.path.join(directory, filename)
        try:
            with pdfplumber.open(path) as pdf:
                text = ""
                for page in pdf.pages: text += (page.extract_text() or "") + "\n"
                
                date_match = re.search(r'Fecha de Emisión:\s*(\d{2}/\d{2}/\d{4})', text)
                amount_match = re.search(r'Importe Total:\s*\$\s*([\d\.,]+)', text)
                
                # Extracción de Receptor (CUIT/Nombre)
                # Busca CUIT Receptor: XX-XXXXXXXX-X
                recipient_cuit = re.search(r'CUIT:\s*(\d{2}-\d{8}-\d)', text)
                # Busca Nombre Receptor (A veces es difícil por el formato variable, intentamos una aprox)
                recipient_name = re.search(r'Apellido y Nombre / Razón Social:\s*(.+)', text)
                
                if date_match and amount_match:
                    date = datetime.strptime(date_match.group(1), '%d/%m/%Y')
                    amount = parse_money(amount_match.group(1))
                    is_nc = "NOTA DE CRÉDITO" in text.upper() or "_013_" in filename
                    if is_nc: amount = -abs(amount)
                    
                    data.append({
                        'date': date,
                        'month_key': date.strftime('%Y-%m'),
                        'description': f"ARCA {'NC' if is_nc else 'FC'} {filename}",
                        'amount': amount,
                        'source': 'ARCA',
                        'recipient_cuit': recipient_cuit.group(1) if recipient_cuit else None,
                        'recipient_name': recipient_name.group(1).strip() if recipient_name else None
                    })
        except Exception as e:
            print(f"Error ARCA {filename}: {e}")
    return data

def process_santander(directory):
    movements = []
    print(f"Procesando Santander (Multilínea) en: {directory}")
    if not os.path.exists(directory): return []

    files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    for filename in files:
        path = os.path.join(directory, filename)
        try:
            with pdfplumber.open(path) as pdf:
                # State for section filtering
                # Default to True to handle files that are just movement extracts.
                capturing = True 
                
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    lines = text.split('\n')
                    
                    current_tx = None
                    
                    for line in lines:
                        clean_line = line.strip()
                        
                        # --- Section Detection ---
                        # Start of Bank Account Section
                        if "Movimientos en pesos" in clean_line or "Movimientos en dólares" in clean_line:
                            capturing = True
                            continue
                        
                        # Start of Credit Card Section (Stop capturing)
                        if any(header in clean_line for header in ["Tarjeta Santander", "Consumos del mes", "Tarjeta de débito", "Tarjeta de crédito"]):
                            capturing = False
                            continue
                            
                        if not capturing:
                            continue

                        # --- Informative Lines Filter ---
                        if "Saldo Inicial" in clean_line:
                            continue

                        # --- Transaction Parsing ---
                        # Regex para detectar fecha al inicio: 17/09/24 ...
                        date_match = re.match(r'^(\d{2}/\d{2}/\d{2})\s+(.*)', line)
                        
                        if date_match:
                            # Si ya veníamos trayendo una, la guardamos antes de empezar la nueva
                            if current_tx:
                                movements.append(finalize_santander_tx(current_tx))
                            
                            # Iniciamos nueva tx
                            raw_date, text_part = date_match.groups()
                            day, month, year = raw_date.split('/')
                            try:
                                date_obj = datetime.strptime(f"{day}/{month}/20{year}", "%d/%m/%Y")
                                current_tx = {
                                    'date': date_obj,
                                    'desc_parts': [],
                                    'amount': None
                                }
                                # Analizar si esta misma línea ya tiene montos
                                parse_santander_line(line, text_part, current_tx)
                            except:
                                current_tx = None
                        
                        elif current_tx:
                            # Es una línea de continuación (detalle del remitente, etc)
                            # A veces Santander repite la fecha o pone basura, intentamos limpiar
                            parse_santander_line(line, line, current_tx)

                    # Al final de la página, guardar la última pendiente
                    if current_tx:
                        movements.append(finalize_santander_tx(current_tx))

        except Exception as e:
            print(f"Error Santander {filename}: {e}")
            
    return movements

def parse_santander_line(full_line, text_content, tx_obj):
    """Analiza una línea para buscar montos y texto."""
    
    # 1. Limpiar la fecha del inicio para que no confunda al buscador de números
    # Formato dd/mm/yy (8 chars) + espacios
    clean_line = re.sub(r'^\d{2}/\d{2}/\d{2}', '', full_line).strip()
    
    # 2. Buscar montos que TENGAN signo $ explícito primero
    # Esto filtra números de comprobante (ej: 253622) o cuits
    money_matches = re.findall(r'(-?\$\s?[\d\.,]+)', clean_line)
    
    # Si no encuentra con $, busca genéricos (riesgoso, pero fallback)
    if not money_matches:
        money_matches = re.findall(r'(-?[\d\.,]+)', clean_line)

    clean_text = text_content.strip()
    
    # Limpiar el texto descriptivo quitando los montos encontrados
    for amt in money_matches:
        clean_text = clean_text.replace(amt, "").strip()
        
    # Asignar monto si no tiene
    if tx_obj['amount'] is None and money_matches:
        # Prioridad: El primer monto con '$' suele ser el movimiento en Santander
        # (Columna Movimiento viene antes de Columna Saldo)
        for m in money_matches:
            if '$' in m:
                try:
                    val = parse_money(m)
                    # Evitar saldos en 0.00 o valores nulos si hay otros mejores
                    if val != 0 or len(money_matches) == 1:
                        tx_obj['amount'] = val
                        break
                except: continue
        
        # Si falló lo anterior, intentar con el primero numérico puro
        if tx_obj['amount'] is None:
             try:
                tx_obj['amount'] = parse_money(money_matches[0])
             except: pass

    # Limpieza extra de "basura" numérica que queda en la descripción (IDs, CUITs sueltos al final)
    # Ej: "253622 Pago..." -> Quitar 253622
    clean_text = re.sub(r'^\d{6,}\s+', '', clean_text)
    
    if clean_text:
        tx_obj['desc_parts'].append(clean_text)

def finalize_santander_tx(tx):
    return {
        'date': tx['date'],
        'month_key': tx['date'].strftime('%Y-%m'),
        'description': " ".join(tx['desc_parts']),
        'amount': tx['amount'] if tx['amount'] is not None else 0.0,
        'source': 'Santander'
    }

def process_mercadopago(directory):
    movements = []
    print(f"Procesando MP en: {directory}")
    if not os.path.exists(directory): return []

    files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    for filename in files:
        path = os.path.join(directory, filename)
        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    lines = (page.extract_text() or "").split('\n')
                    
                    # Iterar con índice para poder mirar adelante
                    i = 0
                    while i < len(lines):
                        line = lines[i]
                        
                        # --- SKIP FILTER ---
                        if "Pago cancelado" in line:
                            i += 1
                            continue

                        match_date = re.match(r'^(\d{2}-\d{2}-\d{4})', line)
                        match_amount = re.search(r'(-?\$?\s?[\d\.,]+)\s+(-?\$?\s?[\d\.,]+)$', line)
                        
                        if match_date and match_amount:
                            try:
                                date_obj = datetime.strptime(match_date.group(1), "%d-%m-%Y")
                                amount = parse_money(match_amount.group(1))
                                
                                # Extraer descripción base de la línea 1 (quitando fecha y montos)
                                desc = line[len(match_date.group(1)):].replace(match_amount.group(0), "").strip()
                                # Limpiar IDs numéricos iniciales (ej: 139277...)
                                desc = re.sub(r'^\s*\d+\s+', '', desc)
                                
                                # --- LÓGICA MULTILÍNEA ---
                                # Mirar la siguiente línea para ver si es continuación (nombre del remitente)
                                if i + 1 < len(lines):
                                    next_line = lines[i+1]
                                    # Si la siguiente línea NO tiene fecha al inicio, es parte de esta tx
                                    if not re.match(r'^(\d{2}-\d{2}-\d{4})', next_line):
                                        # Y nos aseguramos que no sea un pie de página o basura
                                        if len(next_line.strip()) > 2 and "Página" not in next_line:
                                            desc += " " + next_line.strip()
                                            # Saltamos esa línea en la próxima iteración
                                            i += 1
                                
                                movements.append({
                                    'date': date_obj,
                                    'month_key': date_obj.strftime('%Y-%m'),
                                    'description': desc,
                                    'amount': amount,
                                    'source': 'MercadoPago'
                                })
                            except Exception as e: 
                                # print(f"Error parsing line MP: {line} -> {e}")
                                pass
                        
                        i += 1 # Avanzar
                        
        except Exception as e:
            print(f"Error MP {filename}: {e}")
            
    return movements

def process_credicoop(directory):
    movements = []
    print(f"Procesando Credicoop en: {directory}")
    if not os.path.exists(directory): return []

    files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    for filename in files:
        path = os.path.join(directory, filename)
        
        # Determinar año base por el nombre del archivo (Del YYYY...)
        file_year = "2020"
        ym = re.search(r'Del (\d{4})', filename)
        if ym: file_year = ym.group(1)

        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    lines = (page.extract_text() or "").split('\n')
                    
                    i = 0
                    while i < len(lines):
                        line = lines[i]
                        # Credicoop: dd/mm Descripcion ... Monto Saldo
                        match = re.match(r'^(\d{2}/\d{2})\s+(.+?)\s+(-?[\d\.,]+)\s+(-?[\d\.,]+)$', line)
                        
                        if match:
                            dm, desc, amt_str, _ = match.groups()
                            
                            # Filtros básicos de líneas de saldo inicial/transporte
                            if "SALDO" in desc.upper() or "TRANSPORTE" in desc.upper(): 
                                i += 1
                                continue
                                
                            try:
                                date_obj = datetime.strptime(f"{dm}/{file_year}", "%d/%m/%Y")
                                desc = desc.strip()
                                
                                # --- LÓGICA MULTILÍNEA ---
                                if i + 1 < len(lines):
                                    next_line = lines[i+1]
                                    # Si la siguiente línea NO tiene fecha al inicio, es continuación
                                    if not re.match(r'^(\d{2}/\d{2})', next_line):
                                        # Evitar pies de página
                                        if len(next_line.strip()) > 2 and "Hoja" not in next_line:
                                            desc += " " + next_line.strip()
                                            i += 1
                                
                                movements.append({
                                    'date': date_obj,
                                    'month_key': date_obj.strftime('%Y-%m'),
                                    'description': desc,
                                    'amount': parse_money(amt_str),
                                    'source': 'Credicoop'
                                })
                            except: pass
                        
                        i += 1
                        
        except Exception as e:
            # print(f"Error Credicoop {filename}: {e}")
            pass
    return movements

def process_western_union(file_path):
    movements = []
    print(f"Procesando Western Union: {file_path}")
    if not os.path.exists(file_path): return []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                rows = page.extract_table()
                if not rows: continue
                
                for row in rows:
                    if not row: continue
                    
                    # Filter out None and empty strings to handle spacing columns
                    clean_row = [x for x in row if x and str(x).strip()]
                    
                    # Expected structure after cleaning:
                    # [MTCN, Receiver, DateSent, Sender, DatePaid, Amount, Origin, Destination]
                    # Example: ['1056196357', 'ESTEBAN SELVAGGI', '12/20/2025', 'AMANDA OSPINA', '12/20/2025', 'ARS 108,010.00', 'UNITED STATES', 'ARGENTINA']
                    
                    if len(clean_row) < 6: continue
                    if clean_row[0] == "MTCN": continue
                    
                    try:
                        mtcn = clean_row[0]
                        sender = clean_row[3]
                        date_str = clean_row[4] # MM/DD/YYYY
                        amount_str = clean_row[5] # ARS 108,010.00
                        
                        # Parse Date
                        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
                        
                        # Parse Amount
                        clean_amt = amount_str.replace("ARS", "").strip().replace(",", "")
                        amount = float(clean_amt)
                        
                        movements.append({
                            'date': date_obj,
                            'month_key': date_obj.strftime('%Y-%m'),
                            'description': f"WU {mtcn} - {sender}",
                            'amount': amount,
                            'source': 'Western Union'
                        })
                    except Exception as e:
                        # print(f"Skipping row WU: {clean_row} -> {e}")
                        pass
                        
    except Exception as e:
        print(f"Error Western Union {file_path}: {e}")
            
    return movements