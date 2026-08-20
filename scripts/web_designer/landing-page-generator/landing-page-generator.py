#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Landing Pages optimizadas para SEO Local y CSV de Contactos.
Genera landing pages HTML y un archivo CSV de contactos estilo Google
desde datos de Google Business Profile.
"""

import csv
import re
from core.paths import PROJECT_ROOT
import json
from unicodedata import normalize
import shutil
import urllib.request
import urllib.error
import time
import hashlib


# Diccionario para convertir nombres de país a códigos
COUNTRY_CODES = {
    "Argentina": "ARG"
}

# Plantilla de workflow de WhatsApp para funnel de contactos
WHATSAPP_WORKFLOW_TEMPLATE = {
    "funnel_steps": [
        {
            "step": 1,
            "name": "Primer contacto",
            "message": "Hola, soy Esteban. Este número figura para {title} en Google. Armé una página web con datos públicos: {backlink} para {category}. ¿Te interesa sugerir cambios en Google?"
        },
        {
            "step": 2,
            "name": "Seguimiento 1",
            "message": "Hola, soy Esteban. Vi mejoras para tu sitio web y tu posicionamiento en Google. ¿Querés que te cuente?"
        },
        {
            "step": 3,
            "name": "Seguimiento 2",
            "message": "Estuve revisando tu posicionamiento web. Soy SEO y experto en desarrollo web. Vi ajustes rápidos para mejorar tu ranking en Google. ¿Te interesa?"
        },
        {
            "step": 4,
            "name": "Seguimiento 3",
            "message": "Ayudo a negocios locales a mejorar su página web y SEO local. Puedo optimizar tu sitio web y tu posicionamiento en Google. ¿Conversamos?"
        },
        {
            "step": 5,
            "name": "Cierre de secuencia",
            "message": "Te preparo gratis un informe SEO para mejorar tu página web y posicionamiento en Google. ¿Querés?"
        }
    ]
}

def crear_slug(texto):
    """Crea un slug amigable para URLs"""
    if not texto:
        return "negocio"
    texto = normalize('NFKD', str(texto)).encode('ASCII', 'ignore').decode('ASCII')
    texto = texto.lower()
    texto = re.sub(r'[^\w\s-]', '', texto)
    texto = re.sub(r'[-\s]+', '-', texto)
    return texto.strip('-')[:80]

def extract_whatsapp_from_links(website='', order_online=''):
    """
    Extrae número de WhatsApp de campos website o order_online.
    Retorna el número en formato +54 9 11 XXXXXXXX o None si no encuentra.
    """
    combined_text = f"{website} {order_online}"

    # Patrón 1: api.whatsapp.com/send?phone=XXXXXXXXXX
    match = re.search(r'whatsapp\.com/send\?phone=(\d+)', combined_text)
    if match:
        phone_digits = match.group(1)
        if phone_digits.startswith('54911') and len(phone_digits) == 13:
            return f"+{phone_digits}"
        elif phone_digits.startswith('549') and len(phone_digits) >= 12:
            return f"+{phone_digits}"

    # Patrón 2: wa.me/XXXXXXXXXX o wa.link/...
    match = re.search(r'wa\.(?:me|link)/[^/\s]*?(\d{10,15})', combined_text)
    if match:
        phone_digits = match.group(1)
        if phone_digits.startswith('54911') and len(phone_digits) == 13:
            return f"+{phone_digits}"
        elif phone_digits.startswith('549') and len(phone_digits) >= 12:
            return f"+{phone_digits}"

    return None

def format_phone_number(phone_string, website='', order_online=''):
    """
    Elige el mejor número telefónico con mayor probabilidad de ser WhatsApp.

    Prioridad:
      1. WhatsApp explícito en website/order_online (100% seguro)
      2. Celular con "15" en phone (alta probabilidad)
      3. Teléfono fijo en phone (baja probabilidad, sin WhatsApp)

    Formato: +54 9 11 XXXXXXXX (celular) o +54 11 XXXXXXXX (fijo)

    Returns: (True, formatted_number, priority_level) on success
             (False, original_number, 0) on failure
    """
    # PRIORIDAD 1: Buscar WhatsApp explícito en links
    whatsapp_number = extract_whatsapp_from_links(website, order_online)
    if whatsapp_number:
        return (True, whatsapp_number, 1)  # Prioridad máxima

    # PRIORIDAD 2 y 3: Analizar campo phone
    if not phone_string or not isinstance(phone_string, str):
        return (False, phone_string if phone_string else '', 0)

    phone_cleaned = phone_string.strip()

    # Detectar si es celular (tiene "15" después del 011)
    is_mobile = bool(re.search(r'011[\s-]*15[\s-]', phone_cleaned))

    # Extraer solo dígitos
    digits_only = re.sub(r'\D', '', phone_cleaned)

    # Procesar números con código 011 (Buenos Aires)
    if digits_only.startswith('011'):
        after_area_code = digits_only[3:]

        # Si es celular, quitar el "15"
        if is_mobile and after_area_code.startswith('15'):
            after_area_code = after_area_code[2:]

        # Validar 8 dígitos
        if len(after_area_code) >= 8:
            local_number = after_area_code[:8]

            if is_mobile:
                # PRIORIDAD 2: Celular (alta probabilidad de WhatsApp)
                formatted_number = f"+54911{local_number}"
                return (True, formatted_number, 2)
            else:
                # PRIORIDAD 3: Fijo (baja probabilidad, sin WhatsApp)
                formatted_number = f"+5411{local_number}"
                return (True, formatted_number, 3)

    # Fallback: intentar extraer del final
    if len(digits_only) >= 8:
        has_15 = bool(re.search(r'15', phone_cleaned))

        if has_15:
            # Es celular
            match = re.search(r'15[\s-]*(\d{4})[\s-]*(\d{4})', phone_cleaned)
            if match:
                local_number = match.group(1) + match.group(2)
                formatted_number = f"+54911{local_number}"
                return (True, formatted_number, 2)

        # Asumir fijo
        local_number = digits_only[-8:]
        formatted_number = f"+5411{local_number}"
        return (True, formatted_number, 3)

    # No se pudo formatear
    return (False, phone_string, 0)

def generar_hash_url(url):
    """Genera un hash MD5 de la URL para usar como identificador único"""
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def extraer_datos_direccion(address, complete_address_json=''):
    """
    Extrae componentes de dirección de complete_address_json o de la cadena address.
    Retorna un diccionario con city, region, postal_code, country, full_address_string, street_address.
    """
    city = ''
    region = ''
    postal_code = ''
    country = ''
    street_address = ''
    full_address_string = ''

    # 1. Intentar parsear complete_address_json
    if complete_address_json:
        try:
            ca_data = json.loads(complete_address_json)
            street_address = ca_data.get('street', '')
            city = ca_data.get('city', '')
            region = ca_data.get('state', '') # Using 'state' from JSON for 'region'
            postal_code = ca_data.get('postal_code', '')
            country_code = ca_data.get('country', '')
            country = "Argentina" if country_code == "AR" else country_code # Map AR to Argentina

            # Construct a human-readable full address
            parts = [street_address, city, region, postal_code, country]
            full_address_string = ", ".join(filter(None, parts))

            return {
                'city': city,
                'region': region,
                'postal_code': postal_code,
                'country': country,
                'full_address_string': full_address_string,
                'street_address': street_address
            }
        except json.JSONDecodeError:
            pass # Fallback to parsing 'address' string if JSON is malformed

    # 2. Fallback a parsear la cadena 'address' (lógica existente, ajustada para new return)
    if not address:
        return {
            'city': '', 'region': '', 'postal_code': '', 'country': '',
            'full_address_string': '', 'street_address': ''
        }

    partes = [p.strip() for p in address.split(',')]
    
    # Intenta encontrar el código postal primero
    for parte in partes:
        match = re.search(r'\b([A-Z]?\d{4,5})\b', parte)
        if match:
            postal_code = match.group(1)
            break
            
    # Asume un orden típico para extraer
    if len(partes) >= 1:
        country = partes[-1]
    if len(partes) >= 2:
        region = partes[-1] # Assuming region is second to last part, country is last part
        city = partes[-2] # Assuming city is third to last part
    if len(partes) >= 3: # Street is often the first part
        street_address = partes[0]

    # Construct full address string from parsed parts
    parts = [street_address, city, region, postal_code, country]
    full_address_string = ", ".join(filter(None, parts))
    
    return {
        'city': city,
        'region': region,
        'postal_code': postal_code,
        'country': country,
        'full_address_string': full_address_string,
        'street_address': street_address
    }

def parsear_horarios(open_hours):
    """Parsea los horarios de apertura desde el campo open_hours del CSV."""
    if not open_hours or open_hours == '':
        return {'weekday_opens': '', 'weekday_closes': '', 'saturday_opens': '', 'saturday_closes': ''}
    try:
        if open_hours.startswith('['):
            horarios_json = json.loads(open_hours)
            weekday_opens, weekday_closes, saturday_opens, saturday_closes = '', '', '', ''
            for dia in horarios_json:
                dia_lower = dia.lower()
                if 'lunes' in dia_lower or 'monday' in dia_lower:
                    match = re.search(r'(\d{1,2}:\d{2})[–-](\d{1,2}:\d{2})', dia)
                    if match:
                        weekday_opens, weekday_closes = match.groups()
                elif 'sábado' in dia_lower or 'saturday' in dia_lower:
                    match = re.search(r'(\d{1,2}:\d{2})[–-](\d{1,2}:\d{2})', dia)
                    if match:
                        saturday_opens, saturday_closes = match.groups()
            return {'weekday_opens': weekday_opens, 'weekday_closes': weekday_closes, 'saturday_opens': saturday_opens, 'saturday_closes': saturday_closes}
    except:
        pass
    return {'weekday_opens': '', 'weekday_closes': '', 'saturday_opens': '', 'saturday_closes': ''}

def generar_canonical_url(slug, base_url='https://todoconsultores.com'):
    return f"{base_url}/{slug}.html"
def generar_meta_tags(datos, canonical_url, address_data=None):
    title = datos.get('title', 'Negocio')
    category = datos.get('category', 'Servicio')
    thumbnail = datos.get('thumbnail', '')
    meta_description = generar_meta_description(datos, address_data)
    og_title = f"{title} - {category}"
    og_description = meta_description
    og_image = thumbnail if thumbnail else 'assets/images/carousel-cover.png'
    return {'meta_description': meta_description, 'canonical_url': canonical_url, 'og_title': og_title, 'og_description': og_description, 'og_image': og_image, 'twitter_title': og_title, 'twitter_description': og_description, 'twitter_image': og_image, 'logo_url': og_image}
def generar_faqs(categoria, nombre_negocio, datos=None, address_data=None, horarios=None):
    """
    Genera 5 FAQs dinámicas optimizadas para SEO usando los datos disponibles del negocio.

    Parámetros:
        categoria: Categoría del negocio
        nombre_negocio: Nombre del negocio
        datos: Diccionario con datos del negocio (phone, emails, website, descriptions, review_rating, review_count, etc.)
        address_data: Diccionario con datos de dirección (city, region, borough, street, postal_code, etc.)
        horarios: Diccionario con horarios de atención (weekday_opens, weekday_closes, etc.)

    Retorna:
        Lista de tuplas (pregunta, respuesta) con 5 FAQs optimizadas para SEO
    """
    lista_faqs = []

    # Extraer datos de dirección
    ciudad = address_data.get('city', '') if address_data else ''
    region = address_data.get('region', '') if address_data else ''
    barrio = address_data.get('borough', '') if address_data else ''
    calle = address_data.get('street', '') if address_data else ''
    codigo_postal = address_data.get('postal_code', '') if address_data else ''

    # Extraer datos del negocio
    descripciones = datos.get('descriptions', '') if datos else ''
    calificacion = datos.get('review_rating', '') if datos else ''
    cantidad_resenas = datos.get('review_count', '') if datos else ''
    telefono = datos.get('phone', '') if datos else ''
    correos_electronicos = datos.get('emails', '') if datos else ''
    sitio_web = datos.get('website', '') if datos else ''
    enlace_google_maps = datos.get('link', '') if datos else ''

    # Crear variaciones de la categoría para SEO (evitar keyword stuffing)
    categoria_lower = categoria.lower()
    palabras_categoria = categoria_lower.split()

    # Generar sinónimos o variaciones según las palabras clave
    if 'aluminio' in categoria_lower:
        variacion_categoria_1 = 'aberturas de aluminio'
        variacion_categoria_2 = 'carpintería de aluminio'
    elif 'computación' in categoria_lower or 'computadora' in categoria_lower:
        variacion_categoria_1 = 'servicios informáticos'
        variacion_categoria_2 = 'tecnología'
    elif 'ventana' in categoria_lower:
        variacion_categoria_1 = 'ventanas y aberturas'
        variacion_categoria_2 = 'cerramientos'
    else:
        variacion_categoria_1 = categoria_lower
        variacion_categoria_2 = 'nuestros servicios'

    # FAQ 1: Servicios principales (Opción B con ciudad y descripciones)
    pregunta_1 = f'¿Qué servicios de {categoria_lower} ofrece {nombre_negocio} en {ciudad}?'

    # Construir respuesta larga (120-200 palabras) con descripciones
    respuesta_1 = f'{nombre_negocio} ofrece servicios de {categoria_lower} en {ciudad}. '

    if descripciones:
        # Usar las primeras 150 caracteres de las descripciones
        descripciones_recortadas = descripciones[:150].strip()
        if len(descripciones) > 150:
            # Encontrar el último espacio para no cortar palabras
            ultimo_espacio = descripciones_recortadas.rfind(' ')
            if ultimo_espacio > 0:
                descripciones_recortadas = descripciones_recortadas[:ultimo_espacio]
        respuesta_1 = respuesta_1 + descripciones_recortadas + '. '
    else:
        respuesta_1 = respuesta_1 + f'Somos especialistas en {variacion_categoria_1} brindando soluciones profesionales y personalizadas. '

    respuesta_1 = respuesta_1 + f'Contamos con experiencia comprobada en el sector y un equipo de profesionales altamente capacitados para atender todas tus necesidades de {variacion_categoria_2}. Nuestro compromiso es ofrecer servicios de calidad que superen las expectativas de cada cliente en {ciudad} y toda la región de {region}.'

    lista_faqs.append((pregunta_1, respuesta_1))

    # FAQ 2: Ubicación (Opción C para ubicación + Opción B para respuesta)
    if barrio and ciudad and region and codigo_postal:
        texto_ubicacion = f"{barrio}, {ciudad}, {region} (código postal: {codigo_postal})"
    elif barrio and ciudad and region:
        texto_ubicacion = f"{barrio}, {ciudad}, {region}"
    elif ciudad and region:
        texto_ubicacion = f"{ciudad}, {region}"
    elif ciudad:
        texto_ubicacion = ciudad
    else:
        texto_ubicacion = 'la zona'

    pregunta_2 = f'¿Dónde se encuentra {nombre_negocio} en {ciudad}?'
    respuesta_2 = f'Estamos ubicados en {texto_ubicacion}. '

    if enlace_google_maps:
        respuesta_2 = respuesta_2 + f'Puedes encontrarnos fácilmente en Google Maps usando este enlace: {enlace_google_maps}. '

    respuesta_2 = respuesta_2 + f'{nombre_negocio} es de fácil acceso y atendemos tanto consultas presenciales en nuestra ubicación como consultas remotas para brindarte la mejor experiencia de servicio. Nuestras instalaciones están estratégicamente ubicadas para servir a toda la comunidad de {ciudad} y zonas aledañas con la mayor comodidad posible.'

    lista_faqs.append((pregunta_2, respuesta_2))

    # FAQ 3: Horarios (Opción B - formato estructurado)
    horario_lunes_viernes = ''
    horario_sabado = ''
    estado_domingo = 'Cerrado'

    if horarios and horarios.get('weekday_opens') and horarios.get('weekday_closes'):
        horario_semana_apertura = horarios['weekday_opens']
        horario_semana_cierre = horarios['weekday_closes']
        horario_lunes_viernes = f"{horario_semana_apertura} a {horario_semana_cierre}"

        if horarios.get('saturday_opens') and horarios.get('saturday_closes'):
            horario_sabado_apertura = horarios['saturday_opens']
            horario_sabado_cierre = horarios['saturday_closes']
            horario_sabado = f"{horario_sabado_apertura} a {horario_sabado_cierre}"
        else:
            horario_sabado = 'Cerrado'
    else:
        horario_lunes_viernes = 'Horario comercial estándar'
        horario_sabado = 'Consultar disponibilidad'

    pregunta_3 = f'¿Cuál es el horario de atención de {nombre_negocio}?'
    respuesta_3 = f'Los horarios de atención de {nombre_negocio} son: Lunes a Viernes: {horario_lunes_viernes} | Sábado: {horario_sabado} | Domingo: {estado_domingo}. '
    respuesta_3 = respuesta_3 + f'Te recomendamos contactarnos previamente para coordinar tu visita y asegurar una atención personalizada. En {nombre_negocio} nos adaptamos a las necesidades de nuestros clientes, por lo que también podemos coordinar citas fuera del horario regular según disponibilidad. Para mayor información sobre horarios especiales o días festivos, no dudes en comunicarte con nosotros.'

    lista_faqs.append((pregunta_3, respuesta_3))

    # FAQ 4: Formas de contacto (Opción B - formato estructurado con separadores)
    lista_opciones_contacto = []

    if telefono:
        lista_opciones_contacto.append(f'Llámanos al {telefono}')

    if correos_electronicos:
        primer_correo = correos_electronicos.split(",")[0].strip()
        lista_opciones_contacto.append(f'Escríbenos a {primer_correo}')

    if sitio_web and sitio_web != '#':
        lista_opciones_contacto.append(f'Visita {sitio_web}')

    if enlace_google_maps:
        lista_opciones_contacto.append(f'Encuéntranos en Google Maps')

    if lista_opciones_contacto:
        texto_opciones_contacto = ' | '.join(lista_opciones_contacto)
    else:
        texto_opciones_contacto = 'Contáctanos por los medios de comunicación disponibles'

    pregunta_4 = f'¿Cómo puedo contactar a {nombre_negocio}?'
    respuesta_4 = f'Puedes comunicarte con {nombre_negocio} de las siguientes formas: {texto_opciones_contacto}. '
    respuesta_4 = respuesta_4 + f'Nuestro equipo está disponible para responder todas tus consultas relacionadas con {variacion_categoria_1} y brindarte asesoramiento profesional sobre nuestros servicios de {categoria_lower}. En {nombre_negocio} valoramos la comunicación directa con nuestros clientes y nos esforzamos por responder a todas las consultas en el menor tiempo posible. Ya sea que necesites un presupuesto, información técnica o simplemente quieras conocer más sobre nuestros servicios, estamos aquí para ayudarte.'

    lista_faqs.append((pregunta_4, respuesta_4))

    # FAQ 5: Reseñas y reputación (Opción C con calificación y reseñas)
    pregunta_5 = f'¿Qué dicen los clientes sobre {nombre_negocio}?'

    respuesta_5 = ''
    if calificacion and cantidad_resenas:
        try:
            calificacion_float = float(calificacion)
            cantidad_resenas_int = int(cantidad_resenas)

            if calificacion_float > 0 and cantidad_resenas_int > 0:
                respuesta_5 = f'Con una calificación de {calificacion_float}/5.0 basada en {cantidad_resenas_int} reseñas en Google, {nombre_negocio} es reconocido por su excelencia en {categoria_lower}. '
                respuesta_5 = respuesta_5 + f'Nuestros {cantidad_resenas_int} clientes satisfechos destacan la calidad de nuestro trabajo, la atención personalizada y el compromiso con cada proyecto. '
            else:
                respuesta_5 = f'{nombre_negocio} se destaca por su experiencia en {categoria_lower} y el compromiso con cada cliente. '
        except (ValueError, TypeError):
            respuesta_5 = f'{nombre_negocio} se destaca por su experiencia en {categoria_lower} y el compromiso con cada cliente. '
    else:
        respuesta_5 = f'{nombre_negocio} se destaca por su experiencia en {categoria_lower} y el compromiso con cada cliente. '

    respuesta_5 = respuesta_5 + f'Elegir {nombre_negocio} significa optar por profesionalismo, experiencia y dedicación. Trabajamos con tecnología actualizada y seguimos los más altos estándares de calidad en cada servicio que brindamos. Nuestro objetivo es superar las expectativas de cada cliente y construir relaciones de confianza a largo plazo. La satisfacción de nuestros clientes es nuestra mejor carta de presentación y nos motiva a mejorar continuamente nuestros servicios de {variacion_categoria_2} en {ciudad}.'

    lista_faqs.append((pregunta_5, respuesta_5))

    return lista_faqs
def cargar_cache_imagenes(cache_file):
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}
def guardar_cache_imagenes(cache_file, cache_data):
    with open(cache_file, 'w', encoding='utf-8') as f: json.dump(cache_data, f, indent=2, ensure_ascii=False)
def descargar_imagen(url, output_path, cache_data=None, timeout=10):
    if output_path.exists():
        url_hash = generar_hash_url(url)
        if cache_data and url_hash in cache_data and str(output_path) == cache_data[url_hash].get('path', ''):
            return (True, True)
    if cache_data:
        url_hash = generar_hash_url(url)
        if url_hash in cache_data:
            cached_path = Path(cache_data[url_hash]['path'])
            if cached_path.exists() and cached_path != output_path:
                try:
                    shutil.copy2(cached_path, output_path)
                    return (True, True)
                except: pass
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as response, open(output_path, 'wb') as f:
            f.write(response.read())
        if cache_data is not None:
            cache_data[generar_hash_url(url)] = {'url': url, 'path': str(output_path), 'filename': output_path.name, 'timestamp': time.time()}
        return (True, False)
    except Exception as e:
        print(f"   ⚠️  Error descargando {url}: {str(e)}")
        return (False, False)
def procesar_imagenes_negocio(datos, gallery_dir, categoria, nombre_negocio, index, cache_data=None):
    imagenes_json = datos.get('images', '')
    if not imagenes_json: return []
    try:
        imagenes_data = json.loads(imagenes_json)
        if not isinstance(imagenes_data, list): return []
        imagenes_descargadas = []
        slug_base = crear_slug(f"{categoria}-{nombre_negocio}")[:50]
        for idx, img_info in enumerate(imagenes_data[:8]):
            if not isinstance(img_info, dict) or 'image' not in img_info: continue
            img_url = img_info['image']
            title_img = img_info.get('title', categoria)
            alt_text = crear_slug(f"{categoria}-{nombre_negocio}-{title_img}")[:60]
            extension = '.jpg'
            if '.png' in img_url.lower(): extension = '.png'
            elif '.webp' in img_url.lower(): extension = '.webp'
            filename = f"{slug_base}-{idx+1}{extension}"
            output_path = gallery_dir / filename
            success, cached = descargar_imagen(img_url, output_path, cache_data)
            if success:
                imagenes_descargadas.append({'filename': filename, 'alt': alt_text, 'title': title_img})
        return imagenes_descargadas
    except: return []
def generar_galeria_html(imagenes):
    if not imagenes: return '<div>Galería no disponible</div>'
    html_items = ''
    for img in imagenes:
        html_items += f'<div class="item"><a href="../assets/images/gallery/{img["filename"]}" data-caption="{img["title"]}"><img src="../assets/images/gallery/{img["filename"]}" alt="{img["alt"]}" /></a></div>'
    return html_items
def generar_meta_description(datos, address_data=None):
    nombre = datos.get('title', 'Negocio')
    categoria = datos.get('category', 'Servicio')
    telefono = datos.get('phone', '')
    
    city = address_data.get('city', '') if address_data else ''

    description = f"{categoria} ✓ {nombre}"
    if city: description += f" en {city}"
    description += " - Atención profesional y personalizada. "
    if telefono: description += f"Contacto: {telefono}. "
    return description[:155]
def generar_landing_page(template_html, datos, output_path, imagenes_gallery=None, slug='', address_data=None):
    html = template_html
    title = datos.get('title', 'Negocio')
    category = datos.get('category', 'Servicio')
    phone = datos.get('phone', '')
    address = datos.get('address', '')
    website = datos.get('website', '#')
    thumbnail = datos.get('thumbnail', '')
    latitude = datos.get('latitude', '')
    longitude = datos.get('longitude', '')
    emails = datos.get('emails', '')

    city = address_data.get('city', '') if address_data else ''
    region = address_data.get('region', '') if address_data else ''
    postal_code = address_data.get('postal_code', '') if address_data else ''
    country = address_data.get('country', '') if address_data else ''
    full_address_string = address_data.get('full_address_string', address) # Use generated full string, fallback to original 'address' if parsing failed
    street_address = address_data.get('street_address', '') # For Schema.org
    full_address_string = address_data.get('full_address_string', address) # Use generated full string, fallback to original 'address' if parsing failed
    street_address = address_data.get('street_address', '') # For Schema.org

    descriptions = datos.get('descriptions', '').strip()
    if not descriptions:
        ciudad = ''
        if address:
            partes = address.split(',')
            if len(partes) >= 2: ciudad = partes[-2].strip()
        descriptions = f'Somos especialistas en {category.lower()} con experiencia comprobada'
        if ciudad: descriptions += f' en {ciudad}'
        descriptions += '. Brindamos atención personalizada con tecnología de vanguardia y un equipo de profesionales altamente capacitados.'

    horarios = parsear_horarios(datos.get('open_hours', ''))
    canonical_url = generar_canonical_url(slug)
    meta_tags = generar_meta_tags(datos, canonical_url, address_data)
    faqs = generar_faqs(category, title, datos, address_data, horarios)
    
    # Generate Google Maps URL
    google_maps_url = ''
    if latitude and longitude:
        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"

    # Default values for now, will need CSV fields later
    price_range = datos.get('price_range', '')
    search_term_string = datos.get('search_term_string', title)
    service_description = descriptions # Using the main description for now

    # Newly added dynamic content
    html = html.replace('{google_maps_url}', google_maps_url)
    html = html.replace('{services_heading}', f'Nuestros Servicios de {category}')
    html = html.replace('{gallery_heading}', f'Galería de Imágenes de {title}')
    html = html.replace('{price_range}', price_range)
    html = html.replace('{search_term_string}', search_term_string)
    html = html.replace('{service_description}', service_description)

    map_iframe_src = "https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d!2d-6.8143!3d35.67445!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1ses!2sar"
    if latitude and longitude:
        map_iframe_src = f"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3022.68420600377!2d{longitude}!3d{latitude}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2z{latitude},{longitude}!5e0!3m2!1ses!2sar!4v1625000000000!5m2!1ses!2sar"
    html = html.replace('{map_iframe_src}', map_iframe_src)
    
    html = html.replace('{title}', title)
    html = html.replace('{category}', category)
    html = html.replace('{phone}', phone)
    html = html.replace('{address}', full_address_string) # Use the newly constructed full address string
    html = html.replace('{website}', website)
    html = html.replace('{thumbnail}', thumbnail)
    html = html.replace('{descriptions}', descriptions)
    html = html.replace('{emails}', emails)
    html = html.replace('{email}', emails.split(',')[0] if emails else '')
    html = html.replace('{latitude}', str(latitude))
    html = html.replace('{longitude}', str(longitude))
    html = html.replace('{city}', city)
    html = html.replace('{region}', region)
    html = html.replace('{postal_code}', postal_code)
    html = html.replace('{country}', country)
    html = html.replace('{street_address}', street_address)
    html = html.replace('{meta_description}', meta_tags['meta_description'])
    html = html.replace('{canonical_url}', canonical_url)
    html = html.replace('{og_title}', meta_tags['og_title'])
    html = html.replace('{og_description}', meta_tags['og_description'])
    html = html.replace('{og_image}', meta_tags['og_image'])
    html = html.replace('{twitter_title}', meta_tags['twitter_title'])
    html = html.replace('{twitter_description}', meta_tags['twitter_description'])
    html = html.replace('{twitter_image}', meta_tags['twitter_image'])
    html = html.replace('{logo_url}', meta_tags['logo_url'])

    # --- A1: Generate Service Cards from category and descriptions ---
    # Helper function to generate service details
    def generate_service_details(cat, desc, service_num):
        base_title = f"{cat} - Servicio {service_num}"
        base_desc = f"Detalles del servicio {service_num} de {cat}: {desc[:50]}..."
        image_path = f"../assets/images/service cover {service_num}.webp"
        alt_text = f"Imagen de {base_title}"
        
        # Simple variations based on service number and category for better SEO and uniqueness
        if service_num == 1:
            title = f"{cat} General"
            description = f"Expertos en {cat.lower()} general para todas tus necesidades. {desc[:80]}."
        elif service_num == 2:
            title = f"Especialistas en {cat}"
            description = f"Nuestro equipo de especialistas ofrece soluciones avanzadas en {cat.lower()}. {desc[50:130]}."
        elif service_num == 3:
            title = f"Atención Profesional de {cat}"
            description = f"Brindamos atención personalizada y profesional en {cat.lower()}. {desc[100:180]}."
        elif service_num == 4:
            title = f"Soluciones Innovadoras en {cat}"
            description = f"Ofrecemos las más recientes innovaciones y técnicas en {cat.lower()}. {desc[150:230]}."
        elif service_num == 5:
            title = f"Mantenimiento y Prevención de {cat}"
            description = f"Servicios completos de mantenimiento y prevención para asegurar tu bienestar en {cat.lower()}. {desc[200:280]}."
        elif service_num == 6:
            title = f"Diagnóstico y Tratamiento de {cat}"
            description = f"Diagnóstico preciso y tratamientos efectivos para cualquier problema de {cat.lower()}. {desc[250:330]}."
        else:
            title = base_title
            description = base_desc
        
        # Ensure description is not empty and has a minimum length
        if not description.strip() or len(description.strip()) < 30:
            description = f"Servicios de alta calidad en {cat.lower()} para satisfacer todas tus expectativas."

        return {
            'image': image_path,
            'alt': alt_text,
            'title': title,
            'description': description
        }

    for i in range(1, 7): # For services 1 to 6
        service_details = generate_service_details(category, descriptions, i)
        html = html.replace(f'{{service_{i}_image}}', service_details['image'])
        html = html.replace(f'{{service_{i}_alt}}', service_details['alt'])
        html = html.replace(f'{{service_{i}_title}}', service_details['title'])
        html = html.replace(f'{{service_{i}_description}}', service_details['description'])
    # --- End A1 ---

    # --- B1: Implement "Sobre nosotros" (About Us) ---
    about_us_heading_1 = "Experiencia y Profesionalismo"
    about_us_description_1 = f"En {title} contamos con años de experiencia brindando servicios de {category.lower()}. Nuestro equipo de profesionales se mantiene actualizado con las últimas técnicas y tecnologías del sector para ofrecerte la mejor atención. {descriptions[:150]}"

    about_us_heading_2 = "¿Por qué elegirnos?"
    about_us_description_2 = f"Nos destacamos por nuestra atención personalizada y compromiso con cada cliente. En {title} entendemos que cada caso es único, por eso diseñamos soluciones específicas que se adaptan a tus necesidades. Trabajamos con equipamiento de última generación y mantenemos los más altos estándares de calidad en cada servicio que brindamos. {descriptions[100:250]}"
    
    # Fallback if descriptions is too short
    if len(descriptions) < 250:
        about_us_description_1 = f"En {title} somos líderes en {category.lower()}, ofreciendo soluciones innovadoras y de alta calidad. Nuestro compromiso es garantizar la satisfacción de cada cliente."
        about_us_description_2 = f"Elegir a {title} significa optar por un servicio confiable y eficiente. Nos dedicamos a proporcionar resultados excepcionales, adaptándonos a las necesidades específicas de cada proyecto."

    html = html.replace('{about_us_heading_1}', about_us_heading_1)
    html = html.replace('{about_us_description_1}', about_us_description_1)
    html = html.replace('{about_us_heading_2}', about_us_heading_2)
    html = html.replace('{about_us_description_2}', about_us_description_2)
    # --- End B1 ---

    # --- C1: Implement Slick Carousel ---
    carousel_phrases = [
        f"Tu aliado en {category.lower()} en {city}",
        f"Soluciones a medida para {title}",
        f"Calidad y experiencia en cada servicio de {category.lower()}",
        f"Transformando ideas en realidad con {title}"
    ]
    
    # If descriptions is available, try to extract some keywords or phrases
    if descriptions:
        desc_sentences = [s.strip() for s in descriptions.split('.') if s.strip()]
        if len(desc_sentences) >= 1: carousel_phrases[1] = desc_sentences[0]
        if len(desc_sentences) >= 2: carousel_phrases[2] = desc_sentences[1]
        if len(desc_sentences) >= 3: carousel_phrases[3] = desc_sentences[2]

    slick_carousel_items = ""
    for phrase in carousel_phrases:
        slick_carousel_items += f"""
            <li class="slider-wrapper d-flex align-items-center justify-content-center">
              {phrase}
            </li>"""
    html = html.replace('{slick_carousel_items}', slick_carousel_items)
    # --- End C1 ---

    # --- D1: Implement Banner ---
    banner_1_title = f"Descubre lo mejor de {category} con {title}"
    banner_1_description = f"Explora nuestros servicios de {category.lower()} y encuentra la solución perfecta para tus necesidades. {descriptions[:100]}."

    banner_2_title = f"Contacto directo con expertos en {category}"
    banner_2_description = f"¿Necesitas asesoramiento? Nuestro equipo de {category.lower()} está listo para ayudarte. {descriptions[50:150]}."

    # Fallback if descriptions is too short
    if len(descriptions) < 150:
        banner_1_description = f"Ofrecemos soluciones integrales en {category.lower()} con la calidad y profesionalismo que nos caracteriza."
        banner_2_description = f"Comunícate con nosotros para obtener más información sobre cómo podemos asistirte en tus proyectos de {category.lower()}."

    html = html.replace('{banner_1_title}', banner_1_title)
    html = html.replace('{banner_1_description}', banner_1_description)
    html = html.replace('{banner_2_title}', banner_2_title)
    html = html.replace('{banner_2_description}', banner_2_description)
    # --- End D1 ---

    # --- E: Implement Reviews (existing columns) ---
    rating_value = datos.get('rating_value', '5.0')  # Default to 5.0 if not provided
    review_count = datos.get('review_count', '0')   # Default to 0 if not provided
    reviews_per_rating = datos.get('reviews_per_rating', '{}') # Default to empty JSON string

    html = html.replace('{rating_value}', str(rating_value))
    html = html.replace('{review_count}', str(review_count))

    # Format reviews_per_rating for display
    reviews_per_rating_display = ""
    try:
        if reviews_per_rating:
            reviews_data = json.loads(reviews_per_rating)
            if isinstance(reviews_data, dict):
                formatted_parts = []
                for rating, count in sorted(reviews_data.items(), key=lambda item: int(item[0]), reverse=True):
                    if count > 0:
                        formatted_parts.append(f"{rating} estrellas: {count}")
                reviews_per_rating_display = f"({', '.join(formatted_parts)})"
    except json.JSONDecodeError:
        reviews_per_rating_display = "" # Malformed JSON

    html = html.replace('{reviews_per_rating_display}', reviews_per_rating_display)

    # For individual reviews, since no specific data source is provided, use empty strings
    for i in range(1, 4): # For reviews 1 to 3
        html = html.replace(f'{{review_{i}_author}}', '')
        html = html.replace(f'{{review_{i}_rating}}', '')
        html = html.replace(f'{{review_{i}_text}}', '')
        html = html.replace(f'{{review_{i}_date}}', '')
    # The reviews slider div will remain empty as no data source is provided for it.
    # --- End E ---

    # --- F1: Implement Social Links (default to generic/empty) ---
    html = html.replace('{social_facebook}', datos.get('social_facebook', ''))
    html = html.replace('{social_instagram}', datos.get('social_instagram', ''))
    html = html.replace('{social_twitter}', datos.get('social_twitter', ''))
    html = html.replace('{social_linkedin}', datos.get('social_linkedin', ''))
    # --- End F1 ---

    # --- Gallery: Populate dynamic_gallery_items ---
    dynamic_gallery_items = generar_galeria_html(imagenes_gallery)
    html = html.replace('{dynamic_gallery_items}', dynamic_gallery_items)
    # --- End Gallery ---

    # Reemplazo de variables de horarios
    html = html.replace('{weekday_opens}', horarios['weekday_opens'])
    html = html.replace('{weekday_closes}', horarios['weekday_closes'])
    html = html.replace('{saturday_opens}', horarios['saturday_opens'])
    html = html.replace('{saturday_closes}', horarios['saturday_closes'])

    # Reemplazo de FAQs
    for i, (pregunta, respuesta) in enumerate(faqs):
        html = html.replace(f'{{faq_question_{i+1}}}', pregunta)
        html = html.replace(f'{{faq_answer_{i+1}}}', respuesta)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    # --- Verification Step: Check for unpopulated placeholders ---
    unpopulated_placeholders = re.findall(r'\{[a-zA-Z0-9_]+\}', html)
    if unpopulated_placeholders:
        print(f"   ⚠️  Advertencia: Se encontraron placeholders no poblados en {output_path.name}: {', '.join(set(unpopulated_placeholders))}")
    # --- End Verification Step ---
    
    return output_path


def leer_csv_original(file_path):
    """Lee el archivo CSV de origen y retorna lista de diccionarios"""
    datos = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('title'):
                    datos.append(row)
    except Exception as e:
        print(f"   ⚠️  Error leyendo {file_path.name}: {e}")
    return datos

def generar_workflow_personalizado(workflow_template, title, backlink, category):
    """
    Genera el workflow de WhatsApp con placeholders reemplazados.

    Parámetros:
        workflow_template: Diccionario con la estructura del workflow
        title: Nombre del negocio
        backlink: URL de la landing page del negocio
        category: Categoría del negocio

    Retorna:
        String JSON con el workflow personalizado
    """
    if not workflow_template:
        return ""

    # Crear copia profunda del workflow
    workflow_personalizado = json.loads(json.dumps(workflow_template))

    # Reemplazar placeholders en cada paso del funnel
    if 'funnel_steps' in workflow_personalizado:
        for step in workflow_personalizado['funnel_steps']:
            if 'message' in step:
                step['message'] = step['message'].replace('{title}', title)
                step['message'] = step['message'].replace('{backlink}', backlink)
                step['message'] = step['message'].replace('{category}', category)

    # Retornar como JSON string compacto (sin saltos de línea para CSV)
    return json.dumps(workflow_personalizado, ensure_ascii=False, separators=(',', ':'))

def generar_whatsapp_notes(workflow_json_string, numero_telefono):
    """
    Genera las notas de WhatsApp en formato de texto plano para una columna de CSV,
    incluyendo el enlace de WhatsApp, el número y el mensaje del paso correspondiente.

    Parámetros:
        workflow_json_string: String JSON con el workflow personalizado
                              (placeholders como title, backlink, category ya reemplazados).
        numero_telefono: Número de teléfono en formato +54... (debe incluir el +).

    Retorna:
        String con todas las notas de WhatsApp generadas para el workflow,
        en el formato "https://wa.me/{numero_telefono} - {mensaje_del_paso}".
        Cada paso se separa por dos saltos de línea.
    """
    if not workflow_json_string or not numero_telefono:
        return ""

    try:
        # El workflow_json_string es un JSON string compacto, lo necesitamos parsear
        workflow = json.loads(workflow_json_string)
    except json.JSONDecodeError:
        print(f"Error al decodificar el workflow JSON en generar_whatsapp_notes: {workflow_json_string}")
        return ""

    notas_generadas = []
    
    # Formato de enlace de WhatsApp: https://wa.me/numerodetelefono
    # Se asume que numero_telefono ya viene en formato correcto (+54...)
    # y que wa.me no requiere el '+'
    enlace_whatsapp_base = f"https://wa.me/{numero_telefono.replace('+', '')}"

    if 'funnel_steps' in workflow and isinstance(workflow['funnel_steps'], list):
        for datos_paso in workflow['funnel_steps']:
            mensaje = datos_paso.get('message', '').strip()
            if mensaje: # Asegurarse de que el mensaje no esté vacío
                # Formato solicitado: "enlace de whatsapp con número y guión y mensaje del paso correspondiente"
                notas_generadas.append(f"{enlace_whatsapp_base} - {mensaje}")
    
    return "\n\n".join(notas_generadas)

def main():
    base_path = PROJECT_ROOT / "scripts" / "web_designer" / "landing-page-generator"
    template_path = base_path / 'template.html'
    
    # 1. DEFINIR ESTRUCTURA DEL CSV DE CONTACTOS (Hardcoded)
    final_headers = [
        "First Name", "Middle Name", "Last Name", "Phonetic First Name", 
        "Phonetic Middle Name", "Phonetic Last Name", "Name Prefix", 
        "Name Suffix", "Nickname", "File As", "Organization Name", 
        "Organization Title", "Organization Department", "Birthday", 
        "Notes", "Photo", "Labels", "E-mail 1 - Label", "E-mail 1 - Value", 
        "Phone 1 - Label", "Phone 1 - Value", "Website 1 - Label", 
        "Website 1 - Value"
    ]
    print("✅ Estructura de CSV de destino definida (hardcoded).")

    # NOTA IMPORTANTE: Los CSV de entrada son generados por un scrap y su estructura
    # no puede modificarse añadiendo nuevas columnas.
    # Toda la generación de contenido dinámico debe basarse en las columnas existentes.

    # Rutas de entrada y salida
    input_dir = base_path # Input CSVs are now expected in the script's base directory
    output_base_dir = base_path
    output_csv_path = output_base_dir / 'contactos_google.csv'
    
    csv_files = list(input_dir.glob('*.csv'))



    if not csv_files:
        print(f"❌ No se encontraron archivos CSV de datos en: {input_dir}")
        return

    all_processed_rows = []
    
    print("\n" + "="*70)
    print("  🚀 GENERADOR DE LANDING PAGES Y CSV DE CONTACTOS")
    print("="*70)

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_html = f.read()
    except FileNotFoundError:
        print(f"❌ Error: No se encontró la plantilla HTML en {template_path}")
        return

    # Usar plantilla de workflow de WhatsApp hardcodeada
    print("✅ Workflow de WhatsApp: Activado para columna Notes.")

    for csv_path in csv_files:
        


        # Adjusted `file_part` generation:
        file_part_stem = csv_path.stem # e.g., "aluminio lanus"
        
        # Split by space or hyphen, take the first two parts
        parts = re.split(r'[ -]', file_part_stem)
        file_part = " ".join(parts[:2]).strip()
        
        print(f"\n\n📂 Procesando: {csv_path.name} (Base de nombre: '{file_part}')")

        datos_negocios = leer_csv_original(csv_path)
        if not datos_negocios:
            continue
        
        print(f"   -> Se encontraron {len(datos_negocios)} negocios.")

        # Cargar caché de imágenes
        cache_file = output_base_dir / '.image_cache.json'
        cache_data = cargar_cache_imagenes(cache_file)


        # Use crear_slug on file_part for the directory name, to ensure it's valid for a folder.
        category_slug_for_dir = crear_slug(file_part)

        for index, row in enumerate(datos_negocios):
            # Crear una fila de salida vacía con todas las cabeceras requeridas
            output_row = {header: "" for header in final_headers}

            # --- Aplicar lógica de mapeo y transformación ---

            # 1. First Name
            country, country_code = '', ''
            complete_address = row.get('complete_address', '')
            if complete_address:
                try:
                    country = json.loads(complete_address).get('country', '')
                    if country: country_code = COUNTRY_CODES.get(country, '')
                except: pass
            output_row['First Name'] = f"{file_part} {country_code}".strip()

            # 2. Last Name & Organization Name
            title = row.get('title', '')
            output_row['Last Name'] = title
            output_row['Organization Name'] = title

            # 3. Phone 1 - Value (priorizando WhatsApp)
            raw_phone = row.get('phone', '')
            website = row.get('website', '')
            order_online_field = row.get('order_online', '')
            is_phone_formatted, phone_value, priority = format_phone_number(raw_phone, website, order_online_field)
            output_row['Phone 1 - Value'] = phone_value

            # 4. E-mail 1 - Value
            emails = row.get('emails', '')
            output_row['E-mail 1 - Value'] = emails.split(',')[0].strip() if emails else ''

            # 5. Website 1 - Value
            output_row['Website 1 - Value'] = row.get('website', '')

            # 6. Notes - Generar hipervínculos de WhatsApp para el funnel
            # Generar slug y backlink para el workflow
            slug = crear_slug(title)
            backlink = f"https://google.selvaggiesteban.dev/{category_slug_for_dir}/{slug}.html"
            category = row.get('category', 'Servicio')

            # Generar workflow con placeholders reemplazados
            workflow_personalizado = generar_workflow_personalizado(
                WHATSAPP_WORKFLOW_TEMPLATE,
                title,
                backlink,
                category
            )

            # Generar hipervínculos de WhatsApp a partir del workflow
            whatsapp_notes = generar_whatsapp_notes(workflow_personalizado, phone_value)
            output_row['Notes'] = whatsapp_notes

            all_processed_rows.append(output_row)

            # --- Generación de Landing Page (funcionalidad original) ---
            # category y slug ya fueron definidos arriba para el workflow
            # category_slug_for_dir también fue definido antes del loop

            output_dir = output_base_dir / category_slug_for_dir
            output_dir.mkdir(parents=True, exist_ok=True)
            assets_src = base_path / 'assets'
            assets_dst = output_base_dir / 'assets'
            if not assets_dst.exists():
                shutil.copytree(assets_src, assets_dst)

            gallery_dir = assets_dst / 'images' / 'gallery'
            gallery_dir.mkdir(parents=True, exist_ok=True)

            output_file = output_dir / f'{slug}.html'
            
            print(f"   -> [{index + 1}/{len(datos_negocios)}] Generando LP para: {title}")
            
            address_data = extraer_datos_direccion(row.get('address', ''), row.get('complete_address', ''))

            # Procesar imágenes para la landing page
            imagenes_gallery = procesar_imagenes_negocio(row, gallery_dir, category, title, index, cache_data)
            
            # Generar landing page
            generar_landing_page(template_html, row, output_file, imagenes_gallery, slug, address_data)

        # Guardar caché actualizado para este CSV
        guardar_cache_imagenes(cache_file, cache_data)


    # 4. ESCRIBIR EL CSV DE CONTACTOS FINAL
    if all_processed_rows:
        print(f"\n📝 Escribiendo CSV de contactos en: {output_csv_path}")
        try:
            with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=final_headers)
                writer.writeheader()
                writer.writerows(all_processed_rows)
            print(f"   ✅ Archivo '{output_csv_path.name}' generado con {len(all_processed_rows)} contactos.")
        except Exception as e:
            print(f"   ❌ Error al escribir el CSV de contactos: {e}")

    print("\n" + "="*70)
    print(f"🎉 ¡Proceso completado!")
    print("======================================================================")

if __name__ == "__main__":
    main()
