"""
Fase 7b: Decodificar RFC 2047 restantes en campaigns
"""

import sqlite3
import os
import re
import quopri

DB_PATH = os.path.join("data", "inputs", "contacts.db")


def decode_rfc2047(text):
    """Decodificar asuntos RFC 2047 (=?utf-8?q?...?=)."""
    if not text or "=?" not in text:
        return text
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
            decoded = quopri.decodestring(encoded.encode("ascii", errors="ignore"))
        elif encoding == "b":
            import base64
            decoded = base64.b64decode(encoded)
        else:
            decoded = encoded.encode()

        try:
            decoded_str = decoded.decode(charset, errors="replace")
        except (LookupError, UnicodeDecodeError):
            decoded_str = decoded.decode("utf-8", errors="replace")

        decoded_str = decoded_str.replace("_", " ")
        result = result.replace(full_match, decoded_str)

    return result


def fix_campaigns(conn):
    """Decodificar RFC 2047 y normalizar formato Sender:... en campaigns."""
    cur = conn.cursor()
    cur.execute("SELECT ROWID, campaigns FROM main WHERE campaigns LIKE '%=?%'")
    rows = cur.fetchall()
    print(f"Contacts with RFC 2047: {len(rows)}")

    updated = 0
    for rowid, campaigns in rows:
        entries = campaigns.split(" || ")
        new_entries = []

        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue

            # Si tiene Sender:...|Subj:...|Date:... (formato intermedio)
            if entry.startswith("Sender:") and "|Subj:" in entry:
                fields = {}
                for part in entry.split("|"):
                    if ":" in part:
                        key, val = part.split(":", 1)
                        fields[key.strip()] = val.strip()

                subject = decode_rfc2047(fields.get("Subj", ""))
                sender = fields.get("Sender", "")
                date = fields.get("Date", "")

                # Buscar Msg: para extraer snippet
                msg = fields.get("Msg", "")
                if msg:
                    msg = msg[:300]

                new_entry = f",,{subject},{sender},{date},"
                new_entries.append(new_entry)
            elif "=?" in entry:
                # Decodificar RFC 2047 en cualquier otro formato
                decoded = decode_rfc2047(entry)
                new_entries.append(decoded)
            else:
                new_entries.append(entry)

        new_campaigns = " || ".join(new_entries)
        if new_campaigns != campaigns:
            cur.execute("UPDATE main SET campaigns = ? WHERE ROWID = ?", (new_campaigns, rowid))
            updated += 1

    conn.commit()
    print(f"Updated: {updated}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)

    print("=== Fase 7b: Decodificar RFC 2047 restantes ===\n")

    conn = sqlite3.connect(db_path)
    fix_campaigns(conn)
    conn.close()

    # Verify
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM main WHERE campaigns LIKE '%=?%'")
    remaining = cur.fetchone()[0]
    print(f"\nRemaining RFC 2047: {remaining}")
    conn.close()

    print("\n=== COMPLETADO ===")
