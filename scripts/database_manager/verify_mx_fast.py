"""
verify_mx_fast.py — Verificación rápida de emails: solo MX/DNS (sin SMTP)
Procesa ~1000 emails/segundo. Actualiza deliverability en DB.

Uso:
  python verify_mx_fast.py                    # Verificar emails sin deliverability
  python verify_mx_fast.py --all              # Verificar TODOS los emails
"""

import os
import sys
import csv
import json
import time
import socket
import sqlite3
import logging
import argparse
import dns.resolver
from datetime import datetime
from typing import List, Tuple, Dict, Set

# === CONFIG ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "inputs", "contacts.db")
LOG_DIR = os.path.join(PROJECT_ROOT, "data", "inputs")
REPORT_PATH = os.path.join(PROJECT_ROOT, "data", "outputs", "mx_verification_report.csv")

MX_TIMEOUT = 2

GENERIC_DOMAINS = {
    "gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "live.com",
    "icloud.com", "aol.com", "mail.com", "protonmail.com", "proton.me",
    "zoho.com", "yandex.com", "gmx.com", "fastmail.com",
    "speedy.com.ar", "fibertel.com.ar", "ctgtech.com.ar",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, "verify_mx_fast.log"), encoding="utf-8"),
    ],
)
log = logging.getLogger("verify_mx")


def check_mx_records(domain: str) -> Tuple[bool, List[str], str]:
    """Verifica registros MX de un dominio"""
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=MX_TIMEOUT)
        mx_servers = [str(r.exchange).rstrip(".").lower() for r in answers]
        return True, mx_servers, ""
    except dns.resolver.NXDOMAIN:
        return False, [], "Dominio no existe"
    except dns.resolver.NoAnswer:
        return False, [], "Sin registros MX"
    except dns.resolver.NoNameservers:
        return False, [], "Sin nameservers"
    except dns.resolver.Timeout:
        return False, [], "Timeout DNS"
    except Exception as e:
        return False, [], f"Error DNS: {str(e)[:80]}"


def get_emails_to_verify(conn: sqlite3.Connection, verify_all: bool = False) -> List[Tuple[int, str]]:
    """Obtiene emails de la DB que necesitan verificación"""
    cur = conn.cursor()
    if verify_all:
        cur.execute("""
            SELECT m.ROWID, l.primary_email
            FROM main m
            JOIN lead l ON m.ROWID = l.ROWID
            WHERE l.primary_email IS NOT NULL AND l.primary_email != ''
        """)
    else:
        cur.execute("""
            SELECT m.ROWID, l.primary_email
            FROM main m
            JOIN lead l ON m.ROWID = l.ROWID
            LEFT JOIN contact c ON m.ROWID = c.ROWID
            WHERE l.primary_email IS NOT NULL AND l.primary_email != ''
            AND (c.deliverability IS NULL OR c.deliverability = '' OR c.deliverability = 'uncertain')
        """)
    return cur.fetchall()


def main():
    parser = argparse.ArgumentParser(description="Verificación rápida MX/DNS de emails")
    parser.add_argument("--all", action="store_true", help="Verificar TODOS los emails")
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("INICIO DE VERIFICACIÓN MX RÁPIDA")
    log.info("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    emails = get_emails_to_verify(conn, verify_all=args.all)
    log.info(f"Emails a verificar: {len(emails)}")

    if not emails:
        log.info("No hay emails para verificar")
        conn.close()
        return

    # Deduplicate by domain to avoid repeated MX lookups
    domain_cache = {}  # domain -> (ok, mx_servers, error)
    email_domains = {}  # email -> domain

    for rowid, email in emails:
        domain = email.split("@")[-1].lower()
        email_domains[email] = (rowid, domain)
        if domain not in domain_cache:
            domain_cache[domain] = None  # Mark as pending

    unique_domains = list(domain_cache.keys())
    log.info(f"Dominios únicos a verificar: {len(unique_domains)}")

    # Verify MX for unique domains
    start_time = time.time()
    verified = 0
    for i, domain in enumerate(unique_domains):
        ok, mx_servers, error = check_mx_records(domain)
        domain_cache[domain] = (ok, mx_servers, error)
        verified += 1
        if (i + 1) % 500 == 0:
            elapsed = time.time() - start_time
            log.info(f"Dominios verificados: {i + 1}/{len(unique_domains)} ({(i + 1) / max(elapsed, 0.1):.0f} dom/s)")

    mx_elapsed = time.time() - start_time
    log.info(f"MX verification completa: {mx_elapsed:.1f}s ({len(unique_domains) / max(mx_elapsed, 0.1):.0f} dom/s)")

    # Update DB with incremental commits
    cur = conn.cursor()
    now = datetime.now().isoformat()
    stats = {"valid": 0, "invalid": 0, "generic": 0, "total": 0}
    commit_batch = 500

    for i, (email, (rowid, domain)) in enumerate(email_domains.items()):
        stats["total"] += 1

        if domain in GENERIC_DOMAINS:
            deliverability = "generic"
            status = "generic"
            stats["generic"] += 1
        else:
            ok, mx_servers, error = domain_cache.get(domain, (False, [], "Unknown"))
            if ok:
                deliverability = "valid"
                status = "valid"
                stats["valid"] += 1
            else:
                deliverability = "invalid"
                status = f"no_mx:{error}"
                stats["invalid"] += 1

        cur.execute("""
            UPDATE contact SET deliverability = ?, last_validation_date = ?, last_validation_status = ?
            WHERE ROWID = ?
        """, (deliverability, now, f"mx_verified:{status}", rowid))

        if (i + 1) % commit_batch == 0:
            conn.commit()
            log.info(f"DB actualizada: {i + 1}/{len(email_domains)} registros")

    conn.commit()
    log.info(f"\n=== RESULTADOS ===")
    log.info(f"Total procesados: {stats['total']}")
    log.info(f"Valid (MX ok): {stats['valid']}")
    log.info(f"Invalid (no MX): {stats['invalid']}")
    log.info(f"Generic (skip): {stats['generic']}")

    # Final DB count
    cur.execute("SELECT COUNT(*) FROM contact WHERE deliverability = 'valid'")
    total_valid = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM contact WHERE deliverability = 'invalid'")
    total_invalid = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM contact WHERE deliverability = 'generic'")
    total_generic = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM contact WHERE deliverability IS NULL OR deliverability = ''")
    total_unverified = cur.fetchone()[0]

    log.info(f"\nDB deliverability summary:")
    log.info(f"  valid: {total_valid}")
    log.info(f"  invalid: {total_invalid}")
    log.info(f"  generic: {total_generic}")
    log.info(f"  unverified: {total_unverified}")

    conn.close()
    log.info("FIN DE VERIFICACIÓN")


if __name__ == "__main__":
    main()
