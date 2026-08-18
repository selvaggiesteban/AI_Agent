#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ecommerce_competitor_research.py

- Scrapea productos de una tienda Tienda Nube (lanuscomputacion.mitiendanube.com)
- Busca competidores/precios en:
  - MercadoLibre (API Oficial)
  - Google (API de búsqueda personalizada de JSON) -> resultados web
  - Google Shopping (SerpApi o proveedor similar) -> precios más fiables
  - Facebook Marketplace -> marcador de posición (sin raspado HTML)

Salida:
- output.csv
- consola: "{product}, {competitor}, {price}, {url}, {suggested_price}"

Requisitos:
pip install requests beautifulsoup4 rapidfuzz pandas pyyaml lxml python-dotenv
"""

from __future__ import annotations

import re
import time
import json
import csv
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
import pandas as pd
import yaml
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# ----------------------------
# Configuración / Modelos
# ----------------------------

DEFAULT_CONFIG_YAML: str = """
store:
  base_url: "https://lanuscomputacion.mitiendanube.com"
  products_path: "/productos"
  pages: 8
  timeout_sec: 30
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

sources:
  mercadolibre:
    enabled: true
    site_id: "MLA"
    max_results: 15
  google_custom_search:
    enabled: false
    api_key: "${GOOGLE_API_KEY}"
    cx: "${GOOGLE_CX}"
    max_results: 5
  serpapi_google_shopping:
    enabled: false
    api_key: "${SERPAPI_API_KEY}"
    gl: "ar"
    hl: "en"
    max_results: 10

matching:
  # Similitud mínima (0-100) entre el título del competidor y tu producto
  min_similarity: 65

pricing:
  # Margen como "markup": 100% => multiplicar base * (1 + 1.00) => x2
  margin_pct: 100
  # Cómo calcular el precio base antes del margen
  # opciones: "min_competitor", "median_competitor", "our_current_price"
  base_strategy: "min_competitor"
  # Reglas extra:
  round_to: 10 # redondeo al múltiplo más cercano (10, 50, 100, etc.)
  min_price: 0 # suelo absoluto
  max_price: 0 # 0 = sin techo

synonyms:
  # Archivo opcional para sinónimos específicos por términos/marcas/modelos
  synonyms_file: "synonyms.json"

output:
  csv_path: "output.csv"
  sleep_between_requests_sec: 0.4
"""

DEFAULT_SYNONYMS_JSON: Dict[str, List[str]] = {
  "headphones": ["earphones", "headset", "in-ear", "earbuds"],
  "speaker": ["loudspeaker", "bluetooth speaker", "horn"],
  "charger": ["adapter", "power supply"],
  "cable": ["cord", "wiring", "usb cable"],
  "powerbank": ["external battery", "portable charger", "portable battery"],
}

@dataclass
class StoreProduct:
  """Representa un producto de la propia tienda"""
  name: str
  url: str
  our_price_ars: Optional[float] = None

@dataclass
class CompetitorOffer:
  """Representa una oferta de un competidor"""
  product_name: str
  competitor_name: str
  competitor_price: Optional[float]
  currency: str
  url: str
  similarity: int
  suggested_price: Optional[float]

# ----------------------------
# Utilidades
# ----------------------------

def load_or_create_config(path: str = "config.yaml") -> Dict[str, Any]:
  """Carga o crea el archivo de configuración YAML"""
  if not os.path.exists(path):
    # Reemplazar variables de entorno en la plantilla predeterminada
    config_content = DEFAULT_CONFIG_YAML
    config_content = config_content.replace("${GOOGLE_API_KEY}", os.environ.get("GOOGLE_API_KEY", "YOUR_API_KEY"))
    config_content = config_content.replace("${GOOGLE_CX}", os.environ.get("GOOGLE_CX", "YOUR_CX"))
    config_content = config_content.replace("${SERPAPI_API_KEY}", os.environ.get("SERPAPI_API_KEY", "YOUR_SERPAPI_KEY"))
    
    with open(path, "w", encoding="utf-8") as f:
      f.write(config_content)
    print(f"[i] Creado {path}. Edítalo y ejecútalo de nuevo.")
    
  with open(path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
    # Asegurar que las claves de las variables de entorno se carguen correctamente si el archivo ya existe
    # pero tiene los placeholders de la plantilla
    if config["sources"]["google_custom_search"]["api_key"] == "${GOOGLE_API_KEY}":
        config["sources"]["google_custom_search"]["api_key"] = os.environ.get("GOOGLE_API_KEY", "YOUR_API_KEY")
    if config["sources"]["google_custom_search"]["cx"] == "${GOOGLE_CX}":
        config["sources"]["google_custom_search"]["cx"] = os.environ.get("GOOGLE_CX", "YOUR_CX")
    if config["sources"]["serpapi_google_shopping"]["api_key"] == "${SERPAPI_API_KEY}":
        config["sources"]["serpapi_google_shopping"]["api_key"] = os.environ.get("SERPAPI_API_KEY", "YOUR_SERPAPI_KEY")
    return config

def load_or_create_synonyms(path: str) -> Dict[str, List[str]]:
  """Carga o crea el archivo de sinónimos JSON"""
  if not os.path.exists(path):
    with open(path, "w", encoding="utf-8") as f:
      json.dump(DEFAULT_SYNONYMS_JSON, f, ensure_ascii=False, indent=2)
    print(f"[i] Creado {path} con ejemplos. Personalízalo para obtener mejores resultados.")
  with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
    return {str(k).strip().lower(): [str(x).strip() for x in v] for k, v in data.items()}

def parse_ars_money(text: str) -> Optional[float]:
  """Convierte cadenas como "$11,505.00" o "11,505.00" a float 11505.00"""
  if not text:
    return None
  t = text.strip()
  t = re.sub(r"[^0-9\.,]", "", t)
  if not t:
    return None
  if "," in t:
    t = t.replace(",", "")
  try:
    return float(t)
  except ValueError:
    return None

def normalize_query(s: str) -> str:
  """Normaliza una cadena de búsqueda"""
  s = s.lower().strip()
  s = re.sub(r"[()[]{}]", " ", s)
  s = re.sub(r"[^a-z0-9\s\-.]", " ", s, flags=re.IGNORECASE)
  s = re.sub(r"\s+", " ", s).strip()
  return s

def expand_queries(product_name: str, synonyms: Dict[str, List[str]]) -> List[str]:
  """Genera variantes de búsqueda basadas en sinónimos y normalización"""
  base = product_name.strip()
  norm = normalize_query(base)

  tokens = norm.split()
  queries = {base, norm}

  stop = {"quality", "premium", "best", "new", "original", "aaa", "off"}
  filtered_tokens = [t for t in tokens if len(t) > 2 and t not in stop]
  if filtered_tokens:
    queries.add(" ".join(filtered_tokens))

  for i, tok in enumerate(filtered_tokens):
    if tok in synonyms:
      for syn in synonyms[tok]:
        alt_tokens = filtered_tokens.copy()
        alt_tokens[i] = normalize_query(syn)
        queries.add(" ".join([t for t in alt_tokens if t]))

  if "pro" in filtered_tokens:
    queries.add(" ".join([t for t in filtered_tokens if t != "pro"]))
  if "max" in filtered_tokens:
    queries.add(" ".join([t for t in filtered_tokens if t != "max"]))

  final = []
  for q in queries:
    q2 = q.strip()
    if len(q2) >= 4:
      final.append(q2)
  
  return sorted(final)[:8]

# ----------------------------
# Raspador de Tienda Nube
# ----------------------------

def http_get(session: requests.Session, url: str, timeout: int, ua: str) -> str:
  """Realiza una petición HTTP GET con cabeceras personalizadas"""
  headers = {
    "User-Agent": ua,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
  }
  r = session.get(url, timeout=timeout, headers=headers)
  r.raise_for_status()
  return r.text

def build_store_page_url(base_url: str, products_path: str, page: int) -> str:
  """Construye la URL de paginación para la tienda"""
  if page <= 1:
    return f"{base_url}{products_path}/"
  return f"{base_url}{products_path}/page/{page}/"

def extract_products_from_listing(html: str, base_url: str) -> List[StoreProduct]:
  """Extrae productos y precios de un listado HTML de Tienda Nube"""
  soup = BeautifulSoup(html, "lxml")
  anchors = soup.select('a.js-item-link')
  seen = set()
  products: List[StoreProduct] = []

  for a in anchors:
    href = a.get("href", "").strip()
    name = a.get_text(" ", strip=True)
    if not href or not name:
      continue
    
    if href.rstrip("/") == "/productos":
      continue
      
    url = href if href.startswith("http") else (base_url.rstrip("/") + href)
    key = (name, url)
    if key in seen:
      continue
    seen.add(key)

    price = None
    container = a.parent
    for _ in range(4):
      if not container:
        break
      text = container.get_text(" ", strip=True)
      m = re.search(r"\$\s*[\d\.,]+", text)
      if m:
        price = parse_ars_money(m.group(0))
        break
      container = container.parent
      
    products.append(StoreProduct(name=name, url=url, our_price_ars=price))

  dedup: Dict[str, StoreProduct] = {}
  for p in products:
    dedup[p.url] = p
  return list(dedup.values())

def scrape_store_products(cfg: Dict[str, Any]) -> List[StoreProduct]:
  """Raspa todos los productos de la tienda según la configuración"""
  base_url = cfg["store"]["base_url"].rstrip("/")
  products_path = cfg["store"]["products_path"].rstrip("/")
  pages = int(cfg["store"]["pages"])
  timeout = int(cfg["store"]["timeout_sec"])
  ua = str(cfg["store"]["user_agent"])

  session = requests.Session()
  all_products: List[StoreProduct] = []

  for page in range(1, pages + 1):
    url = build_store_page_url(base_url, products_path, page)
    print(f"[store] Página {page}/{pages}: {url}")
    try:
        html = http_get(session, url, timeout, ua)
        products = extract_products_from_listing(html, base_url)
        print(f"[store] encontrados: {len(products)}")
        all_products.extend(products)
    except Exception as e:
        print(f"[error] Fallo al raspar la página {page}: {e}")
    time.sleep(float(cfg["output"]["sleep_between_requests_sec"]))
  
  by_url = {p.url: p for p in all_products}
  return list(by_url.values())

# ----------------------------
# Fuentes de Competidores
# ----------------------------

def meli_search_offers(
  query: str,
  site_id: str,
  max_results: int,
  timeout: int,
  ua: str
) -> List[Tuple[str, Optional[float], str, str]]:
  """Busca ofertas en MercadoLibre usando su API oficial"""
  url = f"https://api.mercadolibre.com/sites/{site_id}/search"
  params = {"q": query, "limit": max_results}
  r = requests.get(url, params=params, timeout=timeout, headers={"User-Agent": ua})
  r.raise_for_status()
  data = r.json()

  out = []
  for it in data.get("results", []):
    title = it.get("title", "") or ""
    price = it.get("price", None)
    currency = it.get("currency_id", "ARS") or "ARS"
    permalink = it.get("permalink", "") or ""
    if title and permalink:
      out.append((title, float(price) if price is not None else None, currency, permalink))
  return out

def google_custom_search(
  query: str,
  api_key: str,
  cx: str,
  max_results: int,
  timeout: int,
  ua: str
) -> List[Tuple[str, Optional[float], str, str]]:
  """Busca en la web mediante Google Custom Search"""
  if not api_key or api_key == "YOUR_API_KEY":
      return []
  url = "https://www.googleapis.com/customsearch/v1"
  params = {"key": api_key, "cx": cx, "q": query, "num": max(1, min(max_results, 10))}
  r = requests.get(url, params=params, timeout=timeout, headers={"User-Agent": ua})
  r.raise_for_status()
  data = r.json()

  out = []
  for it in data.get("items", [])[:max_results]:
    title = it.get("title", "") or ""
    link = it.get("link", "") or ""
    snippet = it.get("snippet", "") or ""
    m = re.search(r"(\$|ARS)\s*[\d\.,]+", snippet)
    price = parse_ars_money(m.group(0)) if m else None
    if title and link:
      out.append((title, price, "ARS", link))
  return out

def serpapi_google_shopping(
  query: str,
  api_key: str,
  gl: str,
  hl: str,
  max_results: int,
  timeout: int,
  ua: str
) -> List[Tuple[str, Optional[float], str, str, str]]:
  """Busca en Google Shopping mediante SerpApi"""
  if not api_key or api_key == "YOUR_SERPAPI_KEY":
      return []
  url = "https://serpapi.com/search.json"
  params = {
    "engine": "google_shopping",
    "q": query,
    "api_key": api_key,
    "gl": gl,
    "hl": hl,
  }
  r = requests.get(url, params=params, timeout=timeout, headers={"User-Agent": ua})
  r.raise_for_status()
  data = r.json()

  out = []
  results = data.get("shopping_results", [])[:max_results]
  for it in results:
    title = it.get("title", "") or ""
    link = it.get("link", "") or it.get("product_link", "") or ""
    source = it.get("source", "") or "Google Shopping"
    price = it.get("extracted_price", None)
    currency = "ARS"
    if title and link:
      out.append((title, float(price) if price is not None else None, currency, link, source))
  return out

# ----------------------------
# Emparejamiento + Reglas de Precios
# ----------------------------

def similarity_score(a: str, b: str) -> int:
  """Calcula la puntuación de similitud entre dos títulos"""
  return int(fuzz.token_set_ratio(normalize_query(a), normalize_query(b)))

def compute_suggested_price(
  our_price: Optional[float],
  competitor_prices: List[float],
  pricing_cfg: Dict[str, Any]
) -> Optional[float]:
  """Calcula el precio sugerido basado en los precios de la competencia"""
  margin_pct = float(pricing_cfg.get("margin_pct", 100))
  base_strategy = pricing_cfg.get("base_strategy", "min_competitor")
  round_to = int(pricing_cfg.get("round_to", 10))
  min_price = float(pricing_cfg.get("min_price", 0))
  max_price = float(pricing_cfg.get("max_price", 0))

  base_price: Optional[float] = None
  if base_strategy == "our_current_price":
    base_price = our_price
  elif competitor_prices:
    if base_strategy == "median_competitor":
      s = sorted(competitor_prices)
      mid = len(s) // 2
      base_price = s[mid] if len(s) % 2 == 1 else (s[mid - 1] + s[mid]) / 2
    else:
      base_price = min(competitor_prices)
  else:
    base_price = our_price

  if base_price is None:
    return None

  suggested = base_price * (1.0 + margin_pct / 100.0)

  suggested = max(suggested, min_price)
  if max_price and max_price > 0:
    suggested = min(suggested, max_price)

  if round_to and round_to > 1:
    suggested = round(suggested / round_to) * round_to

  return float(suggested)

# ----------------------------
# Pipeline Principal
# ----------------------------

def gather_offers_for_product(
  product: StoreProduct,
  cfg: Dict[str, Any],
  synonyms: Dict[str, List[str]]
) -> List[CompetitorOffer]:
  """Recopila ofertas de diversas fuentes para un producto específico"""
  timeout = int(cfg["store"]["timeout_sec"])
  ua = str(cfg["store"]["user_agent"])
  min_sim = int(cfg["matching"]["min_similarity"])

  queries = expand_queries(product.name, synonyms)
  
  offers_raw: List[Tuple[str, Optional[float], str, str, str]] = []

  # MercadoLibre (API Oficial)
  if cfg["sources"]["mercadolibre"]["enabled"]:
    site_id = cfg["sources"]["mercadolibre"]["site_id"]
    max_results = int(cfg["sources"]["mercadolibre"]["max_results"])
    for q in queries:
      try:
        for title, price, currency, url in meli_search_offers(q, site_id, max_results, timeout, ua):
          offers_raw.append((title, price, currency, url, "MercadoLibre"))
      except Exception as e:
        print(f"[warn] ML falló con búsqueda='{q}': {e}")
      time.sleep(float(cfg["output"]["sleep_between_requests_sec"]))

  # Google Custom Search
  gcs = cfg["sources"]["google_custom_search"]
  if gcs.get("enabled"):
    api_key = gcs["api_key"]
    cx = gcs["cx"]
    max_results = int(gcs["max_results"])
    for q in queries[:3]:
      try:
        for title, price, currency, url in google_custom_search(q, api_key, cx, max_results, timeout, ua):
          offers_raw.append((title, price, currency, url, "Google (Web)"))
      except Exception as e:
        print(f"[warn] GCS falló con búsqueda='{q}': {e}")
      time.sleep(float(cfg["output"]["sleep_between_requests_sec"]))

  # Google Shopping (SerpApi)
  sap = cfg["sources"]["serpapi_google_shopping"]
  if sap.get("enabled"):
    api_key = sap["api_key"]
    gl = sap.get("gl", "ar")
    hl = sap.get("hl", "en")
    max_results = int(sap["max_results"])
    for q in queries[:3]:
      try:
        for title, price, currency, url, source in serpapi_google_shopping(q, api_key, gl, hl, max_results, timeout, ua):
          offers_raw.append((title, price, currency, url, f"Google Shopping: {source}"))
      except Exception as e:
        print(f"[warn] SerpApi falló con búsqueda='{q}': {e}")
      time.sleep(float(cfg["output"]["sleep_between_requests_sec"]))
      
  filtered: List[Tuple[str, Optional[float], str, str, str, int]] = []
  for title, price, currency, url, comp in offers_raw:
    sim = similarity_score(product.name, title)
    if sim >= min_sim:
      filtered.append((title, price, currency, url, comp, sim))

  competitor_prices = [p for _, p, cur, _, _, _ in filtered if p is not None and cur in ("ARS", "AR$", "ARG")]
  suggested = compute_suggested_price(product.our_price_ars, competitor_prices, cfg["pricing"])

  out: List[CompetitorOffer] = []
  for title, price, currency, url, comp, sim in filtered:
    out.append(CompetitorOffer(
      product_name=product.name,
      competitor_name=comp,
      competitor_price=price,
      currency=currency,
      url=url,
      similarity=sim,
      suggested_price=suggested
    ))
  
  out.sort(key=lambda x: (x.competitor_price is None, x.competitor_price if x.competitor_price is not None else 10**18))
  return out

def main() -> None:
  """Función principal para ejecutar el flujo de investigación"""
  cfg = load_or_create_config("config.yaml")
  synonyms = load_or_create_synonyms(cfg["synonyms"]["synonyms_file"])

  products = scrape_store_products(cfg)
  print(f"[store] Total de productos únicos: {len(products)}")
  
  all_offers: List[CompetitorOffer] = []

  for idx, p in enumerate(products, 1):
    print(f"\n[{idx}/{len(products)}] {p.name}")
    offers = gather_offers_for_product(p, cfg, synonyms)
    print(f"  ofertas coincidentes: {len(offers)}")
    all_offers.extend(offers)

  # Exportar a CSV
  csv_path = cfg["output"]["csv_path"]
  df = pd.DataFrame([asdict(o) for o in all_offers])
  df.to_csv(csv_path, index=False, encoding="utf-8-sig")
  print(f"\n[ok] CSV generado: {csv_path}")

  # Imprimir en formato de lista solicitado
  for o in all_offers:
    price_str = "" if o.competitor_price is None else f"{o.competitor_price:.2f} {o.currency}"
    sugg_str = "" if o.suggested_price is None else f"{o.suggested_price:.2f} ARS"
    print(f"{{{o.product_name}}}, {{{o.competitor_name}}}, {{{price_str}}}, {{{o.url}}}, {{{sugg_str}}}")

if __name__ == "__main__":
  main()
