import json
import os

def generate_html_report(data, template_path, output_path):
    """Inyecta el JSON de datos en la plantilla HTML."""
    
    # Convertir datos a JSON string y escapar comillas para evitar romper el script JS
    # ensure_ascii=False para mantener tildes y ñ
    json_data = json.dumps(data, default=str, ensure_ascii=False)
    
    # Escapar caracteres que rompen HTML script tags
    json_data = json_data.replace('<', '\u003c').replace('>', '\u003e')
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Inyección exacta
        target = '{{ data_json | safe }}'
        if target not in html_content:
            print(f"ADVERTENCIA: No se encontró la marca '{target}' en el template.")
        
        final_html = html_content.replace(target, json_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
            
        print(f"Reporte generado exitosamente en: {output_path}")
        return True
    except Exception as e:
        print(f"Error generando HTML: {e}")
        return False