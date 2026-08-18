import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = 'C:\\Users\\Esteban Selvaggi\\Desktop\\subagent-driven_development\\data\\inputs\\contacts.db'

conn = sqlite3.connect(DB_PATH)

# Obtener datos de la campaña recién insertada
query = '''
    SELECT 
        l.primary_email as Email,
        m.title as Empresa,
        m.sector as Sector,
        m.city as Ciudad,
        m.province as Provincia,
        m.country as Pais,
        cp.sender as Cuenta_Remitente,
        cp.date as Fecha_Envio,
        cp.campaign_id as Campaña_ID,
        cp.subject as Asunto
    FROM campaign cp
    JOIN lead l ON cp.contact_rowid = l.ROWID
    JOIN main m ON l.ROWID = m.ROWID
    WHERE cp.campaign_id = 'no_contactados_20260810'
    ORDER BY cp.date, cp.sender
'''

df = pd.read_sql_query(query, conn)
conn.close()

# Guardar Excel
output_path = f'C:\\Users\\Esteban Selvaggi\\Desktop\\LISTA_NO_CONTACTADOS_{datetime.now().strftime("%Y%m%d")}.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='No_Contactados_Enviados', index=False)
    
    # Hoja resumen
    summary = pd.DataFrame({
        'Métrica': ['Total contactos', 'Cuentas usadas', 'Fecha campaña', 'Campaña ID'],
        'Valor': [len(df), df['Cuenta_Remitente'].nunique(), df['Fecha_Envio'].iloc[0], 'no_contactados_20260810']
    })
    summary.to_excel(writer, sheet_name='Resumen', index=False)

print(f'Excel generado: {output_path}')
print(f'Registros: {len(df)}')