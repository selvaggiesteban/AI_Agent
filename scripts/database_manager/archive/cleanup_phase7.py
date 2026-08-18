"""
Fase 7: Normalizar columna campaigns
- Decodificar asuntos RFC 2047
- Migrar formato viejo ID:...|Sender:... al nuevo
- Formato nuevo: campaign, list, subject, sender, date, response
- Separador entre entradas: " || "
"""

import sqlite3
import os
import re
import quopri
from datetime import datetime

DB_PATH = os.path.join("data", "inputs", "contacts.db")


def decode_rfc2047(text):
    """Decodificar asuntos RFC 2047 (=?utf-8?q?...?=)."""
    if not text:
        return text
    # Patron: =?charset?encoding?content?=
    pattern = r"=\?([^?]+)\?([qQbB])\?([^?]+)\?="
    matches = list(re.finditer(pattern, text))
    if not matches:
        return text

    result = text
    for match in matches:
        charset = match.group(1)
        encoding = match.group(2).lower()
        encoded = match.group(3)
        full_match = match.group(0)

        if encoding == "q":
            # Quoted-printable
            decoded = quopri.decodestring(encoded.encode("ascii", errors="ignore"))
        elif encoding == "b":
            # Base64
            import base64
            decoded = base64.b64decode(encoded)
        else:
            decoded = encoded.encode()

        try:
            decoded_str = decoded.decode(charset, errors="replace")
        except (LookupError, UnicodeDecodeError):
            decoded_str = decoded.decode("utf-8", errors="replace")

        # Reemplazar underscores con espacios (variantes Q)
        decoded_str = decoded_str.replace("_", " ")

        result = result.replace(full_match, decoded_str)

    return result


def parse_old_format(entry):
    """Parsear formato viejo: ID:...|Subj:...|Sender:...|Date:..."""
    fields = {}
    for part in entry.split("|"):
        if ":" in part:
            key, val = part.split(":", 1)
            fields[key.strip()] = val.strip()

    campaign = fields.get("ID", "")
    subject = decode_rfc2047(fields.get("Subj", "Desconocido"))
    sender = fields.get("Sender", "")
    date = fields.get("Date", "")

    # Formato nuevo: campaign, list, subject, sender, date, response
    return f"{campaign},,{subject},{sender},{date},"


def parse_type_format(entry):
    """Parsear formato Type:...|From:...|To:...|Subj:...|Date:..."""
    fields = {}
    for part in entry.split("|"):
        if ":" in part:
            key, val = part.split(":", 1)
            fields[key.strip()] = val.strip()

    entry_type = fields.get("Type", "")
    subject = decode_rfc2047(fields.get("Subj", ""))
    sender = fields.get("From", fields.get("Sender", ""))
    date = fields.get("Date", "")
    to = fields.get("To", "")
    name = fields.get("Name", "")
    reason = fields.get("Reason", "")
    code = fields.get("Code", "")
    campaign_name = fields.get("Name", "")

    if entry_type == "sent":
        return f",{to},{subject},{sender},{date},"
    elif entry_type == "received":
        return f",{to},{subject},{sender},{date},"
    elif entry_type == "pending":
        draft = fields.get("Draft", "")
        return f",,{subject},{sender},{date},pending"
    elif entry_type == "campaign":
        return f"{campaign_name},,{subject},{sender},{date},"
    elif entry_type == "bounce":
        return f",,,{sender},{date},bounce:{reason}"
    else:
        return f",,{subject},{sender},{date},"


def normalize_campaigns(conn):
    """Normalizar toda la columna campaigns."""
    cur = conn.cursor()
    cur.execute("SELECT ROWID, campaigns FROM main WHERE campaigns IS NOT NULL AND campaigns != ''")
    rows = cur.fetchall()
    print(f"Contactos con campaigns: {len(rows)}")

    updated = 0
    skipped = 0
    decoded_count = 0

    for rowid, campaigns in rows:
        entries = campaigns.split(" || ")
        new_entries = []

        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue

            # Detectar formato
            if entry.startswith("Type:"):
                new_entry = parse_type_format(entry)
            elif entry.startswith("ID:"):
                new_entry = parse_old_format(entry)
            elif ",," in entry:
                # Ya en formato nuevo
                new_entry = entry
            else:
                # Formato desconocido, intentar parsear
                new_entry = entry

            # Verificar si se decodifico RFC 2047
            if "=?" in entry and "=?" not in new_entry:
                decoded_count += 1

            new_entries.append(new_entry)

        new_campaigns = " || ".join(new_entries)

        if new_campaigns != campaigns:
            cur.execute("UPDATE main SET campaigns = ? WHERE ROWID = ?", (new_campaigns, rowid))
            updated += 1
        else:
            skipped += 1

    conn.commit()
    print(f"Actualizados: {updated}")
    print(f"Sin cambios: {skipped}")
    print(f"Asuntos RFC 2047 decodificados: {decoded_count}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)

    print("=== Fase 7: Normalizar campaigns ===\n")

    conn = sqlite3.connect(db_path)
    normalize_campaigns(conn)
    conn.close()

    print("\n=== COMPLETADO ===")
