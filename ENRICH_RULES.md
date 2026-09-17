# ENRICH_RULES.md — Enrichment Rules for contacts.db

> **Last Update:** 2026-07-27
> **DB:** `data/inputs/contacts.db` (SQLite, normalized v4, ~124K contacts)

---

## 1. Email Validation — Existing Code

### 1.1 Scripts already implementing validation

| Script | Location | Action | Rules |
|---|---|---|---|
| `archive/cleanup_phase4.py` | `scripts/database_manager/archive/` | Removes junk emails from DB | 12 exact emails + 2 domains (`example.com`, `ejemplo.com`) + 2 substrings (`sentry`, `wixpress`) |
| `enrich_campaign_logs.py` | `scripts/database_manager/` | Filters junk when importing SUCCESS/FAILURE logs | `JUNK_PATTERNS`: sentry, wixpress, example, test, demo, `@2x.png`, `.js`, `username@domain`, `your@mail`, `juan.perez`, beispiel, ejemplo, mysite |
| `enrich_gmail_csvs.py` | `scripts/database_manager/` | Filters junk when importing Gmail CSVs | Same `JUNK_PATTERNS` |
| `enrich_identity_maps.py` | `scripts/database_manager/` | Filters junk when importing identity maps | Same `JUNK_PATTERNS` |
| `campaign_engine.py` | `scripts/e-mail_marketing_manager/e-mail_marketing_campaigns/` | Filters when creating campaigns | Regex + `exclude_patterns`: sentry, wixpress, noreply, abuse |
| `generate_5_csvs.py` | `scripts/e-mail_marketing_manager/` | Detects auto-replies | `AUTO_REPLY_PATTERNS`: auto-reply, mailer-daemon, noreply, postmaster, bounce, donotreply, etc. (13 patterns) |

### 1.2 Consolidated Validation Rules

**Base Regex:**
```
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

**Reject Domains** (substrings in domain):
`sentry`, `wixpress`, `example`, `ejemplo`, `test`, `demo`

**Reject Patterns** (substrings in full email):
`@2x.png`, `@2x.webp`, `.js`, `username@domain`, `your@mail`, `juan.perez`, `beispiel`, `ejemplo`, `mysite`

**Auto-reply / system reject** (prefix or substring):
`noreply`, `no-reply`, `mailer-daemon`, `postmaster`, `abuse`, `auto-reply`, `donotreply`, `auto_submit`

**Exact Placeholder Emails** (reject if match):
`yourname@email.com`, `user@domain.com`, `name@example.com`, `john@doe.com`, `info@yourdomain.com`, `info@website.com`, `hello@mycompany.es`, `email@example.com`, `example@mail.com`, `email@example.com`, `name@mail.com`, `theratio_interior@mail.com`

### 1.3 Rule for multiple emails in one field

The DB has two columns: `lead.primary_email` and `lead.secondary_emails`.

If the CSV contains multiple emails in the `emails` field:
- **First** $\rightarrow$ `lead.primary_email`
- **Others** $\rightarrow$ `lead.secondary_emails` (separated by `;`)
- Each individual email must pass validation before being saved.

### 1.4 Maximum Coverage Rule

**Always insert ALL new emails from all rows**, not just the first email. Every valid email that does not exist in the DB should generate a new contact.

- A CSV with 38,869 rows can contain ~5,177 new unique emails.
- If only the first email of each row is taken, ~565 emails (secondary) are lost.
- Contacts with more than 1 email can receive more than 1 campaign (one for each email).

---

## 2. Encoding (Mojibake) — Existing Code

### 2.1 Current Script

`cleanup_phase3.py:153-171` $\rightarrow$ `fix_title_encoding()` function

- Only covers the `title` field.
- Defines 16 replacement patterns.
- **Does NOT cover**: `city` (1,158 rows affected), `country` (841), `sector` (14), `address`.

### 2.2 Detected Mojibake Patterns

**Double-encoded UTF-8** (most common):
```
Ã± → ñ    Ã© → é    Ã¡ → á    Ã³ → ó
Ã­ → í    Ã¼ → ü    Ã  → à    Ã¨ → è
Ã´ → ò    Ã¢ → a    Ã¤ → ä    Ã¶ → ö
Ã§ → ç    Ã® → î    Ã´ → ô
```

**Â prefix patterns:**
```
Â° → °    Âº → º    Â· → ·
```

**Triple-encoded** (isolated cases):
```
Ã³nico → único    Ã³noma → autónoma
```

### 2.3 Application Rule

- Apply ONLY if the string contains mojibake patterns (detect with `Ã` or `Â`).
- Do not overwrite if the correction makes no sense.
- Log each applied correction (field, ROWID, value before/after).
- Apply to ALL text fields: `title`, `sector`, `city`, `province`, `country`, `address`.

---

## 3. Gosom CSV $\rightarrow$ contacts.db Mapping Rules

### 3.1 Gosom CSV Structure (35 columns)

```
input_id, link, title, category, address, open_hours, popular_times,
website, phone, plus_code, review_count, review_rating,
reviews_per_rating, latitude, longitude, cid, status, descriptions,
reviews_link, thumbnail, timezone, price_range, data_id,
street_view_url, place_id, images, reservations, order_online,
menu, owner, complete_address, about, user_reviews,
user_reviews_extended, emails
```

### 3.2 Field Mapping

| CSV Column | DB Column | Type | Transformation |
|---|---|---|---|
| `title` | `main.title` | TEXT | No transformation |
| `category` | `main.sector` | TEXT | No transformation |
| `address` | `main.address` | TEXT | No transformation |
| `complete_address` $\rightarrow$ `city` | `main.city` | TEXT | Parse JSON, extract `city` field |
| `complete_address` $\rightarrow$ `state` | `main.province` | TEXT | Parse JSON, extract `state` field |
| `complete_address` $\rightarrow$ `country` | `main.country` | TEXT | Parse JSON, extract `country` field |
| *(fixed)* | `main.entity_type` | TEXT | `"company"` |
| `website` | `lead.website` | TEXT | Add `https://` if protocol is missing |
| `phone` | `lead.phone` | TEXT | No transformation |
| `link` | `lead.google_maps` | TEXT | Only if the contact is new in the DB |
| `emails` | `lead.primary_email` | TEXT | Validate with regex + blacklist. If multiple: first $\rightarrow$ `primary_email`, others $\rightarrow$ `secondary_emails` (separated by `;`) |
| *(fixed)* | `contact.date_added` | TEXT | `datetime.now().isoformat()` |

### 3.3 Ignored CSV Fields

`input_id`, `open_hours`, `popular_times`, `plus_code`, `review_count`, `review_rating`, `reviews_per_rating`, `latitude`, `longitude`, `cid`, `status`, `descriptions`, `reviews_link`, `thumbnail`, `timezone`, `price_range`, `data_id`, `street_view_url`, `place_id`, `images`, `reservations`, `order_online`, `menu`, `owner`, `about`, `user_reviews`, `user_reviews_extended`

### 3.4 .txt Files (email list)

`.txt` files contain emails separated by commas (not column-based CSVs).
- Import each email as a new contact.
- `lead.primary_email` = the email.
- `main.entity_type` = `"company"`.
- `contact.date_added` = `datetime.now().isoformat()`.
- Other fields = NULL.
- Apply same email validation.

---

## 4. Deduplication

### 4.1 Deduplication Key

**Primary:** `main.title` + `main.city` (both normalized, lowercase, no extra spaces).

### 4.2 Handling Duplicates

Print to console:
```
DUPLICATE FOUND:
  Existing: ROWID=X | title="..." | city="..." | email="..."
  New:     title="..." | city="..." | email="..."
  Options: [S]kip / [U]pdate / [M]erge
```

Pause and wait for user input.

- **Skip**: ignore the new one, keep existing.
- **Update**: overwrite empty fields of existing with new values.
- **Merge**: combine fields (do not overwrite existing data).

---

## 5. Implementation Notes

- Enrichment scripts must import these rules as a reference.
- Regex and blacklist lists must be maintained in a single place (this file or a Python module).
- Any rule change is documented here with a date.

---

## 6. Data Enrichment — Results (2026-07-20)

### 6.1 Data Sources — Import Status

| Source | Files | Unique Emails | Imported | Status |
|--------|----------|---------------|------------|--------|
| Brevo CSV (base_tvmas.csv) | 1 | 9,310 | 9,310 | ✅ 99.96% coverage |
| Brevo CSV (brevo_10042026.csv) | 1 | 12,763 | ~12,763 | ✅ Derived from base_tvmas |
| Brevo CSV (brevo_consolidada_total.csv) | 1 | 12,763 | ~12,763 | ✅ Derived from base_tvmas |
| Gosom General | 1 | 5,347 | 5,347 | ✅ import_gosom_general.py |
| Gosom RRHH | 1 | 5,434 | 5,434 | ✅ import_rrhh_gosom.py |
| Gosom Root (44 CSVs) | 44 | ~4,500 | 303 | ✅ import_gosom_root.py |
| WhatsApp VCFs | 13 | 92 | 92 | ✅ import_vcf.py (phone-only) |
| XLSX Trade Fairs (62 files) | 62 | ~34,000 | 0 | ✅ Already in DB (duplicates) |
| Blacklist (REJECTED CONTACTS) | 1 | 198 | 198 | ✅ Marked BLACKLISTED |
| Google Contacts (7 CSVs) | 7 | ~6,600 | 0 | ✅ Already in DB (duplicates) |
| Pre-existing (date_added=NULL) | — | 99,261 | 99,261 | ✅ Brevo legacy import |

### 6.2 Verified Sources (Gap Closed)

| Source | Files | Unique Emails | Result |
|--------|----------|---------------|-----------|
| Gosom webdata/ (36 UUID CSVs) | 36 | 792 | ✅ Already in DB (import_gosom_root.py) |
| Gosom web_marketing_caba.csv | 1 | 231 | ✅ Already in DB (import_gosom_root.py) |
| contacts Mailrelay | 1 | 71 | ✅ Already in DB (import_mailrelay.py created) |
| contacts selvaggiesteban (phone-only) | 1 | 2,643 | ✅ import_phone_contacts.py (dedup 15K $\rightarrow$ 2.6K) |
| LinkedIn people/authors CSVs | 2 | 118 | ✅ import_linkedin_profiles.py (no email/tel) |
| YOLANDA.csv | 1 | ~500 | ⏳ Non-standard format (pending) |

### 6.3 DB Current State

| Metric | Value |
|---------|-------|
| Total contacts | 123,763 |
| With valid email | 116,747 |
| With phones | 59,739 |
| With LinkedIn | 114 |
| Phone-only (no email) | 5,738 |
| With social networks | 0 (8 columns 100% NULL) |
| With sector | ~92,000 |
| With website | ~121,000 |
| BLACKLISTED | 198 |
| Pre-existing (no date) | 99,261 |
| Imported by scripts | ~24,500 |

### 6.4 Import Scripts and Utilities Created

| Script | Source | Status |
|--------|--------|--------|
| `config.py` | Centralized configuration | ✅ Active |
| `utils.py` | Shared utilities | ✅ Active |
| `verify_imported.py` | Source verification | ✅ Executed |
| `import_vcf.py` | WhatsApp VCFs | ✅ Completed (92 contacts) |
| `import_gosom_root.py` | Gosom root CSVs | ✅ Completed (303 contacts) |
| `import_gosom_general.py` | Gosom General CSV | ✅ Completed (5,347 contacts) |
| `import_rrhh_gosom.py` | Gosom RRHH CSV | ✅ Completed (5,434 contacts) |
| `import_xlsx.py` | XLSX trade fairs | ✅ Executed (0 new, all duplicates) |
| `import_blacklist.py` | REJECTED CONTACTS.docx | ✅ Completed (198 blacklisted) |
| `import_google_contacts.py` | Google Contacts CSVs | ✅ Executed (0 new, 2 tel updated) |
| `import_gosom_webdata.py` | Gosom webdata/ + web_marketing_caba | ✅ Executed (0 new, all already in DB) |
| `import_mailrelay.py` | Mailrelay CSV | ✅ Executed (0 new, all already in DB) |
| `import_phone_contacts.py` | contacts selvaggiesteban (phone-only) | ✅ 2,643 contacts imported |
| `import_linkedin_profiles.py` | LinkedIn people/authors CSVs | ✅ 118 profiles imported |
| `cleanup_duplicate_emails.py` | Duplicate email dedup | ✅ Active |
| `remove_duplicates.py` | CSV dedup | ✅ Active |
| `remove_duplicates_xlsx.py` | XLSX dedup | ✅ Active |
| `enrich_abogados.py` | Lawyer enrichment via web scraping | ✅ Active |
| `enumerate_prefixes.py` | Email prefix analysis | ✅ Active |
| `archive/cleanup_phase3.py` | Archived cleanup (encoding) | 📦 Archived |
| `archive/cleanup_phase4.py` | Archived cleanup (junk emails) | 📦 Archived |
| `archive/cleanup_phase7.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase8.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase9.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase10.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase11.py` | Archived cleanup | 📦 Archived |
| `archive/migrate_v4.py` | Archived DB v4 migration | 📦 Archived |

---

## 7. Schema Update — campaign.email_used

### 7.1 New Column

```sql
ALTER TABLE campaign ADD COLUMN email_used TEXT;
```

Records the exact email of the recipient to whom each campaign was sent. Allows a contact with multiple emails to receive multiple campaigns (one per email).

### 7.2 Usage

- When sending a campaign: `campaign.email_used = recipient_email`
- When querying campaigns: filter by `email_used` to know which email was used
- Backward compatibility: existing rows remain with `email_used = NULL`

---

## 8. Schema Update — campaign.message

### 8.1 New Column

```sql
ALTER TABLE campaign ADD COLUMN message TEXT;
```

Records the body of the message sent in each campaign. Allows querying the exact content received by each contact.

### 8.2 Usage

- When sending a campaign: `campaign.message = message_body`
- When querying campaigns: filter by `message` to know what content was sent
- Backward compatibility: existing rows remain with `message = NULL`

---

## 9. Enrichment Campaign LANÚS-03082026

### 9.1 Campaign Data

| Field | Value |
|-------|-------|
| `list_val` | `LANÚS-03082026` |
| `subject` | Computer Technical Service and Technology Products |
| `type` | `lanus_servicio_tecnico` |
| `message` | Hello, good morning. How are you? I hope very well. I am contacting you to provide technical service for computers and technology products. We provide solutions for both individuals and shops and companies in the area. If you need repair, maintenance or equipment, you can contact us. I remain at your disposal for whatever you need. Kind regards |

### 9.2 Results

| Metric | Value |
|---------|-------|
| Execution Date | 2026-08-03 |
| Contacts inserted | 228 |
| Accounts used | 12 (19 emails each) |
| Logs parsed | `log_lanus_cycle_20260803_112153.txt` (12) + `log_lanus_cycle_20260803_112606.txt` (216) |
| Script | `scripts/database_manager/enrich_lanus_campaign.py` |
| Backup | `data/inputs/contacts_backup_before_lanus_enrich.db` |

### 9.3 Accounts and Distribution

| Account | Emails sent |
|--------|----------------|
| wwwlanuscomputacion@gmail.com | 19 |
| adrianaavila131969@gmail.com | 19 |
| fernando1141967@gmail.com | 19 |
| selvaggiesteban9@gmail.com | 19 |
| selvaggiesteban4@gmail.com | 19 |
| selvaggiesteban11@gmail.com | 19 |
| marketing1a1oficial@gmail.com | 19 |
| selvaggiconsultores@gmail.com | 19 |
| estebanmfwd@gmail.com | 19 |
| selvaggiesteban1@gmail.com | 19 |
| selvaggiesteban2@gmail.com | 19 |
| marcelagomez7799@gmail.com | 19 |

---

## 10. Enrichment Campaign BA/CABA-03082026

### 10.1 Campaign Data

| Field | Value |
|-------|-------|
| `list_val` | `BA-CABA-03082026` |
| `subject` | Computer Technical Service and Technology Products |
| `type` | `ba_caba_servicio_tecnico` |
| `message` | Hello, good morning. How are you? I hope very well. I am contacting you to provide technical service for computers and technology products. We provide solutions for both individuals and shops and companies in the area. If you need repair, maintenance or equipment, you can contact us. I remain at your disposal for whatever you need. Kind regards |

### 10.2 Results

| Metric | Value |
|---------|-------|
| Execution Date | 2026-08-03 |
| Duration | 1:37:39 |
| Emails sent | 196 |
| Contacts reached | 9,800 (50 BCC $\times$ 196 emails) |
| Entries in campaign | 9,166 |
| Skipped (not found/duplicates) | 13 |
| Accounts used | 12 |
| Structure | TO=self, BCC=50 contacts |
| Logs | `log_ba_ciclo_20260803_135251.txt` |

### 10.3 Distribution by Account

| Account | Contacts |
|--------|----------------|
| fernando1141967@gmail.com | 850 contacts |
| adrianaavila131969@gmail.com | 850 contacts |
| wwwlanuscomputacion@gmail.com | 849 contacts |
| selvaggiesteban9@gmail.com | 828 contacts |
| selvaggiesteban4@gmail.com | 799 contacts |
| selvaggiesteban2@gmail.com | 799 contacts |
| selvaggiesteban11@gmail.com | 799 contacts |
| selvaggiconsultores@gmail.com | 799 contacts |
| marketing1a1oficial@gmail.com | 799 contacts |
| marketing1a1oficial@gmail.com | 798 contacts |
| estebanmfwd@gmail.com | 796 contacts |
| selvaggiesteban1@gmail.com | 200 contacts |

---

## 11. Data Sources — Work Directory CSVs

### 11.1 CSV Files

| File | Records | Description |
|---------|-----------|-------------|
| `WORK - CAMPAIGNS.csv` | 18 | Email marketing campaigns sent |
| `WORK - CHAT.csv` | 0 | Chat history (empty) |
| `WORK - GEOGRAPHIC COVERAGE.csv` | 12,045 | Geographic zones with coordinates |
| `WORK - TIME CONTROL.csv` | 153 | Hourly availability by service/date |
| `WORK - EMAILS.csv` | 17 | Email accounts (Gmail, Hostinger, Hotmail, iCloud) |
| `WORK - AI.csv` | 23 | OLLAMA/GROQ agent usage per week |
| `WORK - KEYWORDS.csv` | 1,747 | Search keyword list |
| `WORK - OBJECTIVES.csv` | 12 | 2026 monthly objectives |
| `WORK - WEB PAGES.csv` | 50 | Web pages with keywords and URLs |
| `WORK - SCRAP.csv` | 58 | Scraping results by zone |

### 11.2 Generated JSON

**File:** `Work/work_data.json` (3.5 MB)

**Script:** `scripts/csv_to_json.py`

**Usage:**
```bash
python scripts/csv_to_json.py
```

### 11.3 JSON Structure

```json
{
  "metadata": { ... },
  "campanas": [ ... ],
  "chat": [ ... ],
  "cobertura_geografica": [ ... ],
  "control_horario": [ ... ],
  "emails_cuentas": [ ... ],
  "agentes_ia": [ ... ],
  "keywords": [ ... ],
  "objetivos": [ ... ],
  "paginas_web": [ ... ],
  "scraping": [ ... ]
}
```

### 11.4 Field Mapping — CAMPAIGNS

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Title` | `titulo` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `List` | `lista` | string |
| `Subject` | `asunto` | string |
| `Date` | `fecha` | string |
| `Message` | `mensaje` | string |
| `Status` | `estado` | string |
| `Emails sent` | `emails_enviados` | int |
| `Unique contacts` | `contactos_unicos` | int |
| `Failures` | `fallos` | int |
| `Duration` | `duracion` | string |
| `Accounts used` | `cuentas_usadas` | int |
| `Enriched` | `enriched` | string |
| `Log file` | `log_file` | string |

### 11.5 Field Mapping — EMAILS

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Provider` | `proveedor` | string |
| `User` | `usuario` | string |
| `Password` | `contraseña` | string |
| `Application Password` | `contraseña_aplicacion` | string |
| `OAuth Client ID` | `oauth_client_id` | string |

### 11.6 Field Mapping — GEOGRAPHIC COVERAGE

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `order` | `order` | int |
| `id` | `id` | string |
| `desc` | `desc` | string |
| `north` | `north` | float |
| `west` | `west` | float |
| `south` | `south` | float |
| `east` | `east` | float |
| `cells` | `cells` | int |
| `queries` | `queries` | string |
| `density` | `density` | int |

### 11.7 Field Mapping — TIME CONTROL

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Price` | `precio` | int |
| `Service` | `servicio` | string |
| `Date` | `fecha` | string |
| `9:00` - `16:00` | `horas.9:00` - `horas.16:00` | bool |

### 11.8 Field Mapping — AI

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `AI_Agent` (part 1) | `agente` | string |
| `AI_Agent` (part 2) | `email` | string |
| `Week X` | `semanas.Week X` | bool |

### 11.9 Field Mapping — OBJECTIVES

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Month / Year` | `mes_anio` | string |
| `Working Days` | `dias_habiles` | int |
| `CPI` | `ipc` | string |
| `Price per Session` | `precio_sesion` | int |
| `Available Sessions` | `sesiones_disponibles` | int |
| `Sold Sessions (Target)` | `sesiones_vendidas_objetivo` | int |
| `Earnings` | `ganancias` | string |

### 11.10 Field Mapping — WEB PAGES

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Site` | `sitio` | string |
| `Keyword` | `keyword` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `Campaign` | `campana` | string |
| `URL_ES` | `url_es` | string |
| `URL_EN` | `url_en` | string |
| `Links sent` | `links_enviados` | string |
| `Sold Sessions (Target)` | `sesiones_vendidas_objetivo` | string |
| `Date / Time` | `fecha_hora` | string |

### 11.11 Field Mapping — SCRAPING

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Title` | `titulo` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `Keywords` | `keywords` | string |
| `Date` | `fecha` | string |
| `Status` | `estado` | string |
| `Rows` | `rows` | int |
| `Unique Emails` | `emails_unicos` | int |
| `Location` | `ubicacion` | string |
| `Duration` | `duracion` | string |
| `Log File` | `log_file` | string |

### 11.12 Notes

- Numbers with thousands separators (e.g., `10,800`) are converted to `10800`.
- Geographic coordinates are stored as float (e.g., `-347.100` $\rightarrow$ `-347.1`).
- The CSV `WORK - CHAT.csv` is empty (headers only).
- The script `csv_to_json.py` handles UTF-8 and cp1252 encoding.

---

## 12. Deduplication

### 12.1 Deduplication Key

**Primary:** `main.title` + `main.city` (both normalized, lowercase, no extra spaces).

### 12.2 Handling Duplicates

Print to console:
```
DUPLICATE FOUND:
  Existing: ROWID=X | title="..." | city="..." | email="..."
  New:     title="..." | city="..." | email="..."
  Options: [S]kip / [U]pdate / [M]erge
```

Pause and wait for user input.

- **Skip**: ignore the new one, keep existing.
- **Update**: overwrite empty fields of existing with new values.
- **Merge**: combine fields (do not overwrite existing data).

---

## 13. Implementation Notes

- Enrichment scripts must import these rules as a reference.
- Regex and blacklist lists must be maintained in a single place (this file or a Python module).
- Any rule change is documented here with a date.

---

## 14. Data Enrichment — Results (2026-07-20)

### 14.1 Data Sources — Import Status

| Source | Files | Unique Emails | Imported | Status |
|--------|----------|---------------|------------|--------|
| Brevo CSV (base_tvmas.csv) | 1 | 9,310 | 9,310 | ✅ 99.96% coverage |
| Brevo CSV (brevo_10042026.csv) | 1 | 12,763 | ~12,763 | ✅ Derived from base_tvmas |
| Brevo CSV (brevo_consolidada_total.csv) | 1 | 12,763 | ~12,763 | ✅ Derived from base_tvmas |
| Gosom General | 1 | 5,347 | 5,347 | ✅ import_gosom_general.py |
| Gosom RRHH | 1 | 5,434 | 5,434 | ✅ import_rrhh_gosom.py |
| Gosom Root (44 CSVs) | 44 | ~4,500 | 303 | ✅ import_gosom_root.py |
| WhatsApp VCFs | 13 | 92 | 92 | ✅ import_vcf.py (phone-only) |
| XLSX Trade Fairs (62 files) | 62 | ~34,000 | 0 | ✅ Already in DB (duplicates) |
| Blacklist (REJECTED CONTACTS) | 1 | 198 | 198 | ✅ Marked BLACKLISTED |
| Google Contacts (7 CSVs) | 7 | ~6,600 | 0 | ✅ Already in DB (duplicates) |
| Pre-existing (date_added=NULL) | — | 99,261 | 99,261 | ✅ Brevo legacy import |

### 14.2 Verified Sources (Gap Closed)

| Source | Files | Unique Emails | Result |
|--------|----------|---------------|-----------|
| Gosom webdata/ (36 UUID CSVs) | 36 | 792 | ✅ Already in DB (import_gosom_root.py) |
| Gosom web_marketing_caba.csv | 1 | 231 | ✅ Already in DB (import_gosom_root.py) |
| contacts Mailrelay | 1 | 71 | ✅ Already in DB (import_mailrelay.py created) |
| contacts selvaggiesteban (phone-only) | 1 | 2,643 | ✅ import_phone_contacts.py (dedup 15K $\rightarrow$ 2.6K) |
| LinkedIn people/authors CSVs | 2 | 118 | ✅ import_linkedin_profiles.py (no email/tel) |
| YOLANDA.csv | 1 | ~500 | ⏳ Non-standard format (pending) |

### 14.3 DB Current State

| Metric | Value |
|---------|-------|
| Total contacts | 123,763 |
| With valid email | 116,747 |
| With phones | 59,739 |
| With LinkedIn | 114 |
| Phone-only (no email) | 5,738 |
| With social networks | 0 (8 columns 100% NULL) |
| With sector | ~92,000 |
| With website | ~121,000 |
| BLACKLISTED | 198 |
| Pre-existing (no date) | 99,261 |
| Imported by scripts | ~24,500 |

### 14.4 Import Scripts and Utilities Created

| Script | Source | Status |
|--------|--------|--------|
| `config.py` | Centralized configuration | ✅ Active |
| `utils.py` | Shared utilities | ✅ Active |
| `verify_imported.py` | Source verification | ✅ Executed |
| `import_vcf.py` | WhatsApp VCFs | ✅ Completed (92 contacts) |
| `import_gosom_root.py` | Gosom root CSVs | ✅ Completed (303 contacts) |
| `import_gosom_general.py` | Gosom General CSV | ✅ Completed (5,347 contacts) |
| `import_rrhh_gosom.py` | Gosom RRHH CSV | ✅ Completed (5,434 contacts) |
| `import_xlsx.py` | XLSX trade fairs | ✅ Executed (0 new, all duplicates) |
| `import_blacklist.py` | REJECTED CONTACTS.docx | ✅ Completed (198 blacklisted) |
| `import_google_contacts.py` | Google Contacts CSVs | ✅ Executed (0 new, 2 tel updated) |
| `import_gosom_webdata.py` | Gosom webdata/ + web_marketing_caba | ✅ Executed (0 new, all already in DB) |
| `import_mailrelay.py` | Mailrelay CSV | ✅ Executed (0 new, all already in DB) |
| `import_phone_contacts.py` | contacts selvaggiesteban (phone-only) | ✅ 2,643 contacts imported |
| `import_linkedin_profiles.py` | LinkedIn people/authors CSVs | ✅ 118 profiles imported |
| `cleanup_duplicate_emails.py` | Duplicate email dedup | ✅ Active |
| `remove_duplicates.py` | CSV dedup | ✅ Active |
| `remove_duplicates_xlsx.py` | XLSX dedup | ✅ Active |
| `enrich_abogados.py` | Lawyer enrichment via web scraping | ✅ Active |
| `enumerate_prefixes.py` | Email prefix analysis | ✅ Active |
| `archive/cleanup_phase3.py` | Archived cleanup (encoding) | 📦 Archived |
| `archive/cleanup_phase4.py` | Archived cleanup (junk emails) | 📦 Archived |
| `archive/cleanup_phase7.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase8.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase9.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase10.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase11.py` | Archived cleanup | 📦 Archived |
| `archive/migrate_v4.py` | Archived DB v4 migration | 📦 Archived |

---

## 15. Schema Update — campaign.email_used

### 15.1 New Column

```sql
ALTER TABLE campaign ADD COLUMN email_used TEXT;
```

Records the exact email of the recipient to whom each campaign was sent. Allows a contact with multiple emails to receive multiple campaigns (one per email).

### 15.2 Usage

- When sending a campaign: `campaign.email_used = recipient_email`
- When querying campaigns: filter by `email_used` to know which email was used
- Backward compatibility: existing rows remain with `email_used = NULL`

---

## 16. Schema Update — campaign.message

### 16.1 New Column

```sql
ALTER TABLE campaign ADD COLUMN message TEXT;
```

Records the body of the message sent in each campaign. Allows querying the exact content received by each contact.

### 16.2 Usage

- When sending a campaign: `campaign.message = message_body`
- When querying campaigns: filter by `message` to know what content was sent
- Backward compatibility: existing rows remain with `message = NULL`

---

## 17. Enrichment Campaign LANÚS-03082026

### 17.1 Campaign Data

| Field | Value |
|-------|-------|
| `list_val` | `LANÚS-03082026` |
| `subject` | Computer Technical Service and Technology Products |
| `type` | `lanus_servicio_tecnico` |
| `message` | Hello, good morning. How are you? I hope very well. I am contacting you to provide technical service for computers and technology products. We provide solutions for both individuals and shops and companies in the area. If you need repair, maintenance or equipment, you can contact us. I remain at your disposal for whatever you need. Kind regards |

### 17.2 Results

| Metric | Value |
|---------|-------|
| Execution Date | 2026-08-03 |
| Contacts inserted | 228 |
| Accounts used | 12 (19 emails each) |
| Logs parsed | `log_lanus_cycle_20260803_112153.txt` (12) + `log_lanus_cycle_20260803_112606.txt` (216) |
| Script | `scripts/database_manager/enrich_lanus_campaign.py` |
| Backup | `data/inputs/contacts_backup_before_lanus_enrich.db` |

### 17.3 Accounts and Distribution

| Account | Emails sent |
|--------|----------------|
| wwwlanuscomputacion@gmail.com | 19 |
| adrianaavila131969@gmail.com | 19 |
| fernando1141967@gmail.com | 19 |
| selvaggiesteban9@gmail.com | 19 |
| selvaggiesteban4@gmail.com | 19 |
| selvaggiesteban11@gmail.com | 19 |
| marketing1a1oficial@gmail.com | 19 |
| selvaggiconsultores@gmail.com | 19 |
| estebanmfwd@gmail.com | 19 |
| selvaggiesteban1@gmail.com | 19 |
| selvaggiesteban2@gmail.com | 19 |
| marcelagomez7799@gmail.com | 19 |

---

## 18. Enrichment Campaign BA/CABA-03082026

### 18.1 Campaign Data

| Field | Value |
|-------|-------|
| `list_val` | `BA-CABA-03082026` |
| `subject` | Computer Technical Service and Technology Products |
| `type` | `ba_caba_servicio_tecnico` |
| `message` | Hello, good morning. How are you? I hope very well. I am contacting you to provide technical service for computers and technology products. We provide solutions for both individuals and shops and companies in the area. If you need repair, maintenance or equipment, you can contact us. I remain at your disposal for whatever you need. Kind regards |

### 18.2 Results

| Metric | Value |
|---------|-------|
| Execution Date | 2026-08-03 |
| Duration | 1:37:39 |
| Emails sent | 196 |
| Contacts reached | 9,800 (50 BCC $\times$ 196 emails) |
| Entries in campaign | 9,166 |
| Skipped (not found/duplicates) | 13 |
| Accounts used | 12 |
| Structure | TO=self, BCC=50 contacts |
| Logs | `log_ba_ciclo_20260803_135251.txt` |

### 18.3 Distribution by Account

| Account | Contacts |
|--------|----------------|
| fernando1141967@gmail.com | 850 contacts |
| adrianaavila131969@gmail.com | 850 contacts |
| wwwlanuscomputacion@gmail.com | 849 contacts |
| selvaggiesteban9@gmail.com | 828 contacts |
| selvaggiesteban4@gmail.com | 799 contacts |
| selvaggiesteban2@gmail.com | 799 contacts |
| selvaggiesteban11@gmail.com | 799 contacts |
| selvaggiconsultores@gmail.com | 799 contacts |
| marketing1a1oficial@gmail.com | 799 contacts |
| marketing1a1oficial@gmail.com | 798 contacts |
| estebanmfwd@gmail.com | 796 contacts |
| selvaggiesteban1@gmail.com | 200 contacts |

---

## 19. Data Sources — Work Directory CSVs

### 19.1 CSV Files

| File | Records | Description |
|---------|-----------|-------------|
| `WORK - CAMPAIGNS.csv` | 18 | Email marketing campaigns sent |
| `WORK - CHAT.csv` | 0 | Chat history (empty) |
| `WORK - GEOGRAPHIC COVERAGE.csv` | 12,045 | Geographic zones with coordinates |
| `WORK - TIME CONTROL.csv` | 153 | Hourly availability by service/date |
| `WORK - EMAILS.csv` | 17 | Email accounts (Gmail, Hostinger, Hotmail, iCloud) |
| `WORK - AI.csv` | 23 | OLLAMA/GROQ agent usage per week |
| `WORK - KEYWORDS.csv` | 1,747 | Search keyword list |
| `WORK - OBJECTIVES.csv` | 12 | 2026 monthly objectives |
| `WORK - WEB PAGES.csv` | 50 | Web pages with keywords and URLs |
| `WORK - SCRAP.csv` | 58 | Scraping results by zone |

### 19.2 Generated JSON

**File:** `Work/work_data.json` (3.5 MB)

**Script:** `scripts/csv_to_json.py`

**Usage:**
```bash
python scripts/csv_to_json.py
```

### 19.3 JSON Structure

```json
{
  "metadata": { ... },
  "campanas": [ ... ],
  "chat": [ ... ],
  "cobertura_geografica": [ ... ],
  "control_horario": [ ... ],
  "emails_cuentas": [ ... ],
  "agentes_ia": [ ... ],
  "keywords": [ ... ],
  "objetivos": [ ... ],
  "paginas_web": [ ... ],
  "scraping": [ ... ]
}
```

### 19.4 Field Mapping — CAMPAIGNS

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Title` | `titulo` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `List` | `lista` | string |
| `Subject` | `asunto` | string |
| `Date` | `fecha` | string |
| `Message` | `mensaje` | string |
| `Status` | `estado` | string |
| `Emails sent` | `emails_enviados` | int |
| `Unique contacts` | `contactos_unicos` | int |
| `Failures` | `fallos` | int |
| `Duration` | `duracion` | string |
| `Accounts used` | `cuentas_usadas` | int |
| `Enriched` | `enriched` | string |
| `Log file` | `log_file` | string |

### 19.5 Field Mapping — EMAILS

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Provider` | `proveedor` | string |
| `User` | `usuario` | string |
| `Password` | `contraseña` | string |
| `Application Password` | `contraseña_aplicacion` | string |
| `OAuth Client ID` | `oauth_client_id` | string |

### 19.6 Field Mapping — GEOGRAPHIC COVERAGE

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `order` | `order` | int |
| `id` | `id` | string |
| `desc` | `desc` | string |
| `north` | `north` | float |
| `west` | `west` | float |
| `south` | `south` | float |
| `east` | `east` | float |
| `cells` | `cells` | int |
| `queries` | `queries` | string |
| `density` | `density` | int |

### 19.7 Field Mapping — TIME CONTROL

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Price` | `precio` | int |
| `Service` | `servicio` | string |
| `Date` | `fecha` | string |
| `9:00` - `16:00` | `horas.9:00` - `horas.16:00` | bool |

### 19.8 Field Mapping — AI

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `AI_Agent` (part 1) | `agente` | string |
| `AI_Agent` (part 2) | `email` | string |
| `Week X` | `semanas.Week X` | bool |

### 19.9 Field Mapping — OBJECTIVES

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Month / Year` | `mes_anio` | string |
| `Working Days` | `dias_habiles` | int |
| `CPI` | `ipc` | string |
| `Price per Session` | `precio_sesion` | int |
| `Available Sessions` | `sesiones_disponibles` | int |
| `Sold Sessions (Target)` | `sesiones_vendidas_objetivo` | int |
| `Earnings` | `ganancias` | string |

### 19.10 Field Mapping — WEB PAGES

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Site` | `sitio` | string |
| `Keyword` | `keyword` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `Campaign` | `campana` | string |
| `URL_ES` | `url_es` | string |
| `URL_EN` | `url_en` | string |
| `Links sent` | `links_enviados` | string |
| `Sold Sessions (Target)` | `sesiones_vendidas_objetivo` | string |
| `Date / Time` | `fecha_hora` | string |

### 19.11 Field Mapping — SCRAPING

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Title` | `titulo` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `Keywords` | `keywords` | string |
| `Date` | `fecha` | string |
| `Status` | `estado` | string |
| `Rows` | `rows` | int |
| `Unique Emails` | `emails_unicos` | int |
| `Location` | `ubicacion` | string |
| `Duration` | `duracion` | string |
| `Log File` | `log_file` | string |

### 19.12 Notes

- Numbers with thousands separators (e.g., `10,800`) are converted to `10800`.
- Geographic coordinates are stored as float (e.g., `-347.100` $\rightarrow$ `-347.1`).
- The CSV `WORK - CHAT.csv` is empty (headers only).
- The script `csv_to_json.py` handles UTF-8 and cp1252 encoding.

---

## 20. Deduplication

### 20.1 Deduplication Key

**Primary:** `main.title` + `main.city` (both normalized, lowercase, no extra spaces).

### 20.2 Handling Duplicates

Print to console:
```
DUPLICATE FOUND:
  Existing: ROWID=X | title="..." | city="..." | email="..."
  New:     title="..." | city="..." | email="..."
  Options: [S]kip / [U]pdate / [M]erge
```

Pause and wait for user input.

- **Skip**: ignore the new one, keep existing.
- **Update**: overwrite empty fields of existing with new values.
- **Merge**: combine fields (do not overwrite existing data).

---

## 21. Implementation Notes

- Enrichment scripts must import these rules as a reference.
- Regex and blacklist lists must be maintained in a single place (this file or a Python module).
- Any rule change is documented here with a date.

---

## 22. Data Enrichment — Results (2026-07-20)

### 22.1 Data Sources — Import Status

| Source | Files | Unique Emails | Imported | Status |
|--------|----------|---------------|------------|--------|
| Brevo CSV (base_tvmas.csv) | 1 | 9,310 | 9,310 | ✅ 99.96% coverage |
| Brevo CSV (brevo_10042026.csv) | 1 | 12,763 | ~12,763 | ✅ Derived from base_tvmas |
| Brevo CSV (brevo_consolidada_total.csv) | 1 | 12,763 | ~12,763 | ✅ Derived from base_tvmas |
| Gosom General | 1 | 5,347 | 5,347 | ✅ import_gosom_general.py |
| Gosom RRHH | 1 | 5,434 | 5,434 | ✅ import_rrhh_gosom.py |
| Gosom Root (44 CSVs) | 44 | ~4,500 | 303 | ✅ import_gosom_root.py |
| WhatsApp VCFs | 13 | 92 | 92 | ✅ import_vcf.py (phone-only) |
| XLSX Trade Fairs (62 files) | 62 | ~34,000 | 0 | ✅ Already in DB (duplicates) |
| Blacklist (REJECTED CONTACTS) | 1 | 198 | 198 | ✅ Marked BLACKLISTED |
| Google Contacts (7 CSVs) | 7 | ~6,600 | 0 | ✅ Already in DB (duplicates) |
| Pre-existing (date_added=NULL) | — | 99,261 | 99,261 | ✅ Brevo legacy import |

### 22.2 Verified Sources (Gap Closed)

| Source | Files | Unique Emails | Result |
|--------|----------|---------------|-----------|
| Gosom webdata/ (36 UUID CSVs) | 36 | 792 | ✅ Already in DB (import_gosom_root.py) |
| Gosom web_marketing_caba.csv | 1 | 231 | ✅ Already in DB (import_gosom_root.py) |
| contacts Mailrelay | 1 | 71 | ✅ Already in DB (import_mailrelay.py created) |
| contacts selvaggiesteban (phone-only) | 1 | 2,643 | ✅ import_phone_contacts.py (dedup 15K $\rightarrow$ 2.6K) |
| LinkedIn people/authors CSVs | 2 | 118 | ✅ import_linkedin_profiles.py (no email/tel) |
| YOLANDA.csv | 1 | ~500 | ⏳ Non-standard format (pending) |

### 22.3 DB Current State

| Metric | Value |
|---------|-------|
| Total contacts | 123,763 |
| With valid email | 116,747 |
| With phones | 59,739 |
| With LinkedIn | 114 |
| Phone-only (no email) | 5,738 |
| With social networks | 0 (8 columns 100% NULL) |
| With sector | ~92,000 |
| With website | ~121,000 |
| BLACKLISTED | 198 |
| Pre-existing (no date) | 99,261 |
| Imported by scripts | ~24,500 |

### 22.4 Import Scripts and Utilities Created

| Script | Source | Status |
|--------|--------|--------|
| `config.py` | Centralized configuration | ✅ Active |
| `utils.py` | Shared utilities | ✅ Active |
| `verify_imported.py` | Source verification | ✅ Executed |
| `import_vcf.py` | WhatsApp VCFs | ✅ Completed (92 contacts) |
| `import_gosom_root.py` | Gosom root CSVs | ✅ Completed (303 contacts) |
| `import_gosom_general.py` | Gosom General CSV | ✅ Completed (5,347 contacts) |
| `import_rrhh_gosom.py` | Gosom RRHH CSV | ✅ Completed (5,434 contacts) |
| `import_xlsx.py` | XLSX trade fairs | ✅ Executed (0 new, all duplicates) |
| `import_blacklist.py` | REJECTED CONTACTS.docx | ✅ Completed (198 blacklisted) |
| `import_google_contacts.py` | Google Contacts CSVs | ✅ Executed (0 new, 2 tel updated) |
| `import_gosom_webdata.py` | Gosom webdata/ + web_marketing_caba | ✅ Executed (0 new, all already in DB) |
| `import_mailrelay.py` | Mailrelay CSV | ✅ Executed (0 new, all already in DB) |
| `import_phone_contacts.py` | contacts selvaggiesteban (phone-only) | ✅ 2,643 contacts imported |
| `import_linkedin_profiles.py` | LinkedIn people/authors CSVs | ✅ 118 profiles imported |
| `cleanup_duplicate_emails.py` | Duplicate email dedup | ✅ Active |
| `remove_duplicates.py` | CSV dedup | ✅ Active |
| `remove_duplicates_xlsx.py` | XLSX dedup | ✅ Active |
| `enrich_abogados.py` | Lawyer enrichment via web scraping | ✅ Active |
| `enumerate_prefixes.py` | Email prefix analysis | ✅ Active |
| `archive/cleanup_phase3.py` | Archived cleanup (encoding) | 📦 Archived |
| `archive/cleanup_phase4.py` | Archived cleanup (junk emails) | 📦 Archived |
| `archive/cleanup_phase7.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase8.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase9.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase10.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase11.py` | Archived cleanup | 📦 Archived |
| `archive/migrate_v4.py` | Archived DB v4 migration | 📦 Archived |

---

## 15. Schema Update — campaign.email_used

### 15.1 New Column

```sql
ALTER TABLE campaign ADD COLUMN email_used TEXT;
```

Records the exact email of the recipient to whom each campaign was sent. Allows a contact with multiple emails to receive multiple campaigns (one per email).

### 15.2 Usage

- When sending a campaign: `campaign.email_used = recipient_email`
- When querying campaigns: filter by `email_used` to know which email was used
- Backward compatibility: existing rows remain with `email_used = NULL`

---

## 16. Schema Update — campaign.message

### 16.1 New Column

```sql
ALTER TABLE campaign ADD COLUMN message TEXT;
```

Records the body of the message sent in each campaign. Allows querying the exact content received by each contact.

### 16.2 Usage

- When sending a campaign: `campaign.message = message_body`
- When querying campaigns: filter by `message` to know what content was sent
- Backward compatibility: existing rows remain with `message = NULL`

---

## 17. Enrichment Campaign LANÚS-03082026

### 17.1 Campaign Data

| Field | Value |
|-------|-------|
| `list_val` | `LANÚS-03082026` |
| `subject` | Computer Technical Service and Technology Products |
| `type` | `lanus_servicio_tecnico` |
| `message` | Hello, good morning. How are you? I hope very well. I am contacting you to provide technical service for computers and technology products. We provide solutions for both individuals and shops and companies in the area. If you need repair, maintenance or equipment, you can contact us. I remain at your disposal for whatever you need. Kind regards |

### 17.2 Results

| Metric | Value |
|---------|-------|
| Execution Date | 2026-08-03 |
| Contacts inserted | 228 |
| Accounts used | 12 (19 emails each) |
| Logs parsed | `log_lanus_cycle_20260803_112153.txt` (12) + `log_lanus_cycle_20260803_112606.txt` (216) |
| Script | `scripts/database_manager/enrich_lanus_campaign.py` |
| Backup | `data/inputs/contacts_backup_before_lanus_enrich.db` |

### 17.3 Accounts and Distribution

| Account | Emails sent |
|--------|----------------|
| wwwlanuscomputacion@gmail.com | 19 |
| adrianaavila131969@gmail.com | 19 |
| fernando1141967@gmail.com | 19 |
| selvaggiesteban9@gmail.com | 19 |
| selvaggiesteban4@gmail.com | 19 |
| selvaggiesteban11@gmail.com | 19 |
| marketing1a1oficial@gmail.com | 19 |
| selvaggiconsultores@gmail.com | 19 |
| estebanmfwd@gmail.com | 19 |
| selvaggiesteban1@gmail.com | 19 |
| selvaggiesteban2@gmail.com | 19 |
| marcelagomez7799@gmail.com | 19 |

---

## 18. Enrichment Campaign BA/CABA-03082026

### 18.1 Campaign Data

| Field | Value |
|-------|-------|
| `list_val` | `BA-CABA-03082026` |
| `subject` | Computer Technical Service and Technology Products |
| `type` | `ba_caba_servicio_tecnico` |
| `message` | Hello, good morning. How are you? I hope very well. I am contacting you to provide technical service for computers and technology products. We provide solutions for both individuals and shops and companies in the area. If you need repair, maintenance or equipment, you can contact us. I remain at your disposal for whatever you need. Kind regards |

### 18.2 Results

| Metric | Value |
|---------|-------|
| Execution Date | 2026-08-03 |
| Duration | 1:37:39 |
| Emails sent | 196 |
| Contacts reached | 9,800 (50 BCC $\times$ 196 emails) |
| Entries in campaign | 9,166 |
| Skipped (not found/duplicates) | 13 |
| Accounts used | 12 |
| Structure | TO=self, BCC=50 contacts |
| Logs | `log_ba_ciclo_20260803_135251.txt` |

### 18.3 Distribution by Account

| Account | Contacts |
|--------|----------------|
| fernando1141967@gmail.com | 850 contacts |
| adrianaavila131969@gmail.com | 850 contacts |
| wwwlanuscomputacion@gmail.com | 849 contacts |
| selvaggiesteban9@gmail.com | 828 contacts |
| selvaggiesteban4@gmail.com | 799 contacts |
| selvaggiesteban2@gmail.com | 799 contacts |
| selvaggiesteban11@gmail.com | 799 contacts |
| selvaggiconsultores@gmail.com | 799 contacts |
| marketing1a1oficial@gmail.com | 799 contacts |
| marketing1a1oficial@gmail.com | 798 contacts |
| estebanmfwd@gmail.com | 796 contacts |
| selvaggiesteban1@gmail.com | 200 contacts |

---

## 19. Data Sources — Work Directory CSVs

### 19.1 CSV Files

| File | Records | Description |
|---------|-----------|-------------|
| `WORK - CAMPAIGNS.csv` | 18 | Email marketing campaigns sent |
| `WORK - CHAT.csv` | 0 | Chat history (empty) |
| `WORK - GEOGRAPHIC COVERAGE.csv` | 12,045 | Geographic zones with coordinates |
| `WORK - TIME CONTROL.csv` | 153 | Hourly availability by service/date |
| `WORK - EMAILS.csv` | 17 | Email accounts (Gmail, Hostinger, Hotmail, iCloud) |
| `WORK - AI.csv` | 23 | OLLAMA/GROQ agent usage per week |
| `WORK - KEYWORDS.csv` | 1,747 | Search keyword list |
| `WORK - OBJECTIVES.csv` | 12 | 2026 monthly objectives |
| `WORK - WEB PAGES.csv` | 50 | Web pages with keywords and URLs |
| `WORK - SCRAP.csv` | 58 | Scraping results by zone |

### 19.2 Generated JSON

**File:** `Work/work_data.json` (3.5 MB)

**Script:** `scripts/csv_to_json.py`

**Usage:**
```bash
python scripts/csv_to_json.py
```

### 19.3 JSON Structure

```json
{
  "metadata": { ... },
  "campanas": [ ... ],
  "chat": [ ... ],
  "cobertura_geografica": [ ... ],
  "control_horario": [ ... ],
  "emails_cuentas": [ ... ],
  "agentes_ia": [ ... ],
  "keywords": [ ... ],
  "objetivos": [ ... ],
  "paginas_web": [ ... ],
  "scraping": [ ... ]
}
```

### 19.4 Field Mapping — CAMPAIGNS

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Title` | `titulo` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `List` | `lista` | string |
| `Subject` | `asunto` | string |
| `Date` | `fecha` | string |
| `Message` | `mensaje` | string |
| `Status` | `estado` | string |
| `Emails sent` | `emails_enviados` | int |
| `Unique contacts` | `contactos_unicos` | int |
| `Failures` | `fallos` | int |
| `Duration` | `duracion` | string |
| `Accounts used` | `cuentas_usadas` | int |
| `Enriched` | `enriched` | string |
| `Log file` | `log_file` | string |

### 19.5 Field Mapping — EMAILS

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Provider` | `proveedor` | string |
| `User` | `usuario` | string |
| `Password` | `contraseña` | string |
| `Application Password` | `contraseña_aplicacion` | string |
| `OAuth Client ID` | `oauth_client_id` | string |

### 19.6 Field Mapping — GEOGRAPHIC COVERAGE

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `order` | `order` | int |
| `id` | `id` | string |
| `desc` | `desc` | string |
| `north` | `north` | float |
| `west` | `west` | float |
| `south` | `south` | float |
| `east` | `east` | float |
| `cells` | `cells` | int |
| `queries` | `queries` | string |
| `density` | `density` | int |

### 19.7 Field Mapping — TIME CONTROL

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Price` | `precio` | int |
| `Service` | `servicio` | string |
| `Date` | `fecha` | string |
| `9:00` - `16:00` | `horas.9:00` - `horas.16:00` | bool |

### 19.8 Field Mapping — AI

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `AI_Agent` (part 1) | `agente` | string |
| `AI_Agent` (part 2) | `email` | string |
| `Week X` | `semanas.Week X` | bool |

### 19.9 Field Mapping — OBJECTIVES

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Month / Year` | `mes_anio` | string |
| `Working Days` | `dias_habiles` | int |
| `CPI` | `ipc` | string |
| `Price per Session` | `precio_sesion` | int |
| `Available Sessions` | `sesiones_disponibles` | int |
| `Sold Sessions (Target)` | `sesiones_vendidas_objetivo` | int |
| `Earnings` | `ganancias` | string |

### 19.10 Field Mapping — WEB PAGES

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Site` | `sitio` | string |
| `Keyword` | `keyword` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `Campaign` | `campana` | string |
| `URL_ES` | `url_es` | string |
| `URL_EN` | `url_en` | string |
| `Links sent` | `links_enviados` | string |
| `Sold Sessions (Target)` | `sesiones_vendidas_objetivo` | string |
| `Date / Time` | `fecha_hora` | string |

### 19.11 Field Mapping — SCRAPING

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Title` | `titulo` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `Keywords` | `keywords` | string |
| `Date` | `fecha` | string |
| `Status` | `estado` | string |
| `Rows` | `rows` | int |
| `Unique Emails` | `emails_unicos` | int |
| `Location` | `ubicacion` | string |
| `Duration` | `duracion` | string |
| `Log File` | `log_file` | string |

### 19.12 Notes

- Numbers with thousands separators (e.g., `10,800`) are converted to `10800`.
- Geographic coordinates are stored as float (e.g., `-347.100` $\rightarrow$ `-347.1`).
- The CSV `WORK - CHAT.csv` is empty (headers only).
- The script `csv_to_json.py` handles UTF-8 and cp1252 encoding.

---

## 20. Deduplication

### 20.1 Deduplication Key

**Primary:** `main.title` + `main.city` (both normalized, lowercase, no extra spaces).

### 20.2 Handling Duplicates

Print to console:
```
DUPLICATE FOUND:
  Existing: ROWID=X | title="..." | city="..." | email="..."
  New:     title="..." | city="..." | email="..."
  Options: [S]kip / [U]pdate / [M]erge
```

Pause and wait for user input.

- **Skip**: ignore the new one, keep existing.
- **Update**: overwrite empty fields of existing with new values.
- **Merge**: combine fields (do not overwrite existing data).

---

## 21. Implementation Notes

- Enrichment scripts must import these rules as a reference.
- Regex and blacklist lists must be maintained in a single place (this file or a Python module).
- Any rule change is documented here with a date.

---

## 22. Data Enrichment — Results (2026-07-20)

### 22.1 Data Sources — Import Status

| Source | Files | Unique Emails | Imported | Status |
|--------|----------|---------------|------------|--------|
| Brevo CSV (base_tvmas.csv) | 1 | 9,310 | 9,310 | ✅ 99.96% coverage |
| Brevo CSV (brevo_10042026.csv) | 1 | 12,763 | ~12,763 | ✅ Derived from base_tvmas |
| Brevo CSV (brevo_consolidada_total.csv) | 1 | 12,763 | ~12,763 | ✅ Derived from base_tvmas |
| Gosom General | 1 | 5,347 | 5,347 | ✅ import_gosom_general.py |
| Gosom RRHH | 1 | 5,434 | 5,434 | ✅ import_rrhh_gosom.py |
| Gosom Root (44 CSVs) | 44 | ~4,500 | 303 | ✅ import_gosom_root.py |
| WhatsApp VCFs | 13 | 92 | 92 | ✅ import_vcf.py (phone-only) |
| XLSX Trade Fairs (62 files) | 62 | ~34,000 | 0 | ✅ Already in DB (duplicates) |
| Blacklist (REJECTED CONTACTS) | 1 | 198 | 198 | ✅ Marked BLACKLISTED |
| Google Contacts (7 CSVs) | 7 | ~6,600 | 0 | ✅ Already in DB (duplicates) |
| Pre-existing (date_added=NULL) | — | 99,261 | 99,261 | ✅ Brevo legacy import |

### 22.2 Verified Sources (Gap Closed)

| Source | Files | Unique Emails | Result |
|--------|----------|---------------|-----------|
| Gosom webdata/ (36 UUID CSVs) | 36 | 792 | ✅ Already in DB (import_gosom_root.py) |
| Gosom web_marketing_caba.csv | 1 | 231 | ✅ Already in DB (import_gosom_root.py) |
| contacts Mailrelay | 1 | 71 | ✅ Already in DB (import_mailrelay.py created) |
| contacts selvaggiesteban (phone-only) | 1 | 2,643 | ✅ import_phone_contacts.py (dedup 15K $\rightarrow$ 2.6K) |
| LinkedIn people/authors CSVs | 2 | 118 | ✅ import_linkedin_profiles.py (no email/tel) |
| YOLANDA.csv | 1 | ~500 | ⏳ Non-standard format (pending) |

### 22.3 DB Current State

| Metric | Value |
|---------|-------|
| Total contacts | 123,763 |
| With valid email | 116,747 |
| With phones | 59,739 |
| With LinkedIn | 114 |
| Phone-only (no email) | 5,738 |
| With social networks | 0 (8 columns 100% NULL) |
| With sector | ~92,000 |
| With website | ~121,000 |
| BLACKLISTED | 198 |
| Pre-existing (no date) | 99,261 |
| Imported by scripts | ~24,500 |

### 22.4 Import Scripts and Utilities Created

| Script | Source | Status |
|--------|--------|--------|
| `config.py` | Centralized configuration | ✅ Active |
| `utils.py` | Shared utilities | ✅ Active |
| `verify_imported.py` | Source verification | ✅ Executed |
| `import_vcf.py` | WhatsApp VCFs | ✅ Completed (92 contacts) |
| `import_gosom_root.py` | Gosom root CSVs | ✅ Completed (303 contacts) |
| `import_gosom_general.py` | Gosom General CSV | ✅ Completed (5,347 contacts) |
| `import_rrhh_gosom.py` | Gosom RRHH CSV | ✅ Completed (5,434 contacts) |
| `import_xlsx.py` | XLSX trade fairs | ✅ Executed (0 new, all duplicates) |
| `import_blacklist.py` | REJECTED CONTACTS.docx | ✅ Completed (198 blacklisted) |
| `import_google_contacts.py` | Google Contacts CSVs | ✅ Executed (0 new, 2 tel updated) |
| `import_gosom_webdata.py` | Gosom webdata/ + web_marketing_caba | ✅ Executed (0 new, all already in DB) |
| `import_mailrelay.py` | Mailrelay CSV | ✅ Executed (0 new, all already in DB) |
| `import_phone_contacts.py` | contacts selvaggiesteban (phone-only) | ✅ 2,643 contacts imported |
| `import_linkedin_profiles.py` | LinkedIn people/authors CSVs | ✅ 118 profiles imported |
| `cleanup_duplicate_emails.py` | Duplicate email dedup | ✅ Active |
| `remove_duplicates.py` | CSV dedup | ✅ Active |
| `remove_duplicates_xlsx.py` | XLSX dedup | ✅ Active |
| `enrich_abogados.py` | Lawyer enrichment via web scraping | ✅ Active |
| `enumerate_prefixes.py` | Email prefix analysis | ✅ Active |
| `archive/cleanup_phase3.py` | Archived cleanup (encoding) | 📦 Archived |
| `archive/cleanup_phase4.py` | Archived cleanup (junk emails) | 📦 Archived |
| `archive/cleanup_phase7.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase8.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase9.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase10.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase11.py` | Archived cleanup | 📦 Archived |
| `archive/migrate_v4.py` | Archived DB v4 migration | 📦 Archived |

---

## 15. Schema Update — campaign.email_used

### 15.1 New Column

```sql
ALTER TABLE campaign ADD COLUMN email_used TEXT;
```

Records the exact email of the recipient to whom each campaign was sent. Allows a contact with multiple emails to receive multiple campaigns (one per email).

### 15.2 Usage

- When sending a campaign: `campaign.email_used = recipient_email`
- When querying campaigns: filter by `email_used` to know which email was used
- Backward compatibility: existing rows remain with `email_used = NULL`

---

## 16. Schema Update — campaign.message

### 16.1 New Column

```sql
ALTER TABLE campaign ADD COLUMN message TEXT;
```

Records the body of the message sent in each campaign. Allows querying the exact content received by each contact.

### 16.2 Usage

- When sending a campaign: `campaign.message = message_body`
- When querying campaigns: filter by `message` to know what content was sent
- Backward compatibility: existing rows remain with `message = NULL`

---

## 17. Enrichment Campaign LANÚS-03082026

### 17.1 Campaign Data

| Field | Value |
|-------|-------|
| `list_val` | `LANÚS-03082026` |
| `subject` | Computer Technical Service and Technology Products |
| `type` | `lanus_servicio_tecnico` |
| `message` | Hello, good morning. How are you? I hope very well. I am contacting you to provide technical service for computers and technology products. We provide solutions for both individuals and shops and companies in the area. If you need repair, maintenance or equipment, you can contact us. I remain at your disposal for whatever you need. Kind regards |

### 17.2 Results

| Metric | Value |
|---------|-------|
| Execution Date | 2026-08-03 |
| Contacts inserted | 228 |
| Accounts used | 12 (19 emails each) |
| Logs parsed | `log_lanus_cycle_20260803_112153.txt` (12) + `log_lanus_cycle_20260803_112606.txt` (216) |
| Script | `scripts/database_manager/enrich_lanus_campaign.py` |
| Backup | `data/inputs/contacts_backup_before_lanus_enrich.db` |

### 17.3 Accounts and Distribution

| Account | Emails sent |
|--------|----------------|
| wwwlanuscomputacion@gmail.com | 19 |
| adrianaavila131969@gmail.com | 19 |
| fernando1141967@gmail.com | 19 |
| selvaggiesteban9@gmail.com | 19 |
| selvaggiesteban4@gmail.com | 19 |
| selvaggiesteban11@gmail.com | 19 |
| marketing1a1oficial@gmail.com | 19 |
| selvaggiconsultores@gmail.com | 19 |
| estebanmfwd@gmail.com | 19 |
| selvaggiesteban1@gmail.com | 19 |
| selvaggiesteban2@gmail.com | 19 |
| marcelagomez7799@gmail.com | 19 |

---

## 18. Enrichment Campaign BA/CABA-03082026

### 18.1 Campaign Data

| Field | Value |
|-------|-------|
| `list_val` | `BA-CABA-03082026` |
| `subject` | Computer Technical Service and Technology Products |
| `type` | `ba_caba_servicio_tecnico` |
| `message` | Hello, good morning. How are you? I hope very well. I am contacting you to provide technical service for computers and technology products. We provide solutions for both individuals and shops and companies in the area. If you need repair, maintenance or equipment, you can contact us. I remain at your disposal for whatever you need. Kind regards |

### 18.2 Results

| Metric | Value |
|---------|-------|
| Execution Date | 2026-08-03 |
| Duration | 1:37:39 |
| Emails sent | 196 |
| Contacts reached | 9,800 (50 BCC $\times$ 196 emails) |
| Entries in campaign | 9,166 |
| Skipped (not found/duplicates) | 13 |
| Accounts used | 12 |
| Structure | TO=self, BCC=50 contacts |
| Logs | `log_ba_ciclo_20260803_135251.txt` |

### 18.3 Distribution by Account

| Account | Contacts |
|--------|----------------|
| fernando1141967@gmail.com | 850 contacts |
| adrianaavila131969@gmail.com | 850 contacts |
| wwwlanuscomputacion@gmail.com | 849 contacts |
| selvaggiesteban9@gmail.com | 828 contacts |
| selvaggiesteban4@gmail.com | 799 contacts |
| selvaggiesteban2@gmail.com | 799 contacts |
| selvaggiesteban11@gmail.com | 799 contacts |
| selvaggiconsultores@gmail.com | 799 contacts |
| marketing1a1oficial@gmail.com | 799 contacts |
| marketing1a1oficial@gmail.com | 798 contacts |
| estebanmfwd@gmail.com | 796 contacts |
| selvaggiesteban1@gmail.com | 200 contacts |

---

## 19. Data Sources — Work Directory CSVs

### 19.1 CSV Files

| File | Records | Description |
|---------|-----------|-------------|
| `WORK - CAMPAIGNS.csv` | 18 | Email marketing campaigns sent |
| `WORK - CHAT.csv` | 0 | Chat history (empty) |
| `WORK - GEOGRAPHIC COVERAGE.csv` | 12,045 | Geographic zones with coordinates |
| `WORK - TIME CONTROL.csv` | 153 | Hourly availability by service/date |
| `WORK - EMAILS.csv` | 17 | Email accounts (Gmail, Hostinger, Hotmail, iCloud) |
| `WORK - AI.csv` | 23 | OLLAMA/GROQ agent usage per week |
| `WORK - KEYWORDS.csv` | 1,747 | Search keyword list |
| `WORK - OBJECTIVES.csv` | 12 | 2026 monthly objectives |
| `WORK - WEB PAGES.csv` | 50 | Web pages with keywords and URLs |
| `WORK - SCRAP.csv` | 58 | Scraping results by zone |

### 19.2 Generated JSON

**File:** `Work/work_data.json` (3.5 MB)

**Script:** `scripts/csv_to_json.py`

**Usage:**
```bash
python scripts/csv_to_json.py
```

### 19.3 JSON Structure

```json
{
  "metadata": { ... },
  "campanas": [ ... ],
  "chat": [ ... ],
  "cobertura_geografica": [ ... ],
  "control_horario": [ ... ],
  "emails_cuentas": [ ... ],
  "agentes_ia": [ ... ],
  "keywords": [ ... ],
  "objetivos": [ ... ],
  "paginas_web": [ ... ],
  "scraping": [ ... ]
}
```

### 19.4 Field Mapping — CAMPAIGNS

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Title` | `titulo` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `List` | `lista` | string |
| `Subject` | `asunto` | string |
| `Date` | `fecha` | string |
| `Message` | `mensaje` | string |
| `Status` | `estado` | string |
| `Emails sent` | `emails_enviados` | int |
| `Unique contacts` | `contactos_unicos` | int |
| `Failures` | `fallos` | int |
| `Duration` | `duracion` | string |
| `Accounts used` | `cuentas_usadas` | int |
| `Enriched` | `enriched` | string |
| `Log file` | `log_file` | string |

### 19.5 Field Mapping — EMAILS

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Provider` | `proveedor` | string |
| `User` | `usuario` | string |
| `Password` | `contraseña` | string |
| `Application Password` | `contraseña_aplicacion` | string |
| `OAuth Client ID` | `oauth_client_id` | string |

### 19.6 Field Mapping — GEOGRAPHIC COVERAGE

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `order` | `order` | int |
| `id` | `id` | string |
| `desc` | `desc` | string |
| `north` | `north` | float |
| `west` | `west` | float |
| `south` | `south` | float |
| `east` | `east` | float |
| `cells` | `cells` | int |
| `queries` | `queries` | string |
| `density` | `density` | int |

### 19.7 Field Mapping — TIME CONTROL

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Price` | `precio` | int |
| `Service` | `servicio` | string |
| `Date` | `fecha` | string |
| `9:00` - `16:00` | `horas.9:00` - `horas.16:00` | bool |

### 19.8 Field Mapping — AI

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `AI_Agent` (part 1) | `agente` | string |
| `AI_Agent` (part 2) | `email` | string |
| `Week X` | `semanas.Week X` | bool |

### 19.9 Field Mapping — OBJECTIVES

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Month / Year` | `mes_anio` | string |
| `Working Days` | `dias_habiles` | int |
| `CPI` | `ipc` | string |
| `Price per Session` | `precio_sesion` | int |
| `Available Sessions` | `sesiones_disponibles` | int |
| `Sold Sessions (Target)` | `sesiones_vendidas_objetivo` | int |
| `Earnings` | `ganancias` | string |

### 19.10 Field Mapping — WEB PAGES

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Site` | `sitio` | string |
| `Keyword` | `keyword` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `Campaign` | `campana` | string |
| `URL_ES` | `url_es` | string |
| `URL_EN` | `url_en` | string |
| `Links sent` | `links_enviados` | string |
| `Sold Sessions (Target)` | `sesiones_vendidas_objetivo` | string |
| `Date / Time` | `fecha_hora` | string |

### 19.11 Field Mapping — SCRAPING

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Title` | `titulo` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `Keywords` | `keywords` | string |
| `Date` | `fecha` | string |
| `Status` | `estado` | string |
| `Rows` | `rows` | int |
| `Unique Emails` | `emails_unicos` | int |
| `Location` | `ubicacion` | string |
| `Duration` | `duracion` | string |
| `Log File` | `log_file` | string |

### 19.12 Notes

- Numbers with thousands separators (e.g., `10,800`) are converted to `10800`.
- Geographic coordinates are stored as float (e.g., `-347.100` $\rightarrow$ `-347.1`).
- The CSV `WORK - CHAT.csv` is empty (headers only).
- The script `csv_to_json.py` handles UTF-8 and cp1252 encoding.

---

## 20. Deduplication

### 20.1 Deduplication Key

**Primary:** `main.title` + `main.city` (both normalized, lowercase, no extra spaces).

### 20.2 Handling Duplicates

Print to console:
```
DUPLICATE FOUND:
  Existing: ROWID=X | title="..." | city="..." | email="..."
  New:     title="..." | city="..." | email="..."
  Options: [S]kip / [U]pdate / [M]erge
```

Pause and wait for user input.

- **Skip**: ignore the new one, keep existing.
- **Update**: overwrite empty fields of existing with new values.
- **Merge**: combine fields (do not overwrite existing data).

---

## 21. Implementation Notes

- Enrichment scripts must import these rules as a reference.
- Regex and blacklist lists must be maintained in a single place (this file or a Python module).
- Any rule change is documented here with a date.

---

## 22. Data Enrichment — Results (2026-07-20)

### 22.1 Data Sources — Import Status

| Source | Files | Unique Emails | Imported | Status |
|--------|----------|---------------|------------|--------|
| Brevo CSV (base_tvmas.csv) | 1 | 9,310 | 9,310 | ✅ 99.96% coverage |
| Brevo CSV (brevo_10042026.csv) | 1 | 12,763 | ~12,763 | ✅ Derived from base_tvmas |
| Brevo CSV (brevo_consolidada_total.csv) | 1 | 12,763 | ~12,763 | ✅ Derived from base_tvmas |
| Gosom General | 1 | 5,347 | 5,347 | ✅ import_gosom_general.py |
| Gosom RRHH | 1 | 5,434 | 5,434 | ✅ import_rrhh_gosom.py |
| Gosom Root (44 CSVs) | 44 | ~4,500 | 303 | ✅ import_gosom_root.py |
| WhatsApp VCFs | 13 | 92 | 92 | ✅ import_vcf.py (phone-only) |
| XLSX Trade Fairs (62 files) | 62 | ~34,000 | 0 | ✅ Already in DB (duplicates) |
| Blacklist (REJECTED CONTACTS) | 1 | 198 | 198 | ✅ Marked BLACKLISTED |
| Google Contacts (7 CSVs) | 7 | ~6,600 | 0 | ✅ Already in DB (duplicates) |
| Pre-existing (date_added=NULL) | — | 99,261 | 99,261 | ✅ Brevo legacy import |

### 22.2 Verified Sources (Gap Closed)

| Source | Files | Unique Emails | Result |
|--------|----------|---------------|-----------|
| Gosom webdata/ (36 UUID CSVs) | 36 | 792 | ✅ Already in DB (import_gosom_root.py) |
| Gosom web_marketing_caba.csv | 1 | 231 | ✅ Already in DB (import_gosom_root.py) |
| contacts Mailrelay | 1 | 71 | ✅ Already in DB (import_mailrelay.py created) |
| contacts selvaggiesteban (phone-only) | 1 | 2,643 | ✅ import_phone_contacts.py (dedup 15K $\rightarrow$ 2.6K) |
| LinkedIn people/authors CSVs | 2 | 118 | ✅ import_linkedin_profiles.py (no email/tel) |
| YOLANDA.csv | 1 | ~500 | ⏳ Non-standard format (pending) |

### 22.3 DB Current State

| Metric | Value |
|---------|-------|
| Total contacts | 123,763 |
| With valid email | 116,747 |
| With phones | 59,739 |
| With LinkedIn | 114 |
| Phone-only (no email) | 5,738 |
| With social networks | 0 (8 columns 100% NULL) |
| With sector | ~92,000 |
| With website | ~121,000 |
| BLACKLISTED | 198 |
| Pre-existing (no date) | 99,261 |
| Imported by scripts | ~24,500 |

### 22.4 Import Scripts and Utilities Created

| Script | Source | Status |
|--------|--------|--------|
| `config.py` | Centralized configuration | ✅ Active |
| `utils.py` | Shared utilities | ✅ Active |
| `verify_imported.py` | Source verification | ✅ Executed |
| `import_vcf.py` | WhatsApp VCFs | ✅ Completed (92 contacts) |
| `import_gosom_root.py` | Gosom root CSVs | ✅ Completed (303 contacts) |
| `import_gosom_general.py` | Gosom General CSV | ✅ Completed (5,347 contacts) |
| `import_rrhh_gosom.py` | Gosom RRHH CSV | ✅ Completed (5,434 contacts) |
| `import_xlsx.py` | XLSX trade fairs | ✅ Executed (0 new, all duplicates) |
| `import_blacklist.py` | REJECTED CONTACTS.docx | ✅ Completed (198 blacklisted) |
| `import_google_contacts.py` | Google Contacts CSVs | ✅ Executed (0 new, 2 tel updated) |
| `import_gosom_webdata.py` | Gosom webdata/ + web_marketing_caba | ✅ Executed (0 new, all already in DB) |
| `import_mailrelay.py` | Mailrelay CSV | ✅ Executed (0 new, all already in DB) |
| `import_phone_contacts.py` | contacts selvaggiesteban (phone-only) | ✅ 2,643 contacts imported |
| `import_linkedin_profiles.py` | LinkedIn people/authors CSVs | ✅ 118 profiles imported |
| `cleanup_duplicate_emails.py` | Duplicate email dedup | ✅ Active |
| `remove_duplicates.py` | CSV dedup | ✅ Active |
| `remove_duplicates_xlsx.py` | XLSX dedup | ✅ Active |
| `enrich_abogados.py` | Lawyer enrichment via web scraping | ✅ Active |
| `enumerate_prefixes.py` | Email prefix analysis | ✅ Active |
| `archive/cleanup_phase3.py` | Archived cleanup (encoding) | 📦 Archived |
| `archive/cleanup_phase4.py` | Archived cleanup (junk emails) | 📦 Archived |
| `archive/cleanup_phase7.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase8.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase9.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase10.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase11.py` | Archived cleanup | 📦 Archived |
| `archive/migrate_v4.py` | Archived DB v4 migration | 📦 Archived |

---

## 15. Schema Update — campaign.email_used

### 15.1 New Column

```sql
ALTER TABLE campaign ADD COLUMN email_used TEXT;
```

Records the exact email of the recipient to whom each campaign was sent. Allows a contact with multiple emails to receive multiple campaigns (one per email).

### 15.2 Usage

- When sending a campaign: `campaign.email_used = recipient_email`
- When querying campaigns: filter by `email_used` to know which email was used
- Backward compatibility: existing rows remain with `email_used = NULL`

---

## 16. Schema Update — campaign.message

### 16.1 New Column

```sql
ALTER TABLE campaign ADD COLUMN message TEXT;
```

Records the body of the message sent in each campaign. Allows querying the exact content received by each contact.

### 16.2 Usage

- When sending a campaign: `campaign.message = message_body`
- When querying campaigns: filter by `message` to know what content was sent
- Backward compatibility: existing rows remain with `message = NULL`

---

## 17. Enrichment Campaign LANÚS-03082026

### 17.1 Campaign Data

| Field | Value |
|-------|-------|
| `list_val` | `LANÚS-03082026` |
| `subject` | Computer Technical Service and Technology Products |
| `type` | `lanus_servicio_tecnico` |
| `message` | Hello, good morning. How are you? I hope very well. I am contacting you to provide technical service for computers and technology products. We provide solutions for both individuals and shops and companies in the area. If you need repair, maintenance or equipment, you can contact us. I remain at your disposal for whatever you need. Kind regards |

### 17.2 Results

| Metric | Value |
|---------|-------|
| Execution Date | 2026-08-03 |
| Contacts inserted | 228 |
| Accounts used | 12 (19 emails each) |
| Logs parsed | `log_lanus_cycle_20260803_112153.txt` (12) + `log_lanus_cycle_20260803_112606.txt` (216) |
| Script | `scripts/database_manager/enrich_lanus_campaign.py` |
| Backup | `data/inputs/contacts_backup_before_lanus_enrich.db` |

### 17.3 Accounts and Distribution

| Account | Emails sent |
|--------|----------------|
| wwwlanuscomputacion@gmail.com | 19 |
| adrianaavila131969@gmail.com | 19 |
| fernando1141967@gmail.com | 19 |
| selvaggiesteban9@gmail.com | 19 |
| selvaggiesteban4@gmail.com | 19 |
| selvaggiesteban11@gmail.com | 19 |
| marketing1a1oficial@gmail.com | 19 |
| selvaggiconsultores@gmail.com | 19 |
| estebanmfwd@gmail.com | 19 |
| selvaggiesteban1@gmail.com | 19 |
| selvaggiesteban2@gmail.com | 19 |
| marcelagomez7799@gmail.com | 19 |

---

## 18. Enrichment Campaign BA/CABA-03082026

### 18.1 Campaign Data

| Field | Value |
|-------|-------|
| `list_val` | `BA-CABA-03082026` |
| `subject` | Computer Technical Service and Technology Products |
| `type` | `ba_caba_servicio_tecnico` |
| `message` | Hello, good morning. How are you? I hope very well. I am contacting you to provide technical service for computers and technology products. We provide solutions for both individuals and shops and companies in the area. If you need repair, maintenance or equipment, you can contact us. I remain at your disposal for whatever you need. Kind regards |

### 18.2 Results

| Metric | Value |
|---------|-------|
| Execution Date | 2026-08-03 |
| Duration | 1:37:39 |
| Emails sent | 196 |
| Contacts reached | 9,800 (50 BCC $\times$ 196 emails) |
| Entries in campaign | 9,166 |
| Skipped (not found/duplicates) | 13 |
| Accounts used | 12 |
| Structure | TO=self, BCC=50 contacts |
| Logs | `log_ba_ciclo_20260803_135251.txt` |

### 18.3 Distribution by Account

| Account | Contacts |
|--------|----------------|
| fernando1141967@gmail.com | 850 contacts |
| adrianaavila131969@gmail.com | 850 contacts |
| wwwlanuscomputacion@gmail.com | 849 contacts |
| selvaggiesteban9@gmail.com | 828 contacts |
| selvaggiesteban4@gmail.com | 799 contacts |
| selvaggiesteban2@gmail.com | 799 contacts |
| selvaggiesteban11@gmail.com | 799 contacts |
| selvaggiconsultores@gmail.com | 799 contacts |
| marketing1a1oficial@gmail.com | 799 contacts |
| marketing1a1oficial@gmail.com | 798 contacts |
| estebanmfwd@gmail.com | 796 contacts |
| selvaggiesteban1@gmail.com | 200 contacts |

---

## 19. Data Sources — Work Directory CSVs

### 19.1 CSV Files

| File | Records | Description |
|---------|-----------|-------------|
| `WORK - CAMPAIGNS.csv` | 18 | Email marketing campaigns sent |
| `WORK - CHAT.csv` | 0 | Chat history (empty) |
| `WORK - GEOGRAPHIC COVERAGE.csv` | 12,045 | Geographic zones with coordinates |
| `WORK - TIME CONTROL.csv` | 153 | Hourly availability by service/date |
| `WORK - EMAILS.csv` | 17 | Email accounts (Gmail, Hostinger, Hotmail, iCloud) |
| `WORK - AI.csv` | 23 | OLLAMA/GROQ agent usage per week |
| `WORK - KEYWORDS.csv` | 1,747 | Search keyword list |
| `WORK - OBJECTIVES.csv` | 12 | 2026 monthly objectives |
| `WORK - WEB PAGES.csv` | 50 | Web pages with keywords and URLs |
| `WORK - SCRAP.csv` | 58 | Scraping results by zone |

### 19.2 Generated JSON

**File:** `Work/work_data.json` (3.5 MB)

**Script:** `scripts/csv_to_json.py`

**Usage:**
```bash
python scripts/csv_to_json.py
```

### 19.3 JSON Structure

```json
{
  "metadata": { ... },
  "campanas": [ ... ],
  "chat": [ ... ],
  "cobertura_geografica": [ ... ],
  "control_horario": [ ... ],
  "emails_cuentas": [ ... ],
  "agentes_ia": [ ... ],
  "keywords": [ ... ],
  "objetivos": [ ... ],
  "paginas_web": [ ... ],
  "scraping": [ ... ]
}
```

### 19.4 Field Mapping — CAMPAIGNS

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Title` | `titulo` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `List` | `lista` | string |
| `Subject` | `asunto` | string |
| `Date` | `fecha` | string |
| `Message` | `mensaje` | string |
| `Status` | `estado` | string |
| `Emails sent` | `emails_enviados` | int |
| `Unique contacts` | `contactos_unicos` | int |
| `Failures` | `fallos` | int |
| `Duration` | `duracion` | string |
| `Accounts used` | `cuentas_usadas` | int |
| `Enriched` | `enriched` | string |
| `Log file` | `log_file` | string |

### 19.5 Field Mapping — EMAILS

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Provider` | `proveedor` | string |
| `User` | `usuario` | string |
| `Password` | `contraseña` | string |
| `Application Password` | `contraseña_aplicacion` | string |
| `OAuth Client ID` | `oauth_client_id` | string |

### 19.6 Field Mapping — GEOGRAPHIC COVERAGE

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `order` | `order` | int |
| `id` | `id` | string |
| `desc` | `desc` | string |
| `north` | `north` | float |
| `west` | `west` | float |
| `south` | `south` | float |
| `east` | `east` | float |
| `cells` | `cells` | int |
| `queries` | `queries` | string |
| `density` | `density` | int |

### 19.7 Field Mapping — TIME CONTROL

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Price` | `precio` | int |
| `Service` | `servicio` | string |
| `Date` | `fecha` | string |
| `9:00` - `16:00` | `horas.9:00` - `horas.16:00` | bool |

### 19.8 Field Mapping — AI

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `AI_Agent` (part 1) | `agente` | string |
| `AI_Agent` (part 2) | `email` | string |
| `Week X` | `semanas.Week X` | bool |

### 19.9 Field Mapping — OBJECTIVES

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Month / Year` | `mes_anio` | string |
| `Working Days` | `dias_habiles` | int |
| `CPI` | `ipc` | string |
| `Price per Session` | `precio_sesion` | int |
| `Available Sessions` | `sesiones_disponibles` | int |
| `Sold Sessions (Target)` | `sesiones_vendidas_objetivo` | int |
| `Earnings` | `ganancias` | string |

### 19.10 Field Mapping — WEB PAGES

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Site` | `sitio` | string |
| `Keyword` | `keyword` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `Campaign` | `campana` | string |
| `URL_ES` | `url_es` | string |
| `URL_EN` | `url_en` | string |
| `Links sent` | `links_enviados` | string |
| `Sold Sessions (Target)` | `sesiones_vendidas_objetivo` | string |
| `Date / Time` | `fecha_hora` | string |

### 19.11 Field Mapping — SCRAPING

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Title` | `titulo` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `Keywords` | `keywords` | string |
| `Date` | `fecha` | string |
| `Status` | `estado` | string |
| `Rows` | `rows` | int |
| `Unique Emails` | `emails_unicos` | int |
| `Location` | `ubicacion` | string |
| `Duration` | `duracion` | string |
| `Log File` | `log_file` | string |

### 19.12 Notes

- Numbers with thousands separators (e.g., `10,800`) are converted to `10800`.
- Geographic coordinates are stored as float (e.g., `-347.100` $\rightarrow$ `-347.1`).
- The CSV `WORK - CHAT.csv` is empty (headers only).
- The script `csv_to_json.py` handles UTF-8 and cp1252 encoding.

---

## 20. Deduplication

### 20.1 Deduplication Key

**Primary:** `main.title` + `main.city` (both normalized, lowercase, no extra spaces).

### 20.2 Handling Duplicates

Print to console:
```
DUPLICATE FOUND:
  Existing: ROWID=X | title="..." | city="..." | email="..."
  New:     title="..." | city="..." | email="..."
  Options: [S]kip / [U]pdate / [M]erge
```

Pause and wait for user input.

- **Skip**: ignore the new one, keep existing.
- **Update**: overwrite empty fields of existing with new values.
- **Merge**: combine fields (do not overwrite existing data).

---

## 21. Implementation Notes

- Enrichment scripts must import these rules as a reference.
- Regex and blacklist lists must be maintained in a single place (this file or a Python module).
- Any rule change is documented here with a date.

---

## 22. Data Enrichment — Results (2026-07-20)

### 22.1 Data Sources — Import Status

| Source | Files | Unique Emails | Imported | Status |
|--------|----------|---------------|------------|--------|
| Brevo CSV (base_tvmas.csv) | 1 | 9,310 | 9,310 | ✅ 99.96% coverage |
| Brevo CSV (brevo_10042026.csv) | 1 | 12,763 | ~12,763 | ✅ Derived from base_tvmas |
| Brevo CSV (brevo_consolidada_total.csv) | 1 | 12,763 | ~12,763 | ✅ Derived from base_tvmas |
| Gosom General | 1 | 5,347 | 5,347 | ✅ import_gosom_general.py |
| Gosom RRHH | 1 | 5,434 | 5,434 | ✅ import_rrhh_gosom.py |
| Gosom Root (44 CSVs) | 44 | ~4,500 | 303 | ✅ import_gosom_root.py |
| WhatsApp VCFs | 13 | 92 | 92 | ✅ import_vcf.py (phone-only) |
| XLSX Trade Fairs (62 files) | 62 | ~34,000 | 0 | ✅ Already in DB (duplicates) |
| Blacklist (REJECTED CONTACTS) | 1 | 198 | 198 | ✅ Marked BLACKLISTED |
| Google Contacts (7 CSVs) | 7 | ~6,600 | 0 | ✅ Already in DB (duplicates) |
| Pre-existing (date_added=NULL) | — | 99,261 | 99,261 | ✅ Brevo legacy import |

### 22.2 Verified Sources (Gap Closed)

| Source | Files | Unique Emails | Result |
|--------|----------|---------------|-----------|
| Gosom webdata/ (36 UUID CSVs) | 36 | 792 | ✅ Already in DB (import_gosom_root.py) |
| Gosom web_marketing_caba.csv | 1 | 231 | ✅ Already in DB (import_gosom_root.py) |
| contacts Mailrelay | 1 | 71 | ✅ Already in DB (import_mailrelay.py created) |
| contacts selvaggiesteban (phone-only) | 1 | 2,643 | ✅ import_phone_contacts.py (dedup 15K $\rightarrow$ 2.6K) |
| LinkedIn people/authors CSVs | 2 | 118 | ✅ import_linkedin_profiles.py (no email/tel) |
| YOLANDA.csv | 1 | ~500 | ⏳ Non-standard format (pending) |

### 22.3 DB Current State

| Metric | Value |
|---------|-------|
| Total contacts | 123,763 |
| With valid email | 116,747 |
| With phones | 59,739 |
| With LinkedIn | 114 |
| Phone-only (no email) | 5,738 |
| With social networks | 0 (8 columns 100% NULL) |
| With sector | ~92,000 |
| With website | ~121,000 |
| BLACKLISTED | 198 |
| Pre-existing (no date) | 99,261 |
| Imported by scripts | ~24,500 |

### 22.4 Import Scripts and Utilities Created

| Script | Source | Status |
|--------|--------|--------|
| `config.py` | Centralized configuration | ✅ Active |
| `utils.py` | Shared utilities | ✅ Active |
| `verify_imported.py` | Source verification | ✅ Executed |
| `import_vcf.py` | WhatsApp VCFs | ✅ Completed (92 contacts) |
| `import_gosom_root.py` | Gosom root CSVs | ✅ Completed (303 contacts) |
| `import_gosom_general.py` | Gosom General CSV | ✅ Completed (5,347 contacts) |
| `import_rrhh_gosom.py` | Gosom RRHH CSV | ✅ Completed (5,434 contacts) |
| `import_xlsx.py` | XLSX trade fairs | ✅ Executed (0 new, all duplicates) |
| `import_blacklist.py` | REJECTED CONTACTS.docx | ✅ Completed (198 blacklisted) |
| `import_google_contacts.py` | Google Contacts CSVs | ✅ Executed (0 new, 2 tel updated) |
| `import_gosom_webdata.py` | Gosom webdata/ + web_marketing_caba | ✅ Executed (0 new, all already in DB) |
| `import_mailrelay.py` | Mailrelay CSV | ✅ Executed (0 new, all already in DB) |
| `import_phone_contacts.py` | contacts selvaggiesteban (phone-only) | ✅ 2,643 contacts imported |
| `import_linkedin_profiles.py` | LinkedIn people/authors CSVs | ✅ 118 profiles imported |
| `cleanup_duplicate_emails.py` | Duplicate email dedup | ✅ Active |
| `remove_duplicates.py` | CSV dedup | ✅ Active |
| `remove_duplicates_xlsx.py` | XLSX dedup | ✅ Active |
| `enrich_abogados.py` | Lawyer enrichment via web scraping | ✅ Active |
| `enumerate_prefixes.py` | Email prefix analysis | ✅ Active |
| `archive/cleanup_phase3.py` | Archived cleanup (encoding) | 📦 Archived |
| `archive/cleanup_phase4.py` | Archived cleanup (junk emails) | 📦 Archived |
| `archive/cleanup_phase7.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase8.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase9.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase10.py` | Archived cleanup | 📦 Archived |
| `archive/cleanup_phase11.py` | Archived cleanup | 📦 Archived |
| `archive/migrate_v4.py` | Archived DB v4 migration | 📦 Archived |

---

## 15. Schema Update — campaign.email_used

### 15.1 New Column

```sql
ALTER TABLE campaign ADD COLUMN email_used TEXT;
```

Records the exact email of the recipient to whom each campaign was sent. Allows a contact with multiple emails to receive multiple campaigns (one per email).

### 15.2 Usage

- When sending a campaign: `campaign.email_used = recipient_email`
- When querying campaigns: filter by `email_used` to know which email was used
- Backward compatibility: existing rows remain with `email_used = NULL`

---

## 16. Schema Update — campaign.message

### 16.1 New Column

```sql
ALTER TABLE campaign ADD COLUMN message TEXT;
```

Records the body of the message sent in each campaign. Allows querying the exact content received by each contact.

### 16.2 Usage

- When sending a campaign: `campaign.message = message_body`
- When querying campaigns: filter by `message` to know what content was sent
- Backward compatibility: existing rows remain with `message = NULL`

---

## 17. Enrichment Campaign LANÚS-03082026

### 17.1 Campaign Data

| Field | Value |
|-------|-------|
| `list_val` | `LANÚS-03082026` |
| `subject` | Computer Technical Service and Technology Products |
| `type` | `lanus_servicio_tecnico` |
| `message` | Hello, good morning. How are you? I hope very well. I am contacting you to provide technical service for computers and technology products. We provide solutions for both individuals and shops and companies in the area. If you need repair, maintenance or equipment, you can contact us. I remain at your disposal for whatever you need. Kind regards |

### 17.2 Results

| Metric | Value |
|---------|-------|
| Execution Date | 2026-08-03 |
| Contacts inserted | 228 |
| Accounts used | 12 (19 emails each) |
| Logs parsed | `log_lanus_cycle_20260803_112153.txt` (12) + `log_lanus_cycle_20260803_112606.txt` (216) |
| Script | `scripts/database_manager/enrich_lanus_campaign.py` |
| Backup | `data/inputs/contacts_backup_before_lanus_enrich.db` |

### 17.3 Accounts and Distribution

| Account | Emails sent |
|--------|----------------|
| wwwlanuscomputacion@gmail.com | 19 |
| adrianaavila131969@gmail.com | 19 |
| fernando1141967@gmail.com | 19 |
| selvaggiesteban9@gmail.com | 19 |
| selvaggiesteban4@gmail.com | 19 |
| selvaggiesteban11@gmail.com | 19 |
| marketing1a1oficial@gmail.com | 19 |
| selvaggiconsultores@gmail.com | 19 |
| estebanmfwd@gmail.com | 19 |
| selvaggiesteban1@gmail.com | 19 |
| selvaggiesteban2@gmail.com | 19 |
| marcelagomez7799@gmail.com | 19 |

---

## 18. Enrichment Campaign BA/CABA-03082026

### 18.1 Campaign Data

| Field | Value |
|-------|-------|
| `list_val` | `BA-CABA-03082026` |
| `subject` | Computer Technical Service and Technology Products |
| `type` | `ba_caba_servicio_tecnico` |
| `message` | Hello, good morning. How are you? I hope very well. I am contacting you to provide technical service for computers and technology products. We provide solutions for both individuals and shops and companies in the area. If you need repair, maintenance or equipment, you can contact us. I remain at your disposal for whatever you need. Kind regards |

### 18.2 Results

| Metric | Value |
|---------|-------|
| Execution Date | 2026-08-03 |
| Duration | 1:37:39 |
| Emails sent | 196 |
| Contacts reached | 9,800 (50 BCC $\times$ 196 emails) |
| Entries in campaign | 9,166 |
| Skipped (not found/duplicates) | 13 |
| Accounts used | 12 |
| Structure | TO=self, BCC=50 contacts |
| Logs | `log_ba_ciclo_20260803_135251.txt` |

### 18.3 Distribution by Account

| Account | Contacts |
|--------|----------------|
| fernando1141967@gmail.com | 850 contacts |
| adrianaavila131969@gmail.com | 850 contacts |
| wwwlanuscomputacion@gmail.com | 849 contacts |
| selvaggiesteban9@gmail.com | 828 contacts |
| selvaggiesteban4@gmail.com | 799 contacts |
| selvaggiesteban2@gmail.com | 799 contacts |
| selvaggiesteban11@gmail.com | 799 contacts |
| selvaggiconsultores@gmail.com | 799 contacts |
| marketing1a1oficial@gmail.com | 799 contacts |
| marketing1a1oficial@gmail.com | 798 contacts |
| estebanmfwd@gmail.com | 796 contacts |
| selvaggiesteban1@gmail.com | 200 contacts |

---

## 19. Data Sources — Work Directory CSVs

### 19.1 CSV Files

| File | Records | Description |
|---------|-----------|-------------|
| `WORK - CAMPAIGNS.csv` | 18 | Email marketing campaigns sent |
| `WORK - CHAT.csv` | 0 | Chat history (empty) |
| `WORK - GEOGRAPHIC COVERAGE.csv` | 12,045 | Geographic zones with coordinates |
| `WORK - TIME CONTROL.csv` | 153 | Hourly availability by service/date |
| `WORK - EMAILS.csv` | 17 | Email accounts (Gmail, Hostinger, Hotmail, iCloud) |
| `WORK - AI.csv` | 23 | OLLAMA/GROQ agent usage per week |
| `WORK - KEYWORDS.csv` | 1,747 | Search keyword list |
| `WORK - OBJECTIVES.csv` | 12 | 2026 monthly objectives |
| `WORK - WEB PAGES.csv` | 50 | Web pages with keywords and URLs |
| `WORK - SCRAP.csv` | 58 | Scraping results by zone |

### 19.2 Generated JSON

**File:** `Work/work_data.json` (3.5 MB)

**Script:** `scripts/csv_to_json.py`

**Usage:**
```bash
python scripts/csv_to_json.py
```

### 19.3 JSON Structure

```json
{
  "metadata": { ... },
  "campanas": [ ... ],
  "chat": [ ... ],
  "cobertura_geografica": [ ... ],
  "control_horario": [ ... ],
  "emails_cuentas": [ ... ],
  "agentes_ia": [ ... ],
  "keywords": [ ... ],
  "objetivos": [ ... ],
  "paginas_web": [ ... ],
  "scraping": [ ... ]
}
```

### 19.4 Field Mapping — CAMPAIGNS

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Title` | `titulo` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `List` | `lista` | string |
| `Subject` | `asunto` | string |
| `Date` | `fecha` | string |
| `Message` | `mensaje` | string |
| `Status` | `estado` | string |
| `Emails sent` | `emails_enviados` | int |
| `Unique contacts` | `contactos_unicos` | int |
| `Failures` | `fallos` | int |
| `Duration` | `duracion` | string |
| `Accounts used` | `cuentas_usadas` | int |
| `Enriched` | `enriched` | string |
| `Log file` | `log_file` | string |

### 19.5 Field Mapping — EMAILS

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Provider` | `proveedor` | string |
| `User` | `usuario` | string |
| `Password` | `contraseña` | string |
| `Application Password` | `contraseña_aplicacion` | string |
| `OAuth Client ID` | `oauth_client_id` | string |

### 19.6 Field Mapping — GEOGRAPHIC COVERAGE

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `order` | `order` | int |
| `id` | `id` | string |
| `desc` | `desc` | string |
| `north` | `north` | float |
| `west` | `west` | float |
| `south` | `south` | float |
| `east` | `east` | float |
| `cells` | `cells` | int |
| `queries` | `queries` | string |
| `density` | `density` | int |

### 19.7 Field Mapping — TIME CONTROL

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Price` | `precio` | int |
| `Service` | `servicio` | string |
| `Date` | `fecha` | string |
| `9:00` - `16:00` | `horas.9:00` - `horas.16:00` | bool |

### 19.8 Field Mapping — AI

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `AI_Agent` (part 1) | `agente` | string |
| `AI_Agent` (part 2) | `email` | string |
| `Week X` | `semanas.Week X` | bool |

### 19.9 Field Mapping — OBJECTIVES

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Month / Year` | `mes_anio` | string |
| `Working Days` | `dias_habiles` | int |
| `CPI` | `ipc` | string |
| `Price per Session` | `precio_sesion` | int |
| `Available Sessions` | `sesiones_disponibles` | int |
| `Sold Sessions (Target)` | `sesiones_vendidas_objetivo` | int |
| `Earnings` | `ganancias` | string |

### 19.10 Field Mapping — WEB PAGES

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Site` | `sitio` | string |
| `Keyword` | `keyword` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `Campaign` | `campana` | string |
| `URL_ES` | `url_es` | string |
| `URL_EN` | `url_en` | string |
| `Links sent` | `links_enviados` | string |
| `Sold Sessions (Target)` | `sesiones_vendidas_objetivo` | string |
| `Date / Time` | `fecha_hora` | string |

### 19.11 Field Mapping — SCRAPING

| CSV Column | JSON Field | Type |
|-------------|------------|------|
| `Title` | `titulo` | string |
| `Geographic Coverage` | `cobertura_geografica` | string |
| `Keywords` | `keywords` | string |
| `Date` | `fecha` | string |
| `Status` | `estado` | string |
| `Rows` | `rows` | int |
| `Unique Emails` | `emails_unicos` | int |
| `Location` | `ubicacion` | string |
| `Duration` | `duracion` | string |
| `Log File` | `log_file` | string |

### 19.12 Notes

- Numbers with thousands separators (e.g., `10,800`) are converted to `10800`.
- Geographic coordinates are stored as float (e.g., `-347.100` $\rightarrow$ `-347.1`).
- The CSV `WORK - CHAT.csv` is empty (headers only).
- The script `csv_to_json.py` handles UTF-8 and cp1252 encoding.

---

## 20. Deduplication

### 20.1 Deduplication Key

**Primary:** `main.title` + `main.city` (both normalized, lowercase, no extra spaces).

### 20.2 Handling Duplicates

Print to console:
```
DUPLICATE FOUND:
  Existing: ROWID=X | title="..." | city="..." | email="..."
  New:     title="..." | city="..." | email="..."
  Options: [S]kip / [U]pdate / [M]erge
```

Pause and wait for user input.

- **Skip**: ignore the new one, keep existing.
- **Update**: overwrite empty fields of existing with new values.
- **Merge**: combine fields (do not overwrite existing data).

---

## 21. Implementation Notes

- Enrichment scripts must import these rules as a reference.
- Regex and blacklist lists must be maintained in a single place (this file or a Python module).
- Any rule change is documented here with a date.

---

## 22. Data Enrichment — Results (202
