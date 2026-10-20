"""
Generador de lista de números desde URLs de wa.me
Lee las URLs del archivo numeros_raw.txt y genera config.json
"""
import json
import re

def parse_urls(filepath):
    """Extrae números de teléfono de URLs de wa.me"""
    numeros = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            match = re.search(r'wa\.me/(\d+)', line)
            if match:
                phone = match.group(1)
                if phone not in numeros:
                    numeros.append(phone)
    return numeros

def decode_message_from_url(url):
    """Decodifica el mensaje predefinido de la URL"""
    match = re.search(r'text=(.+?)(?:\s*$)', url)
    if match:
        from urllib.parse import unquote
        return unquote(match.group(1))
    return None

if __name__ == "__main__":
    numeros = parse_urls("numeros_raw.txt")
    
    # Detectar mensaje de la primera URL
    mensaje = ""
    with open("numeros_raw.txt", 'r', encoding='utf-8') as f:
        for line in f:
            if 'wa.me/' in line:
                msg = decode_message_from_url(line.strip())
                if msg:
                    mensaje = msg
                break
    
    print(f"[+] Números encontrados: {len(numeros)}")
    print(f"[+] Mensaje detectado: {mensaje[:80]}...")
    
    config = {
        "mensaje": mensaje,
        "numeros": numeros,
        "delay_min": 1,
        "delay_max": 10
    }
    
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"[+] config.json generado con {len(numeros)} números")
