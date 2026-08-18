from collections import defaultdict
import re
from datetime import datetime

def classify_movement(description, amount, source):
    """
    Clasifica el movimiento basándose en reglas semánticas estrictas.
    Retorna: (Categoría, EsTransferenciaPropia)
    """
    desc_upper = description.upper()
    
    # 1. Detectar Transferencia Propia
    is_own_transfer = False
    own_keywords = ['SELVAGGI', 'ESTEBAN', 'MISMO TITULAR', 'PROPIA', '20433102593']
    if any(k in desc_upper for k in own_keywords):
        is_own_transfer = True

    category = 'Otro'
    
    if amount > 0:
        # --- INGRESOS ---
        category = 'Ingreso (Transf. Propia)' if is_own_transfer else 'Ingreso (Ventas/Terceros)'
    else:
        # --- EGRESOS ---
        # Lógica estricta para diferenciar Gasto vs Pago de Deuda
        
        # Caso A: Pago del resumen de la tarjeta (Deuda)
        # Santander suele poner: "PAGO TARJETA DE CREDITO" o "PAGO DE TARJETA"
        if "PAGO" in desc_upper and "TARJETA" in desc_upper and "DEBITO" not in desc_upper:
             category = 'Pago Tarjeta / Crédito'
        elif "PAGO" in desc_upper and ("VISA" in desc_upper or "MASTER" in desc_upper or "AMEX" in desc_upper) and "DEBITO" not in desc_upper:
             category = 'Pago Tarjeta / Crédito'
             
        # Caso B: Consumo con débito o gasto directo (Gasto Corriente)
        # Ej: "COMPRA CON TARJETA DE DEBITO", "DEBITO AUTOMATICO"
        else:
             category = 'Egreso (Gasto)'

    return category, is_own_transfer

def normalize_concept_text(text):
    """Limpia el nombre para la visualización, pero retiene la esencia."""
    if not text: return "DESCONOCIDO"
    clean = text.upper().strip()
    
    # Prefijos que indican el TIPO de transacción (útiles para lógica, ruidosos para agrupación visual)
    prefixes = [
        "COMPRA CON TARJETA DE DEBITO", "DEBITO AUTOMATICO", "DEBITO DIRECTO", 
        "COMPRA", "PAGO", "DEBITO", "CONSUMO", "TRANSFERENCIA REALIZADA"
    ]
    
    # Eliminar prefijos del nombre visual
    for p in prefixes:
        clean = clean.replace(p, "")
    
    # Limpieza de basura técnica
    clean = clean.replace("S.A.", "").replace("S.R.L.", "").replace("SRL", "").replace("SA", "")
    clean = clean.replace(".COM.AR", "").replace(".COM", "").replace(".NET", "")
    
    # Quitar IDs numéricos largos
    clean = re.sub(r'\d{6,}', '', clean) 
    clean = clean.strip()
    
    # Separar Pasarelas (MP, DLO, etc)
    parts = re.split(r'[\*\-]', clean)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts: return "OTROS"
    
    candidate = parts[0]
    aggregators = ["MERCADOPAGO", "MERPAGO", "MP", "PAYU", "PAGOS360", "DLO", "FISERV", "DEBIN", "CREDIN"]
    
    # Si el primero es un agregador, tomamos el segundo como el comercio real
    if len(parts) > 1 and any(agg in candidate for agg in aggregators):
        candidate = parts[1]

    # Diccionario Canónico (Mapeo estricto)
    canonical_rules = {
        "NETFLIX": "NETFLIX", "SPOTIFY": "SPOTIFY", "YOUTUBE": "YOUTUBE",
        "UBER": "UBER", "DID": "DIDI", "CABIFY": "CABIFY",
        "PEDIDOS": "PEDIDOSYA", "RAPPI": "RAPPI",
        "CARREFOUR": "CARREFOUR", "COTO": "COTO", "DIA ": "DIA", "VEA": "VEA", "DISCO": "DISCO", "JUMBO": "JUMBO",
        "FARMACITY": "FARMACITY", "OPENFARMA": "OPENFARMA",
        "MC DONALD": "MCDONALDS", "MCDONALD": "MCDONALDS", "BURGER": "BURGER KING", "MOSTAZA": "MOSTAZA", "STARBUCKS": "STARBUCKS",
        "SHELL": "SHELL", "YPF": "YPF", "AXION": "AXION",
        "TELECENTRO": "TELECENTRO", "PERSONAL": "PERSONAL", "MOVISTAR": "MOVISTAR", "CLARO": "CLARO",
        "EDESUR": "EDESUR", "METROGAS": "METROGAS", "AYSA": "AYSA",
        "AFIP": "IMPUESTOS AFIP", "MONOTRIBUTO": "MONOTRIBUTO", "ARBA": "IMPUESTOS ARBA", "AGIP": "IMPUESTOS AGIP",
        "HOSTINGER": "HOSTINGER", "AWS": "AMAZON AWS", "MERCADOLIBRE": "MERCADOLIBRE"
    }
    
    for key, unified in canonical_rules.items():
        if key in candidate: return unified
            
    # Limpieza final de caracteres no alfanuméricos
    candidate = re.sub(r'[^A-Z0-9 ]', '', candidate).strip() 
    return candidate if len(candidate) > 2 else "VARIOS"

def aggregate_data(arca_data, bank_data):
    monthly_map = defaultdict(lambda: {
        'arca': 0.0, 'income': 0.0, 'expenses': 0.0, 
        'own_transfers': 0.0, 'credit_card_payments': 0.0, 'result': 0.0
    })
    
    concepts_map = defaultdict(lambda: {'count': 0, 'total': 0.0, 'details': []})

    # ARCA
    for item in arca_data:
        monthly_map[item['month_key']]['arca'] += item['amount']

    # BANCOS
    concept_blocklist = [
        'NO GRAVADA', 'INMEDIATA', 'ENVIADA', 'DEBIN', 'CREDIN', 
        'IMPUESTO PAIS', 'RG ', 'LEY ', 'INTERESES', 'MANTENIMIENTO', 'DB ', 'IVA ', 'IIBB',
        'COMISION', 'SANTANDER', 'CREDITO', 'VARIOS', 'A ', 'DE '
    ]

    for item in bank_data:
        m = item['month_key']
        desc = item['description']
        amt = item['amount']
        
        category, is_own = classify_movement(desc, amt, item['source'])
        
        # --- Lógica Financiera Mensual ---
        if amt > 0:
            if is_own: 
                monthly_map[m]['own_transfers'] += amt
            else:
                monthly_map[m]['income'] += amt
                monthly_map[m]['result'] += amt
        else:
            # Es negativo (Egreso o Pago Deuda)
            abs_amt = abs(amt)
            monthly_map[m]['result'] += amt # Siempre resta caja
            
            if category == 'Pago Tarjeta / Crédito':
                monthly_map[m]['credit_card_payments'] += abs_amt
                # NO suma a 'expenses' porque es deuda financiera, no gasto operativo del mes
            else:
                monthly_map[m]['expenses'] += abs_amt # Es gasto operativo (Débito, Transferencia, Extracción)

            # --- Análisis de Conceptos ---
            # Solo analizamos GASTOS reales (no pagos de tarjeta ni transf propias)
            if not is_own and category != 'Pago Tarjeta / Crédito':
                unified_name = normalize_concept_text(desc)
                is_blocked = any(unified_name == b or unified_name.startswith(b) for b in concept_blocklist)
                
                if not is_blocked and len(unified_name) > 2:
                    concepts_map[unified_name]['count'] += 1
                    concepts_map[unified_name]['total'] += abs_amt
                    concepts_map[unified_name]['details'].append({
                        'date': item['date'].strftime('%d/%m/%Y'),
                        'original_desc': desc,
                        'amount': abs_amt,
                        'source': item['source']
                    })

    # Generar salidas ordenadas
    sorted_months = sorted(monthly_map.keys())
    history = [{'month': m, **monthly_map[m]} for m in sorted_months]
    
    totals = {'arca': 0, 'income': 0, 'expenses': 0, 'result': 0}
    for h in history:
        totals['arca'] += h['arca']
        totals['income'] += h['income']
        totals['expenses'] += h['expenses']
        totals['result'] += h['result']

    top_concepts = []
    for name, data in concepts_map.items():
        if data['total'] > 0:
            data['details'].sort(key=lambda x: datetime.strptime(x['date'], '%d/%m/%Y'), reverse=True)
            top_concepts.append({'name': name, **data})
    
    top_concepts.sort(key=lambda x: x['total'], reverse=True)

    return {
        'monthly_history': history,
        'recurring_expenses': top_concepts,
        'potential_clients': potential_clients,
        'totals': totals
    }

def extract_sender_name(description):
    """
    Intenta extraer el nombre del remitente de una descripción de transferencia.
    """
    desc = description.upper().strip()
    
    # 1. Santander: "Transferencia recibida De NOMBRE / ..."
    if "TRANSFERENCIA RECIBIDA" in desc and "DE " in desc:
        # Busca lo que hay entre "DE " y el siguiente "/" o el final
        match = re.search(r" DE (.*?)(?:/|$)", desc)
        if match:
            name = match.group(1).strip()
            # Limpiar basura final si quedó
            name = name.split(" - ")[0] 
            return clean_name(name)

    # 2. Santander: "Pago a proveedores recibido NOMBRE ..."
    if "PAGO A PROVEEDORES RECIBIDO" in desc:
        # Generalmente seguido del nombre y luego números
        # Borramos la frase clave
        clean = desc.replace("PAGO A PROVEEDORES RECIBIDO", "").strip()
        # Tomamos todo hasta encontrar el primer bloque de números largo (CUIT/ID)
        match = re.search(r"^([A-Z\s\.]+)(?=\d)", clean)
        if match:
            return clean_name(match.group(1))
        else:
            # Si no hay números, devolvemos todo (con cuidado)
            return clean_name(clean)

    # 3. Patrones Genéricos (Mercado Pago / Otros)
    patterns = [
        r"TRANSFERENCIA DE (.*)",
        r"TRANSFERENCIA RECIBIDA DE (.*)",
        r"CREDITO POR TRANSFERENCIA DE (.*)",
        r"CREDITO TRANSFERENCIA DE (.*)",
        r"^DE (.*)", 
        r"TRANSF. DE (.*)"
    ]
    
    for pat in patterns:
        match = re.search(pat, desc)
        if match:
            return clean_name(match.group(1))
            
    return None

def clean_name(name):
    """Limpieza auxiliar de nombres extraídos."""
    if not name: return None
    name = name.strip()
    
    # Quitar CUIT/CUIL si aparece (ej: NOMBRE APELLIDO 20-...)
    name = re.sub(r'\d{2}-\d{8}-\d', '', name)
    name = re.sub(r'\d{10,}', '', name) # Quitar numeros largos
    
    # Quitar sufijos bancarios
    trash = [" - BANCO", " BANCO", " S.A.", " SA", " CUIT", " CUIL", " VARIOS", "- VAR"]
    for t in trash:
        name = name.replace(t, "")
        
    name = re.sub(r'[^A-Z ]', '', name).strip()
    return name if len(name) > 3 else None

def aggregate_data(arca_data, bank_data, wu_data):
    monthly_map = defaultdict(lambda: {
        'arca': 0.0, 'income': 0.0, 'expenses': 0.0, 
        'own_transfers': 0.0, 'credit_card_payments': 0.0, 'result': 0.0
    })
    
    potential_clients_map = defaultdict(lambda: {'count': 0, 'total': 0.0, 'details': []})

    # ARCA
    for item in arca_data:
        monthly_map[item['month_key']]['arca'] += item['amount']

    # WESTERN UNION (Siempre Ingreso)
    for item in wu_data:
        m = item['month_key']
        amt = item['amount']
        monthly_map[m]['income'] += amt
        monthly_map[m]['result'] += amt
        
        # Add to potential clients
        sender = item['description'] # "WU MTCN - Sender"
        potential_clients_map[sender]['count'] += 1
        potential_clients_map[sender]['total'] += amt
        potential_clients_map[sender]['details'].append({
            'date': item['date'].strftime('%d/%m/%Y'),
            'original_desc': sender,
            'amount': amt,
            'source': item['source']
        })

    # BANCOS
    for item in bank_data:
        m = item['month_key']
        desc = item['description']
        amt = item['amount']
        
        category, is_own = classify_movement(desc, amt, item['source'])
        
        # --- Lógica Financiera Mensual ---
        if amt > 0:
            if is_own: 
                monthly_map[m]['own_transfers'] += amt
            else:
                monthly_map[m]['income'] += amt
                monthly_map[m]['result'] += amt
                
                # --- Análisis de Potenciales Clientes (Ingresos) ---
                sender = desc
                potential_clients_map[sender]['count'] += 1
                potential_clients_map[sender]['total'] += amt
                potential_clients_map[sender]['details'].append({
                    'date': item['date'].strftime('%d/%m/%Y'),
                    'original_desc': desc,
                    'amount': amt,
                    'source': item['source']
                })

        else:
            # Es negativo (Egreso o Pago Deuda)
            abs_amt = abs(amt)
            monthly_map[m]['result'] += amt # Siempre resta caja
            
            if category == 'Pago Tarjeta / Crédito':
                monthly_map[m]['credit_card_payments'] += abs_amt
            else:
                monthly_map[m]['expenses'] += abs_amt

    # Generar salidas ordenadas
    sorted_months = sorted(monthly_map.keys())
    history = [{'month': m, **monthly_map[m]} for m in sorted_months]
    
    totals = {'arca': 0, 'income': 0, 'expenses': 0, 'result': 0}
    for h in history:
        totals['arca'] += h['arca']
        totals['income'] += h['income']
        totals['expenses'] += h['expenses']
        totals['result'] += h['result']

    # Procesar Potenciales Clientes (Orden Alfabético)
    potential_clients = []
    
    # Pre-procesar facturas de ARCA para matching
    available_invoices = []
    for inv in arca_data:
        available_invoices.append({
            'amount': abs(inv['amount']), 
            'date': inv['date'],
            'recipient_name': inv.get('recipient_name'),
            'recipient_cuit': inv.get('recipient_cuit'),
            'matched': False 
        })

    for name, data in potential_clients_map.items():
        data['details'].sort(key=lambda x: datetime.strptime(x['date'], '%d/%m/%Y'), reverse=True)
        
        # Lógica de Matching
        for tx in data['details']:
            # Skip matching for WU if needed, or apply similar logic. 
            # WU receipts are proof themselves, but we might want to match with invoices if they exist.
            # Assuming standard matching logic applies.
            
            tx_amount = tx['amount']
            tx_date = datetime.strptime(tx['date'], '%d/%m/%Y')
            tx_name_clean = name.upper().replace(" ", "")
            
            is_invoiced = False
            
            for inv in available_invoices:
                if inv['matched']: continue
                
                match_amount = abs(inv['amount'] - tx_amount) < 1.0
                delta_days = (inv['date'] - tx_date).days
                match_date = -5 <= delta_days <= 45
                
                match_identity = False
                if inv['recipient_cuit']:
                    cuit_clean = inv['recipient_cuit'].replace("-", "")
                    if inv['recipient_cuit'] in tx_name_clean or cuit_clean in tx_name_clean:
                        match_identity = True
                
                if not match_identity and inv['recipient_name']:
                    inv_name_norm = inv['recipient_name'].upper().strip()
                    tx_desc_norm = name.upper().strip()
                    inv_tokens = [t for t in inv_name_norm.split() if len(t) > 2]
                    matches = sum(1 for t in inv_tokens if t in tx_desc_norm)
                    if len(inv_tokens) > 0 and matches >= len(inv_tokens) * 0.6:
                        match_identity = True

                if (match_amount and match_date and match_identity) or \
                   (match_amount and match_identity) or \
                   (match_amount and match_date and not inv['recipient_name'] and not inv['recipient_cuit']):
                    is_invoiced = True
                    inv['matched'] = True
                    break
            
            tx['is_invoiced'] = is_invoiced

        potential_clients.append({'name': name, **data})
        
    potential_clients.sort(key=lambda x: x['name'])

    return {
        'monthly_history': history,
        'potential_clients': potential_clients,
        'totals': totals
    }
