# ENRICH_RULES.md — Reglas de Enriquecimiento de contacts.db

> **Última actualización:** 2026-07-27
> **DB:** `data/inputs/contacts.db` (SQLite, v4 normalizada, ~124K contactos)

---

## 1. Validación de Emails — Código existente

### 1.1 Scripts que ya implementan validación

| Script | Ubicación | Qué hace | Reglas |
|---|---|---|---|
| `archive/cleanup_phase4.py` | `scripts/database_manager/archive/` | Elimina emails junk de la DB | 12 emails exactos + 2 dominios (`example.com`, `ejemplo.com`) + 2 substrings (`sentry`, `wixpress`) |
| `enrich_campaign_logs.py` | `scripts/database_manager/` | Filtra junk al importar logs EXITO/FALLO | `JUNK_PATTERNS`: sentry, wixpress, example, test, demo, `@2x.png`, `.js`, `username@domain`, `your@mail`, `juan.perez`, beispiel, ejemplo, mysite |
| `enrich_gmail_csvs.py` | `scripts/database_manager/` | Filtra junk al importar Gmail CSVs | Mismos `JUNK_PATTERNS` |
| `enrich_identity_maps.py` | `scripts/database_manager/` | Filtra junk al importar identity maps | Mismos `JUNK_PATTERNS` |
| `campaign_engine.py` | `scripts/e-mail_marketing_manager/e-mail_marketing_campaigns/` | Filtra al crear campañas | Regex + `exclude_patterns`: sentry, wixpress, noreply, abuse |
| `generate_5_csvs.py` | `scripts/e-mail_marketing_manager/` | Detecta auto-respuestas | `AUTO_REPLY_PATTERNS`: auto-reply, mailer-daemon, noreply, postmaster, bounce, donotreply, etc. (13 patrones) |

### 1.2 Reglas consolidadas de validación

**Regex base:**
```
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

**Dominios reject** (substrings en dominio):
`sentry`, `wixpress`, `example`, `ejemplo`, `test`, `demo`

**Patrones reject** (substrings en email completo):
`@2x.png`, `@2x.webp`, `.js`, `username@domain`, `your@mail`, `juan.perez`, `beispiel`, `ejemplo`, `mysite`

**Auto-reply / system reject** (prefix o substring):
`noreply`, `no-reply`, `mailer-daemon`, `postmaster`, `abuse`, `auto-reply`, `donotreply`, `auto_submit`

**Emails placeholder exactos** (rechazar si coincide):
`tunombre@email.com`, `usuario@dominio.com`, `nombre@ejemplo.com`, `john@doe.com`, `info@yourdomain.com`, `info@website.com`, `hola@miempresa.es`, `email@example.com`, `ejemplo@mail.com`, `email@ejemplo.com`, `nombre@mail.com`, `theratio_interior@mail.com`

### 1.3 Regla para múltiples emails en un campo

La DB tiene dos columnas: `lead.primary_email` y `lead.secondary_emails`.

Si el CSV trae múltiples emails en el campo `emails`:
- **Primero** → `lead.primary_email`
- **Resto** → `lead.secondary_emails` (separados por `;`)
- Cada email individual debe pasar la validación antes de guardarse

### 1.4 Regla de máxima cobertura

**Siempre insertar TODOS los emails nuevos de todas las filas**, no solo el primer email. Cada email válido que no exista en la DB debe generar un contacto nuevo.

- Un CSV con 38,869 filas puede contener ~5,177 emails únicos nuevos
- Si solo se toma el primer email de cada fila, se pierden ~565 emails (secundarios)
- Contactos con más de 1 email pueden recibir más de 1 campaña (una por cada email)

---

## 2. Encoding (Mojibake) — Código existente

### 2.1 Script actual

`cleanup_phase3.py:153-171` → función `fix_title_encoding()`

- Solo cubre el campo `title`
- Define 16 patrones de reemplazo
- **NO cubre**: `city` (1.158 filas afectadas), `country` (841), `sector` (14), `address`

### 2.2 Patrones de mojibake detectados

**Double-encoded UTF-8** (los más comunes):
```
Ã± → ñ    Ã© → é    Ã¡ → á    Ã³ → ó
Ã­ → í    Ã¼ → ü    Ã  → à    Ã¨ → è
Ã´ → ò    Ã¢ → a    Ã¤ → ä    Ã¶ → ö
Ã§ → ç    Ã® → î    Ã´ → ô
```

**Patrones Â prefix:**
```
Â° → °    Âº → º    Â· → ·
```

**Triple-encoded** (casos puntuales):
```
Ã³nico → único    Ã³noma → autónoma
```

### 2.3 Regla de aplicación

- Aplicar SOLO si el string contiene patrones de mojibake (detectar con `Ã` o `Â`)
- No sobrescribir si la corrección no tiene sentido
- Loggear cada corrección aplicada (campo, ROWID, valor antes/después)
- Aplicar a TODOS los campos de texto: `title`, `sector`, `city`, `province`, `country`, `address`

---

## 3. Reglas de Mapeo CSV Gosom → contacts.db

### 3.1 Estructura del CSV Gosom (35 columnas)

```
input_id, link, title, category, address, open_hours, popular_times,
website, phone, plus_code, review_count, review_rating,
reviews_per_rating, latitude, longitude, cid, status, descriptions,
reviews_link, thumbnail, timezone, price_range, data_id,
street_view_url, place_id, images, reservations, order_online,
menu, owner, complete_address, about, user_reviews,
user_reviews_extended, emails
```

### 3.2 Mapeo de campos

| Columna CSV | Columna DB | Tipo | Transformación |
|---|---|---|---|
| `title` | `main.title` | TEXT | Sin transformación |
| `category` | `main.sector` | TEXT | Sin transformación |
| `address` | `main.address` | TEXT | Sin transformación |
| `complete_address` → `city` | `main.city` | TEXT | Parsear JSON, extraer campo `city` |
| `complete_address` → `state` | `main.province` | TEXT | Parsear JSON, extraer campo `state` |
| `complete_address` → `country` | `main.country` | TEXT | Parsear JSON, extraer campo `country` |
| *(fijo)* | `main.entity_type` | TEXT | `"empresa"` |
| `website` | `lead.website` | TEXT | Agregar `https://` si falta el protocolo |
| `phone` | `lead.phone` | TEXT | Sin transformación |
| `link` | `lead.google_maps` | TEXT | Solo si el contacto es nuevo en la DB |
| `emails` | `lead.primary_email` | TEXT | Validar con regex + blacklist. Si hay múltiples: primero → `primary_email`, resto → `secondary_emails` (separados por `;`) |
| *(fijo)* | `contact.date_added` | TEXT | `datetime.now().isoformat()` |

### 3.3 Campos ignorados del CSV

`input_id`, `open_hours`, `popular_times`, `plus_code`, `review_count`, `review_rating`, `reviews_per_rating`, `latitude`, `longitude`, `cid`, `status`, `descriptions`, `reviews_link`, `thumbnail`, `timezone`, `price_range`, `data_id`, `street_view_url`, `place_id`, `images`, `reservations`, `order_online`, `menu`, `owner`, `about`, `user_reviews`, `user_reviews_extended`

### 3.4 Archivos .txt (email list)

Los archivos `.txt` contienen emails separados por comas (no CSV con columnas).
- Importar cada email como contacto nuevo
- `lead.primary_email` = el email
- `main.entity_type` = `"empresa"`
- `contact.date_added` = `datetime.now().isoformat()`
- Resto de campos = NULL
- Aplicar misma validación de emails

---

## 4. Deduplicación

### 4.1 Clave de deduplicación

**Primaria:** `main.title` + `main.city` (ambos normalizados, lowercase, sin espacios extra)

### 4.2 Al encontrar duplicado

Imprimir en consola:
```
DUPLICADO ENCONTRADO:
  Existente: ROWID=X | title="..." | city="..." | email="..."
  Nuevo:     title="..." | city="..." | email="..."
  Opciones: [S]kip / [U]pdate / [M]erge
```

Pausar y esperar input del usuario.

- **Skip**: ignorar el nuevo, mantener el existente
- **Update**: sobrescribir campos vacíos del existente con los valores nuevos
- **Merge**: combinar campos (no sobrescribir lo que ya tiene dato)

---

## 5. Notas de implementación

- Los scripts de enrichment deben importar estas reglas como referencia
- El regex y las listas de blacklist deben mantenerse en un solo lugar (este archivo o un módulo Python)
- Cualquier cambio de reglas se documenta aquí con fecha

---

## 6. Data Enrichment — Resultados (2026-07-20)

### 6.1 Fuentes de datos — Estado de importación

| Fuente | Archivos | Emails únicos | Importados | Estado |
|--------|----------|---------------|------------|--------|
| Brevo CSV (base_tvmas.csv) | 1 | 9,310 | 9,310 | ✅ 99.96% cobertura |
| Brevo CSV (brevo_10042026.csv) | 1 | 12,763 | ~12,763 | ✅ Derivado de base_tvmas |
| Brevo CSV (brevo_consolidada_total.csv) | 1 | 12,763 | ~12,763 | ✅ Derivado de base_tvmas |
| Gosom General | 1 | 5,347 | 5,347 | ✅ import_gosom_general.py |
| Gosom RRHH | 1 | 5,434 | 5,434 | ✅ import_rrhh_gosom.py |
| Gosom Root (44 CSVs) | 44 | ~4,500 | 303 | ✅ import_gosom_root.py |
| WhatsApp VCFs | 13 | 92 | 92 | ✅ import_vcf.py (phone-only) |
| XLSX Ferias (62 files) | 62 | ~34,000 | 0 | ✅ Ya en DB (duplicados) |
| Blacklist (CONTACTOS RECHAZADOS) | 1 | 198 | 198 | ✅ Marcados BLACKLISTED |
| Google Contacts (7 CSVs) | 7 | ~6,600 | 0 | ✅ Ya en DB (duplicados) |
| Pre-existentes (date_added=NULL) | — | 99,261 | 99,261 | ✅ Brevo legacy import |

### 6.2 Fuentes verificadas (gap cerrado)

| Fuente | Archivos | Emails únicos | Resultado |
|--------|----------|---------------|-----------|
| Gosom webdata/ (36 UUID CSVs) | 36 | 792 | ✅ Ya en DB (import_gosom_root.py) |
| Gosom web_marketing_caba.csv | 1 | 231 | ✅ Ya en DB (import_gosom_root.py) |
| contacts Mailrelay | 1 | 71 | ✅ Ya en DB (import_mailrelay.py creado) |
| contacts selvaggiesteban (phone-only) | 1 | 2,643 | ✅ import_phone_contacts.py (dedup 15K→2.6K) |
| LinkedIn people/authors CSVs | 2 | 118 | ✅ import_linkedin_profiles.py (sin email/tel) |
| YOLANDA.csv | 1 | ~500 | ⏳ Formato no estándar (pendiente) |

### 6.3 DB Estado actual

| Métrica | Valor |
|---------|-------|
| Total contactos | 123,763 |
| Con email válido | 116,747 |
| Con teléfonos | 59,739 |
| Con LinkedIn | 114 |
| Phone-only (sin email) | 5,738 |
| Con redes sociales | 0 (8 columnas 100% NULL) |
| Con sector | ~92,000 |
| Con website | ~121,000 |
| BLACKLISTED | 198 |
| Pre-existentes (sin fecha) | 99,261 |
| Importados por scripts | ~24,500 |

### 6.4 Scripts de importación y utilidades creados

| Script | Fuente | Estado |
|--------|--------|--------|
| `config.py` | Configuración centralizada | ✅ Activo |
| `utils.py` | Utilidades compartidas | ✅ Activo |
| `verify_imported.py` | Verificación de fuentes | ✅ Ejecutado |
| `import_vcf.py` | WhatsApp VCFs | ✅ Completado (92 contactos) |
| `import_gosom_root.py` | Gosom root CSVs | ✅ Completado (303 contactos) |
| `import_gosom_general.py` | Gosom General CSV | ✅ Completado (5,347 contactos) |
| `import_rrhh_gosom.py` | Gosom RRHH CSV | ✅ Completado (5,434 contactos) |
| `import_xlsx.py` | XLSX ferias | ✅ Ejecutado (0 nuevos, todos duplicados) |
| `import_blacklist.py` | CONTACTOS RECHAZADOS.docx | ✅ Completado (198 blacklisted) |
| `import_google_contacts.py` | Google Contacts CSVs | ✅ Ejecutado (0 nuevos, 2 tel actualizados) |
| `import_gosom_webdata.py` | Gosom webdata/ + web_marketing_caba | ✅ Ejecutado (0 nuevos, todos ya en DB) |
| `import_mailrelay.py` | Mailrelay CSV | ✅ Ejecutado (0 nuevos, todos ya en DB) |
| `import_phone_contacts.py` | contacts selvaggiesteban (phone-only) | ✅ 2,643 contactos importados |
| `import_linkedin_profiles.py` | LinkedIn people/authors CSVs | ✅ 118 perfiles importados |
| `cleanup_duplicate_emails.py` | Dedup de emails duplicados | ✅ Activo |
| `remove_duplicates.py` | Dedup de CSVs | ✅ Activo |
| `remove_duplicates_xlsx.py` | Dedup de XLSX | ✅ Activo |
| `enrich_abogados.py` | Enriquecimiento de abogados vía web scraping | ✅ Activo |
| `enumerate_prefixes.py` | Análisis de prefijos de email | ✅ Activo |
| `archive/cleanup_phase3.py` | Cleanup archivado (encoding) | 📦 Archivado |
| `archive/cleanup_phase4.py` | Cleanup archivado (junk emails) | 📦 Archivado |
| `archive/cleanup_phase7.py` | Cleanup archivado | 📦 Archivado |
| `archive/cleanup_phase8.py` | Cleanup archivado | 📦 Archivado |
| `archive/cleanup_phase9.py` | Cleanup archivado | 📦 Archivado |
| `archive/cleanup_phase10.py` | Cleanup archivado | 📦 Archivado |
| `archive/cleanup_phase11.py` | Cleanup archivado | 📦 Archivado |
| `archive/migrate_v4.py` | Migración DB v4 archivada | 📦 Archivado |

---

## 7. Schema Update — campaign.email_used

### 7.1 Columna nueva

```sql
ALTER TABLE campaign ADD COLUMN email_used TEXT;
```

Registra el email exacto del destinatario al que se envió cada campaña. Permite que un contacto con múltiples emails reciba múltiples campañas (una por cada email).

### 7.2 Uso

- Al enviar una campaña: `campaign.email_used = recipient_email`
- Al consultar campañas: filtrar por `email_used` para saber a qué email se envió
- Compatibilidad hacia atrás: filas existentes quedan con `email_used = NULL`

---

## 8. Schema Update — campaign.message

### 8.1 Columna nueva

```sql
ALTER TABLE campaign ADD COLUMN message TEXT;
```

Registra el cuerpo del mensaje enviado en cada campaña. Permite consultar el contenido exacto que recibió cada contacto.

### 8.2 Uso

- Al enviar una campaña: `campaign.message = message_body`
- Al consultar campañas: filtrar por `message` para saber qué contenido se envió
- Compatibilidad hacia atrás: filas existentes quedan con `message = NULL`

---

## 9. Enriquecimiento Campaign LANÚS-03082026

### 9.1 Datos de campaña

| Campo | Valor |
|-------|-------|
| `list_val` | `LANÚS-03082026` |
| `subject` | Servicio Técnico de Computadoras y Productos de Tecnología |
| `type` | `lanus_servicio_tecnico` |
| `message` | Hola, buenos días. ¿Cómo estás? Espero que muy bien. Me comunico facilitando servicio técnico de computadoras y productos de tecnología. Brindamos soluciones tanto para particulares como para comercios y empresas de la zona. Si necesitás reparación, mantenimiento o equipamiento, podés contactarnos. Quedo a disposición para lo que necesites. Saludos cordiales |

### 9.2 Resultados

| Métrica | Valor |
|---------|-------|
| Fecha ejecución | 2026-08-03 |
| Contactos insertados | 228 |
| Cuentas utilizadas | 12 (19 emails cada una) |
| Logs parseados | `log_lanus_cycle_20260803_112153.txt` (12) + `log_lanus_cycle_20260803_112606.txt` (216) |
| Script | `scripts/database_manager/enrich_lanus_campaign.py` |
| Backup | `data/inputs/contacts_backup_before_lanus_enrich.db` |

### 9.3 Cuentas y distribución

| Cuenta | Emails enviados |
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

## 10. Enriquecimiento Campaign BA/CABA-03082026

### 10.1 Datos de campaña

| Campo | Valor |
|-------|-------|
| `list_val` | `BA-CABA-03082026` |
| `subject` | Servicio Tecnico de Computadoras y Productos de Tecnologia |
| `type` | `ba_caba_servicio_tecnico` |
| `message` | Hola, buenos dias. Como estas? Espero que muy bien. Me comunico facilitando servicio tecnico de computadoras y productos de tecnologia. Brindamos soluciones tanto para particulares como para comercios y empresas de la zona. Si necesitás reparacion, mantenimiento o equipamiento, podes contactarnos. Quedo a disposicion para lo que necesites. Saludos cordiales |

### 10.2 Resultados

| Métrica | Valor |
|---------|-------|
| Fecha ejecución | 2026-08-03 |
| Duración | 1:37:39 |
| Emails enviados | 196 |
| Contactos alcanzados | 9,800 (50 BCC × 196 emails) |
| Entradas en campaign | 9,166 |
| Skipped (no encontrados/duplicados) | 13 |
| Cuentas utilizadas | 12 |
| Estructura | TO=si misma, BCC=50 contactos |
| Logs | `log_ba_ciclo_20260803_135251.txt` |

### 10.3 Distribución por cuenta

| Cuenta | Emails enviados |
|--------|----------------|
| fernando1141967@gmail.com | 850 contactos |
| adrianaavila131969@gmail.com | 850 contactos |
| wwwlanuscomputacion@gmail.com | 849 contactos |
| selvaggiesteban9@gmail.com | 828 contactos |
| selvaggiesteban4@gmail.com | 799 contactos |
| selvaggiesteban2@gmail.com | 799 contactos |
| selvaggiesteban11@gmail.com | 799 contactos |
| selvaggiconsultores@gmail.com | 799 contactos |
| marcelagomez7799@gmail.com | 799 contactos |
| marketing1a1oficial@gmail.com | 798 contactos |
| estebanmfwd@gmail.com | 796 contactos |
| selvaggiesteban1@gmail.com | 200 contactos |

### 10.4 Scripts creados

| Script | Ubicación | Función |
|--------|-----------|---------|
| `campaign_sender_ba.py` | `scripts/e-mail_marketing_manager/` | Envío con 50 BCC, TO=si misma |
| `enrich_ba_caba_campaign.py` | `scripts/database_manager/` | Enriquecimiento DB post-envío |
