import sqlite3
import requests
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse

DB_PATH = r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\data\inputs\contacts.db"

EMAILS = [
    "administracion@bufeterodriguezmerino.com",
    "administracion@defensa-legal.com",
    "abogadocaza@gmail.com",
    "admin@abogadosce.es",
    "administracion@asesoreslegalesvalladolid.es",
    "adv54a@hotmail.com",
    "alvaro@vela-abogados.com",
    "antonio@antonioberdugoabogado.es",
    "administracion@lilianamiguel.es",
    "anamartinvela@icava.org",
    "atencionalcliente@abogadosgamo.com",
    "arlanzonabogados@gmail.com",
    "analeon@analeon.com",
    "asesoreslegales@asesoreslegalesvalladolid.es",
    "beatriz@antonioberdugoabogado.es",
    "eraynal@sac-law.mx",
    "contacto@solucionabogados.com",
    "contacto@pintoarranz.com",
    "contacto@tresierrayasociados.com",
    "consultas@abogadosfides.es",
    "bnicolasabogada@gmail.com",
    "info@abogados.one",
    "ignaciofraileabogados@gmail.com",
    "contactosdiazyasociados@gmail.com",
    "elena@tresierrayasociados.com",
    "fernando@tresierrayasociados.com",
    "info@alvarezcalzada.es",
    "info@abogadosmms.com",
    "gabinete@aggabogados.es",
    "contacto@ponientelegal.es",
    "info@atenabogados.com",
    "info@fenollera-abogados.com",
    "info@garciamartinabogados.com",
    "info@atlabogados.es",
    "antonio@atlabogados.es",
    "info@cuadradelarocaabogada.com",
    "info@djfabogados.com",
    "info@magnumabogados.com",
    "info@molpeceresabogados.com",
    "enrique@tresierrayasociados.com",
    "info@martosyasociados.com",
    "info@sergiocastroabogados.com",
    "jelure90@gmail.com",
    "jocriado@gmail.com",
    "info@clicklaboral.es",
    "jalcoba@alcobalaw.com",
    "negotia@abogadosnegotia.es",
    "legal@cuadrilleroyasociados.es",
    "monsalveabogados@gmail.com",
    "juanpa@icava.org",
    "mjvina@abogadosyconsultores.es",
    "jesus@castrocordovabogados.es",
    "info@iberforovalladolid.eu",
    "mjolmedo@iberforovalladolid.eu",
    "valladolid@garrigues.com",
    "info@parisduran.com",
    "diego@parisduran.com",
    "contacto@diazyasociados.es",
    "vym@vicenteymatanza.com",
    "documentospg@outlook.com",
    "pablojusto@icamelilla.com",
    "pgurpegui@icava.org",
    "patriciagutierrez@icaburgos.com",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

SPANISH_CITIES = [
    "Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza", "Malaga", "Murcia",
    "Palma", "Las Palmas", "Bilbao", "Alicante", "Cordoba", "Valladolid",
    "Vigo", "Gijon", "Granada", "A Coruna", "Vitoria", "Santa Cruz de Tenerife",
    "Pamplona", "Santander", "Burgos", "Salamanca", "Alcala de Henares",
    "Logrono", "Badajoz", "Castellon", "Albacete", "San Sebastian", "Cadiz",
    "Huelva", "Tarragona", "Leon", "Jaen", "Oviedo", "Girona", "Lleida",
    "Caceres", "Ciudad Real", "Toledo", "Marbella", "Irun", "Sanlucar de Barrameda",
]

SPAIN_PROVINCES = {
    "Madrid": "Madrid", "Barcelona": "Barcelona", "Valencia": "Valencia",
    "Sevilla": "Sevilla", "Zaragoza": "Zaragoza", "Malaga": "Malaga",
    "Valladolid": "Valladolid", "Bilbao": "Vizcaya", "Burgos": "Burgos",
    "Salamanca": "Salamanca", "Leon": "Leon", "Oviedo": "Asturias",
    "Girona": "Girona", "Pamplona": "Navarra", "San Sebastian": "Guipuzcoa",
    "Logrono": "La Rioja", "Vitoria": "Alava", "Tarragona": "Tarragona",
    "Lleida": "Lleida", "Castellon": "Castellon", "Caceres": "Caceres",
    "Toledo": "Toledo", "Badajoz": "Badajoz", "Cadiz": "Cadiz",
    "Huelva": "Huelva", "Jaen": "Jaen", "Ciudad Real": "Ciudad Real",
    "Albacete": "Albacete", "Gijon": "Asturias", "A Coruna": "A Coruna",
}


def extract_domain(email):
    return email.split("@")[1].lower()


def build_website_url(domain):
    return "https://" + domain


def scrape_website(url):
    """Scrape website for company info."""
    result = {"title": "", "city": "", "sector": "", "phone": "", "country": "Espana"}

    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = "https://" + url

        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Title
        if soup.title and soup.title.string:
            result["title"] = soup.title.string.strip()[:200]

        text = soup.get_text(separator=" ", strip=True)

        # Phone
        phone_patterns = [
            r'(?:tel|telefono|phone|fax)[\s:]*([+\d\s\-()]{7,20})',
            r'(\+34[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3})',
            r'(\+34[\s\-]?\d{2}[\s\-]?\d{4}[\s\-]?\d{3})',
            r'(9\d{2}[\s\-]?\d{3}[\s\-]?\d{3})',
            r'(8\d{2}[\s\-]?\d{3}[\s\-]?\d{3})',
            r'(6\d{2}[\s\-]?\d{3}[\s\-]?\d{3})',
            r'(7\d{2}[\s\-]?\d{3}[\s\-]?\d{3})',
        ]
        for pat in phone_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                phone = m.group(1) if m.lastindex else m.group(0)
                phone = re.sub(r'[^\d+\-() ]', '', phone).strip()
                if len(phone) >= 7:
                    result["phone"] = phone[:30]
                    break

        # City detection
        for city in SPANISH_CITIES:
            if re.search(r'\b' + re.escape(city) + r'\b', text, re.IGNORECASE):
                result["city"] = city
                break

        # If no city found, try meta tags
        if not result["city"]:
            meta_loc = soup.find("meta", attrs={"name": "geo.position"}) or \
                       soup.find("meta", attrs={"name": "ICBM"})
            if meta_loc and meta_loc.get("content"):
                parts = meta_loc["content"].split(";")
                if len(parts) >= 2:
                    # Try reverse geocoding or just use domain hints
                    pass

        # Sector detection
        sector_keywords = {
            "abogado": "Abogacia",
            "law": "Abogacia",
            "legal": "Abogacia",
            "advocat": "Abogacia",
            "asesoria": "Asesoria",
            "asesor": "Asesoria",
            "consultoria": "Consultoria",
            "consultor": "Consultoria",
            "contable": "Contabilidad",
            "contabilidad": "Contabilidad",
            "economia": "Economia",
            "empresa": "Empresas",
            "inmobiliari": "Inmobiliario",
            "inmueble": "Inmobiliario",
            "seguro": "Seguros",
            "seguridad": "Seguridad",
            "fiscal": "Fiscal",
            "laboral": "Laboral",
            "tributar": "Tributario",
            "mercantil": "Mercantil",
            "penal": "Penal",
            "familia": "Familia",
            "propiedad": "Propiedad",
            "intelectual": "Propiedad Intelectual",
        }
        text_lower = text.lower() + " " + (result["title"].lower() if result["title"] else "")
        for kw, sec in sector_keywords.items():
            if kw in text_lower:
                result["sector"] = sec
                break

        if not result["sector"]:
            result["sector"] = "Abogacia"

    except Exception as e:
        pass

    return result


def get_rowid_for_email(conn, email):
    row = conn.execute("SELECT ROWID FROM lead WHERE primary_email = ?", (email,)).fetchone()
    return row[0] if row else None


def main():
    conn = sqlite3.connect(DB_PATH)
    updated = 0
    scraped = 0
    failed = 0

    for email in EMAILS:
        domain = extract_domain(email)
        rowid = get_rowid_for_email(conn, email)
        if not rowid:
            print(f"SKIP (not in DB): {email}")
            continue

        website_url = build_website_url(domain)
        print(f"Scraping {website_url} ...")

        data = scrape_website(website_url)
        scraped += 1

        # Get current values
        current = conn.execute("""
            SELECT m.title, m.sector, m.city, m.country,
                   l.website, l.phone
            FROM main m
            JOIN lead l ON m.ROWID = l.ROWID
            WHERE m.ROWID = ?
        """, (rowid,)).fetchone()

        if not current:
            continue

        cur_title, cur_sector, cur_city, cur_country, cur_website, cur_phone = current

        # Update main table
        new_title = data["title"] if data["title"] and (not cur_title or cur_title == "website") else cur_title
        new_sector = data["sector"] if data["sector"] and (not cur_sector or cur_sector == "website") else cur_sector
        new_city = data["city"] if data["city"] and (not cur_city or cur_city == "website") else cur_city
        new_country = data["country"] if data["country"] and (not cur_country or cur_country == "website") else cur_country

        # Always fix website URL
        new_website = website_url if (not cur_website or cur_website == "website") else cur_website

        # Update lead table
        new_phone = data["phone"] if data["phone"] and (not cur_phone or cur_phone == "website") else cur_phone

        conn.execute("""
            UPDATE main SET title = ?, sector = ?, city = ?, country = ?
            WHERE ROWID = ?
        """, (new_title, new_sector, new_city, new_country, rowid))

        conn.execute("""
            UPDATE lead SET website = ?, phone = ?
            WHERE ROWID = ?
        """, (new_website, new_phone, rowid))

        changes = []
        if new_title != cur_title: changes.append("title")
        if new_sector != cur_sector: changes.append("sector")
        if new_city != cur_city: changes.append("city")
        if new_country != cur_country: changes.append("country")
        if new_website != cur_website: changes.append("website")
        if new_phone != cur_phone: changes.append("phone")

        if changes:
            updated += 1
            print(f"  UPDATED {email}: {', '.join(changes)}")
            print(f"    title={new_title}, city={new_city}, sector={new_sector}, phone={new_phone}")
        else:
            print(f"  NO CHANGE {email}")

        time.sleep(0.5)

    conn.commit()
    conn.close()

    print(f"\nDone: {scraped} scraped, {updated} updated")


if __name__ == "__main__":
    main()
