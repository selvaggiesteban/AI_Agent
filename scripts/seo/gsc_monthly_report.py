"""
gsc_monthly_report.py — Reporte mensual de Google Search Console por mes natural.

Para CADA propiedad de la cuenta: detecta el origen real de sus datos (primera
fecha con métricas en la retención de 16 meses de GSC) y recolecta cada mes
natural desde ese origen hasta la fecha de ejecución:

  1. Clics, impresiones totales, CTR medio y posición media (agregado del mes)
  2. Consultas principales con clics e impresiones
  3. Páginas principales con clics e impresiones
  4. Dispositivos (clics e impresiones)
  5. Apariciones en búsqueda completo (searchAppearance)
  6. Día por día con sus clics

Optimización: una única consulta "date" por propiedad (desde 2000-01-01) trae
todos los días con métricas → de ahí se derivan días y resumen de cada mes, y se
consultan las 4 dimensiones extra SOLO en meses con datos (menos cuota).

Salidas:
  docs/Esteban/campana/gsc_monthly_report.json   (base de datos cruda)
  docs/Esteban/campana/gsc_monthly_report.html   (fragmento autocontenido que se
      inyecta en docs/weekly-SEO.html: JSON embebido + UI con filtro Desde/Hasta)

La ejecución guarda progreso sitio a sitio: si se corta (p. ej. cuota 429 o
timeout), reejecutá el mismo comando y retoma donde quedó (mismo día).

Uso:
  python gsc_monthly_report.py                    # TODAS las propiedades, origen..hoy
  python gsc_monthly_report.py --site https://lanuscomputacion.com/   # una sola
  python gsc_monthly_report.py --from 2026-01 --to 2026-10            # rango fijo
  python gsc_monthly_report.py --months 6         # últimos 6 meses naturales
  python gsc_monthly_report.py --top 15           # top N consultas/páginas

Auth: misma que gsc_indexing_fixer.py (token token_gsc.json, scope webmasters).
Primera ejecución: abre el navegador (selector de cuentas → selvaggi.esteban@gmail.com).
Client secret: GSC_CLIENT_SECRET o el de docs/Esteban/campana/google/
(preferido: cliente 188518434756 / proyecto responsive-sun-499419-h1, API habilitada).
"""

import argparse
import json
import os
import sys
from calendar import monthrange
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as e:
    print(f"[ERROR] Faltan dependencias: {e}. Instalá: pip install google-api-python-client google-auth-oauthlib")
    sys.exit(1)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

SCOPES = ["https://www.googleapis.com/auth/webmasters"]
HERE = Path(__file__).resolve().parent
TOKEN_PATH = HERE / "token_gsc.json"
AI_ROOT = HERE.parent.parent
DEFAULT_CLIENT_SECRET_DIR = AI_ROOT / "docs" / "Esteban" / "campana" / "google"
JSON_OUT = AI_ROOT / "docs" / "Esteban" / "campana" / "gsc_monthly_report.json"
FRAG_OUT = AI_ROOT / "docs" / "Esteban" / "campana" / "gsc_monthly_report.html"
PREFERRED_CLIENT = "188518434756"  # proyecto responsive-sun-499419-h1 (API habilitada, cuenta del usuario)

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}
DEVICE_LABELS = {"MOBILE": "Móvil", "DESKTOP": "Escritorio", "TABLET": "Tablet"}
DEVICE_ORDER = ["MOBILE", "DESKTOP", "TABLET"]
ROW_LIMIT_TOP = 50  # filas máximas para consultas/páginas/apariciones (se ordena localmente)


# ─────────────────────────── AUTH (misma que gsc_indexing_fixer) ───────────────────────────

def find_client_secret() -> Path:
    env_path = os.getenv("GSC_CLIENT_SECRET")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    if DEFAULT_CLIENT_SECRET_DIR.exists():
        candidates = sorted(DEFAULT_CLIENT_SECRET_DIR.glob("client_secret_*.json"))
        if candidates:
            preferred = [c for c in candidates if PREFERRED_CLIENT in c.name]
            if preferred:
                return preferred[0]
            return candidates[0]
    raise FileNotFoundError(
        "No se encontró client_secret de Google. Definí GSC_CLIENT_SECRET o colocá "
        f"un archivo client_secret_*.json en {DEFAULT_CLIENT_SECRET_DIR}"
    )


def get_credentials() -> Credentials:
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        print("Se abrirá el navegador para autorizar Google Search Console… "
              "IMPORTANTE: elegí la cuenta selvaggi.esteban@gmail.com en el selector.", flush=True)
        flow = InstalledAppFlow.from_client_secrets_file(str(find_client_secret()), SCOPES)
        creds = flow.run_local_server(
            port=0, open_browser=True, timeout_seconds=600, prompt="select_account"
        )
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return creds


def list_sites(service):
    result = service.sites().list().execute()
    # La API devuelve "siteEntry" (algunas versiones documentan "sites")
    entries = result.get("siteEntry") or result.get("sites") or []
    return [s["siteUrl"] for s in entries]


# ─────────────────────────── CONSULTAS ───────────────────────────

def gsc_query(service, site, start, end, dimensions, row_limit):
    """Devuelve rows (lista) o None si la API falló. 429 (cuota) corta con mensaje."""
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": dimensions,
        "rowLimit": row_limit,
    }
    try:
        resp = service.searchanalytics().query(siteUrl=site, body=body).execute()
        return resp.get("rows", [])
    except HttpError as e:
        if getattr(e, "status", None) == 429:
            raise SystemExit(
                "[ERROR] Cuota diaria de la Search Console API agotada (429). "
                "El progreso quedó guardado sitio a sitio: reejecutá el mismo comando "
                "cuando renueve la cuota y retoma donde quedó."
            )
        return None


def _sorted_rows(rows):
    return sorted(rows, key=lambda r: (-r.get("clicks", 0), -r.get("impressions", 0)))


def months_ago(n, ref):
    y, m = ref.year, ref.month - n
    while m < 1:
        m += 12
        y -= 1
    return date(y, m, 1)


def collect_site_dates(service, site, today):
    """Mapa {fecha_iso: {clicks, impressions, position}} desde el origen real.

    Una sola consulta cubre toda la retención de GSC (16 meses). Devuelve {} si
    la propiedad nunca tuvo datos.
    """
    end = today.isoformat()
    rows = gsc_query(service, site, "2000-01-01", end, ["date"], 25000)
    if rows is None:  # reintento con el rango de retención por si '2000' falla
        rows = gsc_query(service, site, months_ago(16, today).isoformat(), end, ["date"], 25000)
    if not rows:
        return {}
    date_map = {}
    for r in rows:
        date_map[r["keys"][0]] = {
            "clicks": r.get("clicks", 0),
            "impressions": r.get("impressions", 0),
            "position": r.get("position", 0),
        }
    return date_map


def build_month(ym, date_map, today):
    """Mes natural con resumen y día por día derivados del mapa global de fechas."""
    y, m = int(ym[:4]), int(ym[5:])
    last = monthrange(y, m)[1]
    days = []
    clicks = impr = wpos = 0.0
    for d in range(1, last + 1):
        key = f"{y:04d}-{m:02d}-{d:02d}"
        e = date_map.get(key)
        c = e["clicks"] if e else 0
        days.append({"day": d, "clicks": c})
        if e:
            clicks += e["clicks"]
            impr += e["impressions"]
            wpos += e["position"] * e["impressions"]
    summary = None
    if impr or clicks:
        summary = {
            "clicks": int(clicks),
            "impressions": int(impr),
            "ctr": (clicks / impr) if impr else 0.0,
            "position": (wpos / impr) if impr else 0.0,
        }
    return {
        "ym": ym,
        "label": f"{MESES[m]} {y}",
        "start": f"{y:04d}-{m:02d}-01",
        "end": f"{y:04d}-{m:02d}-{last:02d}",
        "mm": f"{m:02d}",
        "en_curso": (y, m) == (today.year, today.month),
        "errors": [],
        "summary": summary,
        "queries": [],
        "pages": [],
        "devices": [],
        "appearances": [],
        "days": days,
    }


def fetch_month_extras(service, site, month, top, app_broken):
    """Consulta las 4 dimensiones extra de un mes con datos. Devuelve app_broken."""
    start, end = month["start"], month["end"]

    for dim, key in (("query", "queries"), ("page", "pages")):
        rows = gsc_query(service, site, start, end, [dim], ROW_LIMIT_TOP)
        if rows is None:
            month["errors"].append(f"Error API: {dim}")
            continue
        month[key] = [
            {"key": r["keys"][0], "clicks": r.get("clicks", 0), "impressions": r.get("impressions", 0)}
            for r in _sorted_rows(rows)[:top]
        ]

    rows = gsc_query(service, site, start, end, ["device"], 10)
    if rows is None:
        month["errors"].append("Error API: device")
    else:
        found = {r["keys"][0]: r for r in rows}
        devices = []
        for d in DEVICE_ORDER + [k for k in found if k not in DEVICE_ORDER]:
            r = found.get(d, {})
            devices.append({
                "key": d,
                "label": DEVICE_LABELS.get(d, d),
                "clicks": r.get("clicks", 0),
                "impressions": r.get("impressions", 0),
            })
        month["devices"] = sorted(devices, key=lambda x: -x["clicks"])

    if not app_broken:
        rows = gsc_query(service, site, start, end, ["searchAppearance"], ROW_LIMIT_TOP)
        if rows is None:
            app_broken = True
            month["errors"].append(
                "Apariciones en búsqueda no disponibles para esta propiedad (no se reconsultan)")
        else:
            month["appearances"] = [
                {
                    "key": r["keys"][0],
                    "clicks": r.get("clicks", 0),
                    "impressions": r.get("impressions", 0),
                    "ctr": r.get("ctr", 0),
                    "position": r.get("position", 0),
                }
                for r in _sorted_rows(rows)
            ]
    return app_broken


def collect_site(service, site, top, from_ym, to_ym, today):
    """Origen real de la propiedad + todos los meses naturales origen..hoy."""
    entry = {"site": site, "origin": None, "months": [], "error": None}
    date_map = collect_site_dates(service, site, today)
    if not date_map:
        entry["error"] = "Sin datos históricos en Search Console"
        return entry

    origin = min(date_map)
    entry["origin"] = origin
    cur = f"{today.year:04d}-{today.month:02d}"
    if from_ym or to_ym:
        ym_list = _months_between(from_ym or origin[:7], to_ym or cur)
    else:
        ym_list = _months_between(origin[:7], cur)
    print(f"  origen: {origin} · meses: {len(ym_list)}", flush=True)

    app_broken = False
    for ym in ym_list:
        month = build_month(ym, date_map, today)
        if month["summary"] is None:
            entry["months"].append(month)  # mes sin datos: se omite, queda vacío
            continue
        print(f"  [{ym}] consultando…", flush=True)
        app_broken = fetch_month_extras(service, site, month, top, app_broken)
        entry["months"].append(month)
    return entry


# ─────────────────────────── RANGO DE MESES ───────────────────────────

def _months_between(from_ym, to_ym):
    y, m = int(from_ym[:4]), int(from_ym[5:])
    y2, m2 = int(to_ym[:4]), int(to_ym[5:])
    out = []
    while (y, m) <= (y2, m2):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return out


def resolve_sites(sites, requested):
    """Devuelve la lista de propiedades a procesar (todas si no se indicó --site)."""
    if requested:
        if requested in sites:
            return [requested]
        for cand in (requested.rstrip("/") + "/", requested.rstrip("/")):
            if cand in sites:
                return [cand]
        matches = [s for s in sites if requested.rstrip("/") in s]
        if len(matches) == 1:
            return matches
        print(f"[ERROR] La propiedad '{requested}' no está en la cuenta. Disponibles:")
        for s in sites:
            print(f"  {s}")
        sys.exit(2)
    if not sites:
        print("[ERROR] La cuenta no tiene propiedades en Search Console. "
              "Agregá una en https://searchconsole.google.com")
        sys.exit(2)
    return sites


# ─────────────────────────── RENDER HTML (JSON embebido + filtro) ───────────────────────────

FRAG_CSS = """
#gsc-dashboard{--az:#1a73e8;--borde:#dadce0;--txt:#202124;--gris:#5f6368;--fondo:#f8f9fa;font-family:"Google Sans","Segoe UI",Roboto,Arial,sans-serif;color:var(--txt);margin:14px 0 6px}
#gsc-dashboard *{box-sizing:border-box}
#gsc-dashboard h2{font-size:20px;margin:0 0 4px;color:#1a73e8;font-weight:600;letter-spacing:-.2px}
#gsc-sub{font-size:12px;color:#5f6368;margin:0 0 12px}
#gsc-sub strong{color:#202124}
#gsc-topbar{position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;background:#fff;border:1px solid var(--borde);border-radius:12px;padding:10px 14px;box-shadow:0 1px 2px rgba(60,64,67,.18)}
#gsc-topbar .ctl{display:flex;flex-direction:column;gap:3px}
#gsc-topbar label{font-size:10px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--gris)}
#gsc-topbar select,#gsc-topbar input{font:inherit;font-size:13px;padding:7px 9px;border:1px solid var(--borde);border-radius:8px;background:#fff;color:var(--txt);min-width:150px}
#gsc-topbar input[type=month]{min-width:135px}
#gsc-topbar select:focus,#gsc-topbar input:focus{outline:2px solid #aecbfa;border-color:transparent}
#gsc-dashboard button{font:inherit;font-size:13px;font-weight:600;border-radius:18px;padding:8px 18px;cursor:pointer;border:1px solid transparent}
#gsc-btn-aplicar{background:#1a73e8;color:#fff}
#gsc-btn-aplicar:hover{background:#174ea6;box-shadow:0 1px 3px rgba(26,115,232,.5)}
#gsc-btn-todo{background:#fff;color:#1a73e8;border-color:var(--borde)}
#gsc-btn-todo:hover{background:#e8f0fe}
#gsc-rango-info{font-size:12px;color:var(--gris);margin-left:auto;text-align:right;max-width:360px;padding-bottom:4px}
#gsc-kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px 0}
@media(max-width:760px){#gsc-kpis{grid-template-columns:repeat(2,1fr)}}
#gsc-dashboard .kpi{background:#fff;border:1px solid var(--borde);border-radius:12px;padding:14px 16px;transition:box-shadow .15s}
#gsc-dashboard .kpi:hover{box-shadow:0 1px 6px rgba(60,64,67,.25)}
#gsc-dashboard .kpi .v{font-size:30px;font-weight:600;line-height:1.05;letter-spacing:-.5px;font-variant-numeric:tabular-nums}
#gsc-dashboard .kpi .l{font-size:11px;font-weight:700;letter-spacing:.7px;text-transform:uppercase;color:var(--gris);margin-top:6px}
#gsc-chart{background:#fff;border:1px solid var(--borde);border-radius:12px;padding:12px 16px 4px}
#gsc-chart .ch-head{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:4px}
#gsc-chart h4{margin:0;font-size:14px;font-weight:600}
#gsc-dashboard .ley{font-size:12px;color:var(--gris);display:flex;gap:14px;align-items:center}
#gsc-dashboard .ley i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px}
#gsc-dashboard .ley .az{background:#1a73e8}
#gsc-dashboard .ley .or{background:#f9ab00;border-radius:50%}
#gsc-tabs{display:flex;gap:2px;background:#fff;border:1px solid var(--borde);border-bottom:0;border-radius:12px 12px 0 0;padding:0 10px;margin-top:12px;overflow-x:auto}
#gsc-tabs button{background:none;border:0;border-bottom:3px solid transparent;border-radius:0;font-size:13px;font-weight:600;color:var(--gris);padding:12px 14px;white-space:nowrap}
#gsc-tabs button:hover{color:#1a73e8;background:#f1f3f4}
#gsc-tabs button.on{color:#1a73e8;border-bottom-color:#1a73e8}
#gsc-tabla{background:#fff;border:1px solid var(--borde);border-radius:0 0 12px 12px;padding:4px 8px 10px;max-height:54vh;overflow:auto}
#gsc-tabla table{border-collapse:separate;border-spacing:0;width:100%;font-size:13px}
#gsc-tabla th{position:sticky;top:0;background:#fff;color:var(--gris);font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:.5px;text-align:left;padding:10px;border-bottom:2px solid var(--borde);z-index:2}
#gsc-tabla td{padding:8px 10px;border-bottom:1px solid #f1f3f4}
#gsc-tabla tr:hover td{background:#f8f9fa}
#gsc-tabla .num{text-align:right;font-variant-numeric:tabular-nums}
#gsc-tabla tfoot td{font-weight:700;border-top:2px solid var(--borde);border-bottom:0;background:#f8f9fa}
#gsc-dashboard .badge{display:inline-block;background:#e8f0fe;color:#1a73e8;font-size:10px;font-weight:700;border-radius:10px;padding:2px 8px;margin-left:6px;vertical-align:1px;text-transform:uppercase;letter-spacing:.4px}
#gsc-tabla .sel-mes{font:inherit;font-size:13px;padding:5px 8px;border:1px solid var(--borde);border-radius:8px}
#gsc-dashboard .gsc-nota{font-size:12px;color:var(--gris);margin:4px 2px}
#gsc-dashboard .gsc-vacio{padding:26px 8px;text-align:center;color:var(--gris)}
#gsc-notas{margin-top:8px;font-size:12px;color:var(--gris);display:flex;flex-wrap:wrap;gap:6px;align-items:center}
#gsc-dashboard .chip{background:#f1f3f4;border:1px solid var(--borde);border-radius:12px;padding:2px 10px}
#gsc-pie{font-size:11px;color:#80868b;margin:8px 2px 0}
""".strip()

RENDER_JS = r"""
(function () {
  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  var DATA;
  try {
    DATA = JSON.parse($('gsc-data').textContent);
  } catch (e) {
    $('gsc-tabla').innerHTML = '<p class="gsc-vacio">Error al leer el JSON embebido: ' + esc(e.message) + '</p>';
    return;
  }
  var meta = DATA.meta || {};
  var MES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
  var state = { prop: '__ALL__', desde: meta.desde || '', hasta: meta.hasta || '',
                tab: 'resumen', dia: null };
  function fi(n) {
    n = Math.round(Number(n) || 0);
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  }
  function fp(x) { return (Number(x) * 100).toFixed(2).replace('.', ',') + ' %'; }
  function fpo(x) { return Number(x).toFixed(1).replace('.', ','); }
  function fd(iso) { return iso.slice(8, 10) + '/' + iso.slice(5, 7) + '/' + iso.slice(0, 4); }
  function ylab(ym) { return MES[Number(ym.slice(5, 7)) - 1] + ' ' + ym.slice(0, 4); }
  function inRange(ym) {
    return (!state.desde || ym >= state.desde) && (!state.hasta || ym <= state.hasta);
  }
  function selSites() {
    return (DATA.sites || []).filter(function (s) {
      return state.prop === '__ALL__' || s.site === state.prop;
    });
  }
  function withData() {
    return (DATA.sites || []).filter(function (s) {
      return !!(s.origin && (s.months || []).length);
    });
  }
  function aggMonths() {
    var map = {};
    selSites().forEach(function (s) {
      (s.months || []).forEach(function (mo) {
        if (!inRange(mo.ym)) return;
        var o = map[mo.ym];
        if (!o) { o = map[mo.ym] = { ym: mo.ym, clicks: 0, impr: 0, posW: 0, en: false }; }
        if (mo.summary) {
          o.clicks += mo.summary.clicks;
          o.impr += mo.summary.impressions;
          o.posW += mo.summary.position * mo.summary.impressions;
        }
        if (mo.en_curso) o.en = true;
      });
    });
    return Object.keys(map).sort().map(function (k) {
      var o = map[k];
      o.ctr = o.impr ? o.clicks / o.impr : 0;
      o.pos = o.impr ? o.posW / o.impr : 0;
      o.label = ylab(o.ym);
      return o;
    });
  }
  function renderKpis(ms) {
    var c = 0, i = 0, pw = 0;
    ms.forEach(function (m) { c += m.clicks; i += m.impr; pw += m.posW; });
    $('gsc-k-clics').textContent = fi(c);
    $('gsc-k-impr').textContent = fi(i);
    $('gsc-k-ctr').textContent = i ? fp(c / i) : '\u2014';
    $('gsc-k-pos').textContent = i ? fpo(pw / i) : '\u2014';
  }
  function chartSVG(ms) {
    var W = 880, H = 240, L = 54, R = 64, T = 14, B = 46;
    var pw = W - L - R, ph = H - T - B, n = ms.length;
    var maxC = 1, maxI = 1;
    ms.forEach(function (m) {
      if (m.clicks > maxC) maxC = m.clicks;
      if (m.impr > maxI) maxI = m.impr;
    });
    var step = pw / n, bw = Math.max(3, Math.min(26, step * 0.5));
    function x(i) { return L + step * (i + 0.5); }
    function yC(v) { return T + ph - (v / maxC) * ph; }
    function yI(v) { return T + ph - (v / maxI) * ph; }
    var s = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" height="' + H +
      '" role="img" aria-label="Clics e impresiones por mes">';
    for (var g = 0; g <= 4; g++) {
      var yy = T + ph - (ph * g / 4);
      s += '<line x1="' + L + '" y1="' + yy + '" x2="' + (W - R) + '" y2="' + yy + '" stroke="#eceff1"/>';
      s += '<text x="' + (L - 8) + '" y="' + (yy + 4) + '" text-anchor="end" font-size="10" fill="#5f6368">' +
        fi(maxC * g / 4) + '</text>';
      var ir = maxI * g / 4;
      s += '<text x="' + (W - R + 8) + '" y="' + (yy + 4) + '" text-anchor="start" font-size="10" fill="#f9ab00">' +
        (ir >= 1000 ? fi(ir / 1000) + 'k' : fi(ir)) + '</text>';
    }
    s += '<line x1="' + L + '" y1="' + (T + ph) + '" x2="' + (W - R) + '" y2="' + (T + ph) + '" stroke="#dadce0"/>';
    ms.forEach(function (m, i) {
      var bh = Math.max(1, (m.clicks / maxC) * ph);
      s += '<rect x="' + (x(i) - bw / 2) + '" y="' + (T + ph - bh) + '" width="' + bw +
        '" height="' + bh + '" rx="2" fill="#1a73e8"><title>' +
        esc(m.label + ': ' + fi(m.clicks) + ' clics') + '</title></rect>';
    });
    s += '<polyline points="' + ms.map(function (m, i) {
      return x(i) + ',' + yI(m.impr);
    }).join(' ') + '" fill="none" stroke="#f9ab00" stroke-width="2.5" stroke-linejoin="round"/>';
    ms.forEach(function (m, i) {
      s += '<circle cx="' + x(i) + '" cy="' + yI(m.impr) + '" r="3" fill="#f9ab00"><title>' +
        esc(m.label + ': ' + fi(m.impr) + ' impresiones') + '</title></circle>';
    });
    var rot = n > 7;
    ms.forEach(function (m, i) {
      var lab = m.ym.slice(2).replace('-', '/');
      if (rot) {
        var tx = x(i) - 4, ty = H - B + 16;
        s += '<text x="' + tx + '" y="' + ty + '" font-size="10" fill="#5f6368" text-anchor="start" transform="rotate(-45 ' +
          tx + ' ' + ty + ')">' + lab + '</text>';
      } else {
        s += '<text x="' + x(i) + '" y="' + (H - B + 20) + '" font-size="11" fill="#5f6368" text-anchor="middle">' +
          lab + '</text>';
      }
    });
    return s + '</svg>';
  }
  function renderChart(ms) {
    $('gsc-chart-svg').innerHTML = ms.length ? chartSVG(ms) :
      '<p class="gsc-vacio">Sin datos en el rango seleccionado.</p>';
  }
  function tabResumen(ms) {
    var h = '<table><thead><tr><th>Mes natural</th><th class="num">Clics</th>' +
      '<th class="num">Impresiones</th><th class="num">CTR medio</th><th class="num">Posici\u00f3n media</th>' +
      '</tr></thead><tbody>';
    var tc = 0, ti = 0, tpw = 0;
    ms.forEach(function (m) {
      tc += m.clicks; ti += m.impr; tpw += m.posW;
      h += '<tr><td>' + esc(m.label) + (m.en ? '<span class="badge">en curso</span>' : '') +
        '</td><td class="num">' + fi(m.clicks) + '</td><td class="num">' + fi(m.impr) +
        '</td><td class="num">' + (m.impr ? fp(m.ctr) : '\u2014') +
        '</td><td class="num">' + (m.impr ? fpo(m.pos) : '\u2014') + '</td></tr>';
    });
    return h + '</tbody><tfoot><tr><td>Total del rango</td><td class="num">' + fi(tc) +
      '</td><td class="num">' + fi(ti) + '</td><td class="num">' + (ti ? fp(tc / ti) : '\u2014') +
      '</td><td class="num">' + (ti ? fpo(tpw / ti) : '\u2014') + '</td></tr></tfoot></table>';
  }
  function keyTable(field, head) {
    var acc = {}, ms = aggMonths();
    var multi = ms.length > 1 || state.prop === '__ALL__';
    selSites().forEach(function (s) {
      (s.months || []).forEach(function (mo) {
        if (!inRange(mo.ym)) return;
        (mo[field] || []).forEach(function (r) {
          var o = acc[r.key] || (acc[r.key] = { key: r.key, clicks: 0, impr: 0 });
          o.clicks += r.clicks;
          o.impr += r.impressions;
        });
      });
    });
    var arr = Object.keys(acc).map(function (k) { return acc[k]; })
      .sort(function (a, b) { return b.clicks - a.clicks || b.impr - a.impr; });
    if (!arr.length) return '<p class="gsc-vacio">Sin datos para este rango.</p>';
    var note = '<p class="gsc-nota">Top 50 por clics' + (multi ?
      ' \u00b7 suma de los tops mensuales del rango (Search Console devuelve hasta 50 filas por consulta).' :
      ' \u00b7 mes completo.') + '</p>';
    arr = arr.slice(0, 50);
    var h = note + '<table><thead><tr><th>' + head + '</th><th class="num">Clics</th>' +
      '<th class="num">Impresiones</th></tr></thead><tbody>';
    arr.forEach(function (r) {
      h += '<tr><td>' + esc(r.key) + '</td><td class="num">' + fi(r.clicks) +
        '</td><td class="num">' + fi(r.impr) + '</td></tr>';
    });
    return h + '</tbody></table>';
  }
  function sumField(field) {
    var acc = {};
    selSites().forEach(function (s) {
      (s.months || []).forEach(function (mo) {
        if (!inRange(mo.ym)) return;
        (mo[field] || []).forEach(function (r) {
          var o = acc[r.key] || (acc[r.key] = { key: r.key, label: r.label || r.key,
            clicks: 0, impr: 0, posW: 0 });
          o.clicks += r.clicks;
          o.impr += r.impressions;
          if (r.position != null) o.posW += r.position * r.impressions;
        });
      });
    });
    return Object.keys(acc).map(function (k) { return acc[k]; })
      .sort(function (a, b) { return b.clicks - a.clicks || b.impr - a.impr; });
  }
  function tabDevices() {
    var arr = sumField('devices');
    if (!arr.length) return '<p class="gsc-vacio">Sin datos para este rango.</p>';
    var h = '<p class="gsc-nota">Totales exactos del rango seleccionado.</p>' +
      '<table><thead><tr><th>Dispositivo</th><th class="num">Clics</th>' +
      '<th class="num">Impresiones</th></tr></thead><tbody>';
    arr.forEach(function (d) {
      h += '<tr><td>' + esc(d.label) + '</td><td class="num">' + fi(d.clicks) +
        '</td><td class="num">' + fi(d.impr) + '</td></tr>';
    });
    return h + '</tbody></table>';
  }
  function tabAppear() {
    var arr = sumField('appearances');
    if (!arr.length) {
      return '<p class="gsc-vacio">Sin datos de apariciones en b\u00fasqueda para este rango.</p>';
    }
    var h = '<table><thead><tr><th>Aparici\u00f3n</th><th class="num">Clics</th>' +
      '<th class="num">Impresiones</th><th class="num">CTR</th><th class="num">Posici\u00f3n</th>' +
      '</tr></thead><tbody>';
    arr.forEach(function (a) {
      h += '<tr><td>' + esc(a.label) + '</td><td class="num">' + fi(a.clicks) +
        '</td><td class="num">' + fi(a.impr) + '</td><td class="num">' +
        (a.impr ? fp(a.clicks / a.impr) : '\u2014') + '</td><td class="num">' +
        (a.impr ? fpo(a.posW / a.impr) : '\u2014') + '</td></tr>';
    });
    return h + '</tbody></table>';
  }
  function tabDias(ms) {
    var opts = ms.map(function (m) { return m.ym; });
    if (state.dia === null || opts.indexOf(state.dia) === -1) state.dia = opts[opts.length - 1];
    var ym = state.dia, y = Number(ym.slice(0, 4)), mo = Number(ym.slice(5, 7));
    var days = {};
    selSites().forEach(function (s) {
      (s.months || []).forEach(function (mm) {
        if (mm.ym !== ym) return;
        (mm.days || []).forEach(function (d) { days[d.day] = (days[d.day] || 0) + d.clicks; });
      });
    });
    var dim = new Date(y, mo, 0).getDate();
    var h = '<p class="gsc-nota">Clics por d\u00eda natural \u00b7 mes: <select class="sel-mes" id="gsc-dia-mes">';
    opts.forEach(function (o) {
      h += '<option value="' + o + '"' + (o === ym ? ' selected' : '') + '>' + esc(ylab(o)) + '</option>';
    });
    h += '</select></p><table><thead><tr><th>D\u00eda</th><th class="num">Clics</th></tr></thead><tbody>';
    for (var d = 1; d <= dim; d++) {
      h += '<tr><td>' + String(d).padStart(2, '0') + '/' + ym.slice(5, 7) +
        '</td><td class="num">' + fi(days[d] || 0) + '</td></tr>';
    }
    return h + '</tbody></table>';
  }
  function renderTab() {
    var ms = aggMonths(), box = $('gsc-tabla');
    if (!ms.length) {
      box.innerHTML = '<p class="gsc-vacio">Sin datos para la propiedad y el rango seleccionados.</p>';
      return;
    }
    var html;
    if (state.tab === 'resumen') html = tabResumen(ms);
    else if (state.tab === 'consultas') html = keyTable('queries', 'Consulta');
    else if (state.tab === 'paginas') html = keyTable('pages', 'P\u00e1gina');
    else if (state.tab === 'dispositivos') html = tabDevices();
    else if (state.tab === 'apariciones') html = tabAppear();
    else html = tabDias(ms);
    box.innerHTML = html;
    var sel = $('gsc-dia-mes');
    if (sel) sel.addEventListener('change', function () { state.dia = sel.value; renderTab(); });
  }
  function setTab(tab) {
    state.tab = tab;
    Array.prototype.forEach.call(document.querySelectorAll('#gsc-tabs button'), function (b) {
      var on = b.getAttribute('data-tab') === tab;
      if (on) b.classList.add('on'); else b.classList.remove('on');
    });
    renderTab();
  }
  function renderAll() {
    var ms = aggMonths();
    renderKpis(ms);
    renderChart(ms);
    renderTab();
    var total = (DATA.sites || []).length, n = withData().length;
    var scope = state.prop === '__ALL__'
      ? 'Todas las propiedades (' + n + ' con datos de ' + total + ')'
      : state.prop;
    $('gsc-rango-info').textContent = scope + ' \u00b7 ' + ms.length + ' meses en el rango (' +
      (state.desde || '?') + ' \u2192 ' + (state.hasta || '?') + ')';
    var sin = (DATA.sites || []).filter(function (s) {
      return !(s.origin && (s.months || []).length);
    });
    $('gsc-notas').innerHTML = sin.length
      ? '<span>Sin datos hist\u00f3ricos:</span>' + sin.map(function (s) {
          return '<span class="chip">' + esc(s.site) + '</span>';
        }).join('')
      : '';
  }
  function readRange() {
    var d = $('gsc-desde').value, h = $('gsc-hasta').value;
    if (d && h && d > h) { var t = d; d = h; h = t; }
    state.desde = d;
    state.hasta = h;
    state.dia = null;
  }
  var selProp = $('gsc-prop');
  var opts = '<option value="__ALL__">Todas las propiedades (' + (DATA.sites || []).length + ')</option>';
  (DATA.sites || []).forEach(function (s) {
    var ok = s.origin && (s.months || []).length;
    opts += '<option value="' + esc(s.site) + '">' + esc(s.site) + (ok ? '' : ' \u2014 sin datos') + '</option>';
  });
  selProp.innerHTML = opts;
  $('gsc-desde').value = state.desde;
  $('gsc-hasta').value = state.hasta;
  selProp.addEventListener('change', function () { state.prop = selProp.value; renderAll(); });
  $('gsc-desde').addEventListener('change', function () { readRange(); renderAll(); });
  $('gsc-hasta').addEventListener('change', function () { readRange(); renderAll(); });
  $('gsc-btn-filtrar').addEventListener('click', function () { readRange(); renderAll(); });
  $('gsc-btn-todo').addEventListener('click', function () {
    state.prop = '__ALL__';
    selProp.value = '__ALL__';
    state.desde = meta.desde || '';
    state.hasta = meta.hasta || '';
    $('gsc-desde').value = state.desde;
    $('gsc-hasta').value = state.hasta;
    state.dia = null;
    renderAll();
  });
  Array.prototype.forEach.call(document.querySelectorAll('#gsc-tabs button'), function (b) {
    b.addEventListener('click', function () { setTab(b.getAttribute('data-tab')); });
  });
  renderAll();
})();
""".strip()


def render_fragment(report) -> str:
    meta = report.get("meta", {})
    desde = escape(meta.get("desde", ""))
    hasta = escape(meta.get("hasta", ""))
    ej = escape(meta.get("ejecucion", ""))
    j = json.dumps(report, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    parts = [
        '<section id="gsc-dashboard">\n',
        "<h2>Search Console \u00b7 Per\u00edodo de tiempo \u2014 por mes natural</h2>\n",
        f'<p id="gsc-sub">{meta.get("sitios", 0)} propiedades \u00b7 ejecuci\u00f3n {ej} \u00b7 '
        f"rango disponible <strong>{desde} \u2192 {hasta}</strong> \u00b7 "
        "retenci\u00f3n de Search Console: 16 meses \u00b7 base de datos JSON embebida "
        "que se recalcula en el navegador al filtrar.</p>\n",
        '<div id="gsc-topbar">\n'
        '  <span class="ctl"><label for="gsc-prop">Propiedad</label>'
        '<select id="gsc-prop"></select></span>\n'
        '  <span class="ctl"><label for="gsc-desde">Desde</label>'
        f'<input type="month" id="gsc-desde" min="{desde}" max="{hasta}" value="{desde}"></span>\n'
        '  <span class="ctl"><label for="gsc-hasta">Hasta</label>'
        f'<input type="month" id="gsc-hasta" min="{desde}" max="{hasta}" value="{hasta}"></span>\n'
        '<button type="button" id="gsc-btn-filtrar">Aplicar</button>\n'
        '<button type="button" id="gsc-btn-todo">Ver todo</button>\n'
        '<span id="gsc-rango-info"></span>\n'
        "</div>\n",
        '<div id="gsc-kpis">\n'
        '  <div class="kpi"><div class="v" id="gsc-k-clics">\u2014</div><div class="l">Clics</div></div>\n'
        '  <div class="kpi"><div class="v" id="gsc-k-impr">\u2014</div><div class="l">Impresiones</div></div>\n'
        '  <div class="kpi"><div class="v" id="gsc-k-ctr">\u2014</div><div class="l">CTR medio</div></div>\n'
        '  <div class="kpi"><div class="v" id="gsc-k-pos">\u2014</div><div class="l">Posici\u00f3n media</div></div>\n'
        "</div>\n",
        '<div id="gsc-chart">\n'
        '  <div class="ch-head"><h4>Clics e impresiones por mes</h4>\n'
        '  <span class="ley"><span><i class="az"></i>Clics</span>'
        '<span><i class="or"></i>Impresiones</span></span></div>\n'
        '  <div id="gsc-chart-svg"></div>\n'
        "</div>\n",
        '<div id="gsc-tabs">\n'
        '  <button type="button" data-tab="resumen" class="on">Resumen mensual</button>\n'
        '  <button type="button" data-tab="consultas">Consultas</button>\n'
        '  <button type="button" data-tab="paginas">P\u00e1ginas</button>\n'
        '  <button type="button" data-tab="dispositivos">Dispositivos</button>\n'
        '  <button type="button" data-tab="apariciones">Apariciones en b\u00fasqueda</button>\n'
        '  <button type="button" data-tab="dias">D\u00eda por d\u00eda</button>\n'
        "</div>\n",
        '<div id="gsc-tabla"></div>\n',
        '<div id="gsc-notas"></div>\n',
        '<p id="gsc-pie">Reporte autocontenido: la base de datos vive en un JSON embebido '
        "(id <code>gsc-data</code>) y los KPIs, el gr\u00e1fico y las tablas se calculan en el "
        f"navegador. Origen real de cada propiedad hasta la fecha de ejecuci\u00f3n ({ej}).</p>\n",
        "</section>\n",
        "<noscript><p>Este reporte requiere JavaScript: los datos est\u00e1n en un JSON "
        "embebido y el navegador los renderiza.</p></noscript>\n",
        f'<script type="application/json" id="gsc-data">{j}</script>\n',
        f"<style>\n{FRAG_CSS}\n</style>\n",
        f"<script>\n{RENDER_JS}\n</script>\n",
    ]
    return "".join(parts)


# ─────────────────────────── PERSISTENCIA (guardado incremental / reanudación) ───────────────────────────

def save_state(report, cur, ejecucion):
    origins = [e["origin"][:7] for e in report["sites"] if e.get("origin")]
    report["meta"] = {
        "ejecucion": ejecucion,
        "desde": min(origins) if origins else months_ago(16, date.today()).strftime("%Y-%m"),
        "hasta": cur,
        "sitios": len(report["sites"]),
    }
    report["generado"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    FRAG_OUT.write_text(render_fragment(report), encoding="utf-8")


def load_resume(params):
    try:
        prev = json.loads(JSON_OUT.read_text(encoding="utf-8"))
    except Exception:
        return None
    if (
        isinstance(prev.get("sites"), list)
        and prev.get("params") == params
        and prev.get("fecha_iso") == date.today().isoformat()
    ):
        return prev
    return None


# ─────────────────────────── MAIN ───────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Reporte mensual de GSC por mes natural (origen real de cada propiedad hasta hoy)")
    parser.add_argument("--site", help="Propiedad GSC (ej. https://lanuscomputacion.com/)")
    parser.add_argument("--from", dest="from_ym", help="Mes inicial YYYY-MM (default: origen de cada propiedad)")
    parser.add_argument("--to", dest="to_ym", help="Mes final YYYY-MM (default: mes actual)")
    parser.add_argument("--months", type=int, help="Últimos N meses naturales (incluye el actual)")
    parser.add_argument("--top", type=int, default=10, help="Top N consultas/páginas (default 10, máx 50)")
    parser.add_argument("--render-only", action="store_true",
                        help="Regenerar JSON y fragmento HTML desde los datos existentes, sin consultar la API")
    args = parser.parse_args()
    top = max(1, min(args.top, ROW_LIMIT_TOP))

    if args.render_only:
        try:
            rep = json.loads(JSON_OUT.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[ERROR] No hay JSON existente en {JSON_OUT} ({e}). Ejecutá sin --render-only.")
            sys.exit(2)
        m = rep.get("meta", {})
        save_state(rep, m.get("hasta") or months_ago(16, date.today()).strftime("%Y-%m"),
                   m.get("ejecucion") or date.today().strftime("%d/%m/%Y"))
        print(f"OK (render-only) {JSON_OUT}")
        print(f"OK (render-only) {FRAG_OUT}")
        print("Para regenerar el HTML: python scripts\\database\\matrices_to_html.py")
        return

    print("Autenticando con Google…")
    creds = get_credentials()
    service = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    sites = list_sites(service)
    print(f"Propiedades en la cuenta: {len(sites)}")
    site_list = resolve_sites(sites, args.site)

    today = date.today()
    cur = f"{today.year:04d}-{today.month:02d}"
    ejecucion = today.strftime("%d/%m/%Y")

    from_ym = to_ym = None
    if args.from_ym or args.to_ym:
        from_ym, to_ym = args.from_ym, args.to_ym
    elif args.months and args.months > 0:
        from_ym = months_ago(args.months - 1, today).strftime("%Y-%m")
        to_ym = cur

    params = {"from": args.from_ym, "to": args.to_ym, "months": args.months, "top": top}
    report = load_resume(params)
    if report:
        done = {e["site"] for e in report["sites"] if e.get("error") is None}
        print(f"Retomando ejecución de hoy: {len(done)} sitios ya completados", flush=True)
    else:
        report = {
            "params": params,
            "fecha_iso": today.isoformat(),
            "fecha_ejecucion": ejecucion,
            "sites": [],
        }
        done = set()

    print(f"Propiedades a procesar: {len(site_list) - len([s for s in site_list if s in done])}")
    for site in site_list:
        if site in done:
            print(f"\n=== {site} === (ya completado, se omite)")
            continue
        print(f"\n=== {site} ===", flush=True)
        try:
            entry = collect_site(service, site, top, from_ym, to_ym, today)
        except SystemExit:
            raise
        except Exception as e:
            entry = {"site": site, "origin": None, "months": [], "error": str(e)}
            print(f"  [ERROR] {site}: {e}", flush=True)
        idx = next((i for i, e in enumerate(report["sites"]) if e["site"] == site), None)
        if idx is None:
            report["sites"].append(entry)
        else:
            report["sites"][idx] = entry
        save_state(report, cur, ejecucion)
        print(f"  guardado ({entry['origin'] or 'sin datos'} · {len(entry['months'])} meses)", flush=True)

    save_state(report, cur, ejecucion)
    print(f"\nOK {JSON_OUT}")
    print(f"OK {FRAG_OUT}")
    print("Para regenerar el HTML: python scripts\\database\\matrices_to_html.py")


if __name__ == "__main__":
    main()
