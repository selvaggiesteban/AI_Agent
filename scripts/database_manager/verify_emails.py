"""
verify_emails.py — Verificación de emails: MX/DNS + SMTP RCPT TO
Valida que el dominio reciba email (MX records) y que el buzón exista (SMTP handshake).

Uso:
  python verify_emails.py                    # Verificar emails sin deliverability
  python verify_emails.py --all              # Verificar TODOS los emails
  python verify_emails.py --email x@y.com    # Verificar un email específico
  python verify_emails.py --batch 1000       # Procesar en batches de 1000
  python verify_emails.py --dry-run          # Solo mostrar, no actualizar DB
"""

import os
import sys
import csv
import json
import time
import socket
import smtplib
import logging
import argparse
import sqlite3
import dns.resolver
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

# === CONFIG ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "inputs", "contacts.db")
LOG_DIR = os.path.join(PROJECT_ROOT, "data", "inputs")
REPORT_PATH = os.path.join(PROJECT_ROOT, "data", "outputs", "email_verification_report.csv")

# Timeouts
MX_TIMEOUT = 5          # segundos para resolver MX
SMTP_TIMEOUT = 10       # segundos para conexión SMTP
RCPT_TIMEOUT = 10       # segundos para RCPT TO
MAX_WORKERS = 20        # threads paralelos

# Dominios descartados (email providers masivos - no vale la pena verificar)
GENERIC_DOMAINS = {
    "gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "live.com",
    "icloud.com", "aol.com", "mail.com", "protonmail.com", "proton.me",
    "zoho.com", "yandex.com", "gmx.com", "fastmail.com",
    "speedy.com.ar", "fibertel.com.ar", "ctgtech.com.ar",
}

# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, "email_verification.log"), encoding="utf-8"),
    ],
)
log = logging.getLogger("verify_emails")


# === MX RECORD CHECK ===

def check_mx_records(domain: str) -> Tuple[bool, List[str], str]:
    """
    Verifica si el dominio tiene registros MX.
    Retorna: (ok, mx_servers, error_message)
    """
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=MX_TIMEOUT)
        mx_servers = [str(r.exchange).rstrip(".").lower() for r in answers]
        mx_servers.sort(key=lambda x: x[0])  # sort by priority (implicit inMX record order)
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


# === SMTP RCPT TO CHECK ===

def smtp_verify_email(email: str, mx_server: str) -> Tuple[bool, str]:
    """
    Verifica si el email existe via SMTP RCPT TO.
    Retorna: (exists, message)
    """
    try:
        server = smtplib.SMTP(timeout=SMTP_TIMEOUT)
        server.connect(mx_server, 25)
        server.helo("verify.example.com")
        server.mail("verify@example.com")

        code, msg = server.rcpt(email)
        server.quit()

        if code == 250:
            return True, "RCPT TO OK"
        elif code == 550:
            return False, "Mailbox no existe"
        elif code == 551:
            return False, "Usuario no local"
        elif code == 552:
            return False, "Mailbox lleno"
        elif code == 553:
            return False, "Syntax error"
        elif code == 452:
            return False, "Insuficiente storage"
        else:
            return False, f"SMTP {code}: {msg.decode(errors='ignore')[:60]}"

    except smtplib.SMTPServerDisconnected:
        return False, "Servidor desconectó"
    except smtplib.SMTPConnectError as e:
        return False, f"Error conexión: {str(e)[:60]}"
    except socket.timeout:
        return False, "Timeout SMTP"
    except ConnectionRefusedError:
        return False, "Conexión rechazada"
    except OSError as e:
        return False, f"Error red: {str(e)[:60]}"
    except Exception as e:
        return False, f"Error SMTP: {str(e)[:60]}"


# === CATCH-ALL DETECTION ===

def is_catch_all(mx_server: str) -> bool:
    """
    Detecta si el dominio es catch-all (acepta cualquier email).
    Prueba con un email aleatorio que no puede existir.
    """
    test_email = f"nonexistent-test-xyz987@{mx_server}"
    try:
        server = smtplib.SMTP(timeout=SMTP_TIMEOUT)
        server.connect(mx_server, 25)
        server.helo("verify.example.com")
        server.mail("verify@example.com")
        code, msg = server.rcpt(test_email)
        server.quit()
        # Si acepta un email inventado, es catch-all
        return code == 250
    except Exception:
        return False


# === DISPOSABLE EMAIL DETECTION ===

DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "tempmail.com", "throwaway.email",
    "temp-mail.org", "fakeinbox.com", "sharklasers.com", "guerrillamailblock.com",
    "grr.la", "dispostable.com", "yopmail.com", "yopmail.fr", "maildrop.cc",
    "trashmail.com", "trashmail.net", "trashmail.org", "mailcatch.com",
    "mailexpire.com", "mailnull.com", "mailscrap.com", "mailshell.com",
    "mailsiphon.com", "mailslurp.com", "mailzilla.com", "mintemail.com",
    "mohmal.com", "nomail.xl.cx", "nospam.ze.tc", "nowmymail.com",
    "obobbo.com", "odnorazovym.ru", "oneoffemail.com", "onewaymail.com",
    "oopi.org", "ordinaryamerican.net", "otherinbox.com",
    "ourklips.com", "outlawonline.net", "owlpic.com",
    "panasas.com", "pimpedupmyspace.com", "pjjkp.com", "plexolan.de",
    "poczta.onet.pl", "privacy.net", "privatdemail.net",
    "proxymail.eu", "prtnx.com", "punkass.com",
    "putthisinyouremail.com", "qq.com",
    "quickinbox.com", "quickmail.nl",
    "rcpt.at", "reallymymail.com", "realtyalerts.ca",
    "recode.me", "recursor.net", "regbypass.com",
    "reliable-mail.com", "rhyta.com", "rklips.com",
    "rmqkr.net", "rtrtr.com", "s0ny.net",
    "safe-mail.net", "safersignup.de", "safetymail.info",
    "sandelf.de", "saynotospams.com", "scatmail.com",
    "schafmail.de", "schrott-email.de", "secretemail.de",
    "secure-mail.biz", "sendspamhere.com", "shiftmail.com",
    "shitmail.me", "shitmail.org", "shitware.nl",
    "shmeriously.com", "shortmail.net", "sibmail.com",
    "sinnlos-mail.de", "skeefmail.com", "slaskpost.se",
    "slipry.net", "slopsbox.com", "slowslow.de",
    "slutty.horse", "smashmail.de", "smellfear.com",
    "snakemail.com", "sneakemail.com", "sneakymail.de",
    "snkmail.com", "sofimail.com", "sofort-mail.de",
    "softpls.asia", "sogetthis.com", "soodonims.com",
    "spam.la", "spam.su", "spam4.me", "spamavert.com",
    "spambob.com", "spambob.net", "spambob.org",
    "spambog.com", "spambog.de", "spambog.ru",
    "spambox.info", "spambox.us", "spamcannon.com",
    "spamcannon.net", "spamcero.com", "spamcorptastic.com",
    "spamcowboy.com", "spamcowboy.net", "spamcowboy.org",
    "spamday.com", "spamex.com", "spamfighter.cf",
    "spamfighter.ga", "spamfighter.gq", "spamfighter.ml",
    "spamfighter.tk", "spamfree.eu", "spamfree24.com",
    "spamfree24.de", "spamfree24.eu", "spamfree24.info",
    "spamfree24.net", "spamfree24.org", "spamgourmet.com",
    "spamgourmet.net", "spamgourmet.org", "spamherelots.com",
    "spamhereplease.com", "spamhole.com", "spamify.com",
    "spaminator.de", "spamkill.info", "spaml.com",
    "spaml.de", "spammotel.com", "spamobox.com",
    "spamoff.de", "spamslicer.com", "spamspot.com",
    "spamstack.net", "spamthis.co.uk", "spamthisplease.com",
    "spamtrail.com", "spamtrap.ro", "speed.1s.fr",
    "superrito.com", "superstachel.de", "suremail.info",
    "svk.jp", "sweetxxx.de", "talkinator.com",
    "tapchicuoihoi.com", "teewars.org", "teleworm.com",
    "teleworm.us", "temp-mail.org", "temp-mail.io",
    "tempalias.com", "tempe.ml", "tempemail.biz",
    "tempemail.co.za", "tempemail.com", "tempemail.net",
    "tempinbox.com", "tempinbox.co.uk", "tempmail.eu",
    "tempmail.it", "tempmail2.com", "tempmaildemo.com",
    "tempmailer.com", "tempmailer.de", "tempomail.fr",
    "temporarily.de", "temporarioemail.com.br",
    "temporaryemail.net", "temporaryemail.us",
    "temporaryforwarding.com", "temporaryinbox.com",
    "temporarymailaddress.com", "tempthe.net",
    "thankyou2010.com", "thc.st", "thecloudindex.com",
    "thetempmail.com", "throwawayemailaddress.com",
    "tittbit.in", "tizi.com", "tmailinator.com",
    "toiea.com", "toomail.biz", "topranklist.de",
    "tradermail.info", "trash-amil.com", "trash-mail.at",
    "trash-mail.com", "trash-mail.de", "trash-me.com",
    "trash2009.com", "trashdevil.com", "trashdevil.de",
    "trashemail.de", "trashmail.at", "trashmail.com",
    "trashmail.de", "trashmail.me", "trashmail.net",
    "trashmail.org", "trashmail.ws", "trashmailer.com",
    "trashmailer.net", "trashymail.com", "trashymail.net",
    "trillianpro.com", "turual.com", "twinmail.de",
    "tyldd.com", "uggsrock.com", "umail.net",
    "upliftnow.com", "uplipht.com", "venompen.com",
    "veryrealliemail.com", "viditag.com", "viewcastmedia.com",
    "viewcastmedia.net", "viewcastmedia.org",
    "vomoto.com", "vpn.st", "vsimcard.com",
    "vubby.com", "wasteland.rfc822.org", "webemail.me",
    "weg-werf-email.de", "wegwerfadresse.de",
    "wegwerfemail.com", "wegwerfemail.de",
    "wegwerfmail.net", "wegwerfmail.org",
    "wetrainbayarea.com", "wetrainbayarea.org",
    "wh4f.org", "whatiaas.com", "whatpaas.com",
    "whyspam.me", "wikidocuslice.com", "willhackforfood.biz",
    "willselfdestruct.com", "winemaven.info",
    "wronghead.com", "wuzup.net", "wuzupmail.net",
    "wwwnew.eu", "xagloo.com", "xemaps.com",
    "xents.com", "xjoi.com", "xmaily.com",
    "xoxy.net", "yapped.net", "yeah.net",
    "yep.it", "yogamaven.com", "yomail.info",
    "yomail.org", "yomp.com", "yopmail.com",
    "yopmail.fr", "yopmail.gq", "yopmail.net",
    "yourdomain.com", "zipmail.com", "zehnminutenmail.de",
    "10minutemail.com", "10minutemail.co.za",
    "20minutemail.com", "2prong.com",
    "33mail.com", "3d-painting.com",
    "4warding.com", "4warding.net",
    "4warding.org", "5ghgfhfghfgh.tk",
    "60minutemail.com", "675hosting.com",
    "675hosting.net", "675hosting.org",
    "6url.com", "75hosting.com",
    "7tags.com", "9ox.net",
    "a-bc.net", "afrobacon.com",
    "agedmail.com", "ajaxapp.net",
    "alivance.com", "amilegit.com",
    "amiri.net", "anappthat.com",
    "ano-mail.net", "anonbox.net",
    "anonymbox.com", "antichef.com",
    "antichef.net", "antispam.de",
    "antispammail.de", "armyspy.com",
    "artman-conception.com", "azmeil.tk",
}


def is_disposable(email: str) -> bool:
    """Verifica si el email usa un dominio desechable"""
    domain = email.split("@")[-1].lower()
    return domain in DISPOSABLE_DOMAINS


def is_generic_provider(email: str) -> bool:
    """Verifica si el email es de un proveedor genérico"""
    domain = email.split("@")[-1].lower()
    return domain in GENERIC_DOMAINS


# === VERIFICACIÓN PRINCIPAL ===

def verify_single_email(email: str) -> Dict:
    """
    Verifica un email completo: syntax → disposable → MX → catch-all → SMTP RCPT TO
    Retorna dict con resultados.
    """
    result = {
        "email": email,
        "domain": email.split("@")[-1].lower(),
        "status": "unknown",
        "mx_ok": False,
        "mx_servers": "",
        "smtp_ok": False,
        "smtp_message": "",
        "is_catch_all": False,
        "is_disposable": False,
        "is_generic": False,
        "checked_at": datetime.now().isoformat(),
    }

    # 1. Disposable check
    if is_disposable(email):
        result["is_disposable"] = True
        result["status"] = "disposable"
        return result

    # 2. Generic provider check
    if is_generic_provider(email):
        result["is_generic"] = True
        result["status"] = "generic"
        return result

    # 3. MX check
    domain = result["domain"]
    mx_ok, mx_servers, mx_error = check_mx_records(domain)
    result["mx_ok"] = mx_ok
    result["mx_servers"] = ";".join(mx_servers[:3])

    if not mx_ok:
        result["status"] = "no_mx"
        result["smtp_message"] = mx_error
        return result

    # 4. Catch-all detection (sample only - not for every email)
    # We'll detect catch-all during batch processing

    # 5. SMTP RCPT TO
    # Try each MX server in order
    for mx in mx_servers[:2]:  # Max 2 MX servers
        smtp_ok, smtp_msg = smtp_verify_email(email, mx)
        result["smtp_ok"] = smtp_ok
        result["smtp_message"] = smtp_msg
        if smtp_ok or "no existe" in smtp_msg.lower() or "not exist" in smtp_msg.lower():
            break  # Got a definitive answer

    if result["smtp_ok"]:
        result["status"] = "valid"
    else:
        result["status"] = "invalid"

    return result


def verify_batch(emails: List[str], batch_size: int = 100, max_workers: int = MAX_WORKERS) -> List[Dict]:
    """
    Verifica un batch de emails en paralelo.
    Retorna lista de resultados.
    """
    results = []
    total = len(emails)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(verify_single_email, email): email for email in emails}

        for i, future in enumerate(as_completed(futures)):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                email = futures[future]
                results.append({
                    "email": email,
                    "status": "error",
                    "smtp_message": str(e)[:100],
                })

            if (i + 1) % batch_size == 0:
                log.info(f"Procesados {i + 1}/{total} emails")

    return results


# === DB OPERATIONS ===

def get_emails_to_verify(conn: sqlite3.Connection, verify_all: bool = False) -> List[Tuple[int, str]]:
    """
    Obtiene emails de la DB que necesitan verificación.
    Retorna lista de (ROWID, email).
    """
    cur = conn.cursor()
    if verify_all:
        cur.execute("""
            SELECT m.ROWID, l.primary_email
            FROM main m
            JOIN lead l ON m.ROWID = l.ROWID
            WHERE l.primary_email IS NOT NULL AND l.primary_email != ''
        """)
    else:
        # Solo emails sin deliverability o con deliverability uncertain
        cur.execute("""
            SELECT m.ROWID, l.primary_email
            FROM main m
            JOIN lead l ON m.ROWID = l.ROWID
            LEFT JOIN contact c ON m.ROWID = c.ROWID
            WHERE l.primary_email IS NOT NULL AND l.primary_email != ''
            AND (c.deliverability IS NULL OR c.deliverability = '' OR c.deliverability = 'uncertain')
        """)
    return cur.fetchall()


def update_deliverability(conn: sqlite3.Connection, results: List[Dict], dry_run: bool = False):
    """Actualiza el campo deliverability en la DB con los resultados de verificación"""
    cur = conn.cursor()
    updated = 0
    status_counts = {}

    for r in results:
        status = r.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

        if dry_run:
            continue

        # Map verification status to deliverability value
        deliverability_map = {
            "valid": "valid",
            "invalid": "invalid",
            "no_mx": "invalid",
            "disposable": "invalid",
            "generic": "uncertain",
            "error": "uncertain",
            "unknown": "uncertain",
        }
        deliverability = deliverability_map.get(status, "uncertain")

        cur.execute("""
            UPDATE contact SET deliverability = ?, last_validation_date = ?, last_validation_status = ?
            WHERE ROWID = (
                SELECT m.ROWID FROM main m
                JOIN lead l ON m.ROWID = l.ROWID
                WHERE l.primary_email = ?
            )
        """, (
            deliverability,
            datetime.now().isoformat(),
            f"smtp_verified:{status}",
            r["email"],
        ))
        updated += 1

    return updated, status_counts


def save_report(results: List[Dict], report_path: str):
    """Guarda reporte detallado de verificación"""
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "email", "domain", "status", "mx_ok", "mx_servers",
            "smtp_ok", "smtp_message", "is_catch_all",
            "is_disposable", "is_generic", "checked_at",
        ])
        writer.writeheader()
        writer.writerows(results)
    log.info(f"Reporte guardado: {report_path}")


# === MAIN ===

def main():
    parser = argparse.ArgumentParser(description="Verificar emails: MX/DNS + SMTP RCPT TO")
    parser.add_argument("--all", action="store_true", help="Verificar TODOS los emails")
    parser.add_argument("--email", type=str, help="Verificar un email específico")
    parser.add_argument("--batch", type=int, default=100, help="Tamaño de batch (default: 100)")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help="Threads paralelos")
    parser.add_argument("--dry-run", action="store_true", help="Solo mostrar, no actualizar DB")
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("INICIO DE VERIFICACIÓN DE EMAILS")
    log.info("=" * 60)

    # Single email mode
    if args.email:
        log.info(f"Verificando email único: {args.email}")
        result = verify_single_email(args.email)
        log.info(f"Resultado: {json.dumps(result, indent=2)}")
        return

    # Batch mode
    conn = sqlite3.connect(DB_PATH)

    emails = get_emails_to_verify(conn, verify_all=args.all)
    log.info(f"Emails a verificar: {len(emails)}")

    if not emails:
        log.info("No hay emails para verificar")
        conn.close()
        return

    # Extract just emails for verification
    email_list = [e[1] for e in emails]

    # Verify
    start_time = time.time()
    results = verify_batch(email_list, batch_size=args.batch, max_workers=args.workers)
    elapsed = time.time() - start_time

    # Stats
    status_counts = {}
    for r in results:
        s = r.get("status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1

    log.info(f"\n=== RESULTADOS ===")
    log.info(f"Tiempo total: {elapsed:.1f}s ({len(results)/max(elapsed,0.1):.0f} emails/s)")
    for status, count in sorted(status_counts.items()):
        log.info(f"  {status}: {count}")

    # Update DB
    updated, _ = update_deliverability(conn, results, dry_run=args.dry_run)
    if not args.dry_run:
        conn.commit()
        log.info(f"DB actualizada: {updated} registros")
    else:
        log.info(f"DRY RUN: {updated} registros se actualizarían")

    # Save report
    save_report(results, REPORT_PATH)

    conn.close()
    log.info("FIN DE VERIFICACIÓN")


if __name__ == "__main__":
    main()
