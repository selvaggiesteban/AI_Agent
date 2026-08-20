# AGENTS.md — Inventario de Agentes, Repositorios y MCP Servers

> **Última actualización:** 2026-07-27
> **Proyecto raíz:** `.`

---

## 1. Scripts Utilitarios (`scripts/`)

| Directorio local | Ruta completa | Archivos principales | Rol |
|---|---|---|---|
| `scripts/ad_studio/` | `scripts/ad_studio/` | `generar_gsr.py`, `gsr_batch_v7.py`, `brand/loader.py`, `brand/prompt_builder.py` | Generador de creatividades publicitarias con IA (Pollinations) + brand manuals |
| `scripts/campaign_manager/` | `scripts/campaign_manager/` | `campaign_ui.py`, `drafts.py` | Dashboard de campañas y creación de borradores Gmail |
| `scripts/database_manager/` | `scripts/database_manager/` | `config.py`, `utils.py`, `audit_db.py`, `contacts_editor.py`, `enrich_*.py`, `import_*.py`, `cleanup_duplicate_emails.py`, `remove_duplicates.py` | Gestión de contacts.db: auditoría, enriquecimiento, importación, dedup |
| `scripts/e-mail_marketing_manager/` | `scripts/e-mail_marketing_manager/` | `e-mail.py`, `generate_5_csvs.py` | Motor SMTP, extracción Gmail CSVs |
| &emsp;↳ `e-mail_marketing_campaigns/` | `scripts/e-mail_marketing_manager/e-mail_marketing_campaigns/` | `campaign_engine.py`, `campaign_launcher.py`, `find_unknown_leads.py`, `gmail_report.py`, `imap_bot.py` | Campañas de email y reporting |
| `scripts/financial_manager/` | `scripts/financial_manager/` | `accountly/main.py` | Dashboard contable (ARCA/Santander/MP) |
| `scripts/graphic_designer/` | `scripts/graphic_designer/` | `web-screenshot/web_screenshots.py` | Screenshots web con Selenium |
| `scripts/inbox_manager/` | `scripts/inbox_manager/` | — | (Módulo vacío, pendiente de desarrollo) |
| `scripts/seo_manager/` | `scripts/seo_manager/` | `keywords.py`, `seo-content-generator/seo_content_generator.py` | SEO técnico, keywords y contenido |
| `scripts/social_media_manager/` | `scripts/social_media_manager/` | `facebook.py`, `instagram.py`, `linkedin.py`, `messenger.py`, `telegram.py`, `whatsapp.py` | RPA redes sociales (Playwright) |
| &emsp;↳ `linkedin/` | `scripts/social_media_manager/linkedin/` | `linkedin_tools.py`, `linkedin_full_scraper.py`, `linkedin_parser.py` | Herramientas LinkedIn vía MCP |
| `scripts/web_designer/` | `scripts/web_designer/` | `landing-page-generator/landing-page-generator.py` | Generador de landing pages |
| &emsp;↳ `example/` | `scripts/web_designer/example/` | Astro + TypeScript (i18n, D1, MercadoPago) | Sitio selvaggiesteban.dev |
| `scripts/web_scraper/` | `scripts/web_scraper/` | `ecommerce.py`, `kompass.py`, `linkedin_ocr_scraper.py`, `research.py` | Scraping e inteligencia de mercado |
| &emsp;↳ `ecommercer-competitor-research/` | `scripts/web_scraper/ecommercer-competitor-research/` | — | Análisis competitivo ecommerce |
| &emsp;↳ `long-tail-keyword-crawler/` | `scripts/web_scraper/long-tail-keyword-crawler/` | — | Crawler de keywords long-tail |
| &emsp;↳ `paginasamarillas_web_scraper/` | `scripts/web_scraper/paginasamarillas_web_scraper/` | — | Scraper Páginas Amarillas |
| &emsp;↳ `smart-research-assistant/` | `scripts/web_scraper/smart-research-assistant/` | — | Research con IA + reportes PDF |
| &emsp;↳ `wordpress-seo-crawler/` | `scripts/web_scraper/wordpress-seo-crawler/` | — | Crawler SEO WordPress |

**Archivo raíz:** `scripts/check_providers.py` — Verifica disponibilidad de proveedores LLM

---

## 2. Repositorios Auxiliares (`core/`)

| Directorio local | Ruta completa | URL remota (GitHub) | Propósito | Propietario |
|---|---|---|---|---|
| `core/free-claude-code` | `core/free-claude-code` | https://github.com/Alishahryar1/free-claude-code | Proxy server para Claude Code CLI / Codex CLI | Alishahryar1 |

---

## 3. Skills (`skills/`)

| Archivo local | Ruta completa | Rol |
|---|---|---|
| `skills/ads_strategist.md` | `skills/ads_strategist.md` | Estrategia publicitaria TOFU/MOFU/BOFU |
| `skills/google-ads-audit.md` | `skills/google-ads-audit.md` | Auditoría de Google Ads |

---

## 4. Módulos Core (`core/*.py`)

| Archivo | Ruta completa | Función |
|---|---|---|
| `core/lead.py` | `core/lead.py` | Pipeline de prospección de leads |
| `core/services.py` | `core/services.py` | Servicios a clientes (contratos, web, SEO, ads) |
| `core/telemetry.py` | `core/telemetry.py` | Reportes consolidados de actividad |
| `core/ai_engine.py` | `core/ai_engine.py` | Motor de IA (LLMRouter: Gemini/OpenAI/Anthropic) |
| `core/__init__.py` | `core/__init__.py` | Inicialización del paquete |

---

## 5. MCP Servers — Estado Real (verificado 2026-06-24)

### 5.1 ✅ Conectados (14)

| MCP Server | Nombre config | Paquete | URL de referencia |
|---|---|---|---|
| **Figma MCP** | `figma` | Plugin HTTP | https://help.figma.com/hc/en-us/articles/32132100833559 |
| **Playwright MCP** | `playwright` | `@playwright/mcp` | https://github.com/microsoft/playwright-mcp |
| **Context7 MCP** | `context7` | `@upstash/context7-mcp` | https://github.com/upstash/context7 |
| **Supabase MCP** | `supabase` | `@supabase/mcp-server-supabase` | https://supabase.com/docs/guides/ai-tools/mcp |
| **GitHub MCP** | `github-mcp` | `@modelcontextprotocol/server-github` | https://github.com/modelcontextprotocol/servers/tree/main/src/github |
| **Chrome DevTools MCP** | `chrome-devtools` | `chrome-devtools-mcp` | https://github.com/chromedevtools/chrome-devtools-mcp |
| **GitHub (gh-cli)** | `github-gh` | `github-mcp` | https://github.com/github/github-mcp-server |
| **Firecrawl MCP** | `firecrawl` | `firecrawl-mcp` | https://docs.firecrawl.dev/mcp-server |
| **WordPress MCP** | `wordpress` | `wordpress-mcp-server` | https://github.com/Automattic/wordpress-mcp |
| **LinkedIn MCP** | `linkedin` | `linkedin-mcp` | https://github.com/stickerdaniel/linkedin-mcp-server |
| **Google Analytics** | `google-analytics` | `google-analytics-mcp-server` | https://github.com/googleanalytics/google-analytics-mcp |
| **Notion MCP** | `notion` | `@notionhq/notion-mcp-server` | https://github.com/notionhq/notion-mcp-server |
| **Redis MCP** | `redis` | `redis-mcp` | https://github.com/redis/mcp-redis |
| **Next.js DevTools** | `next-devtools` | `next-devtools-mcp` | https://github.com/vercel/next-devtools-mcp |

### 5.2 ⏳ Configurados, requieren API keys reales (18)

| MCP Server | Nombre config | Paquete npm | Env vars | URL de referencia |
|---|---|---|---|---|
| **Stripe MCP** | `stripe` | `@stripe/mcp` | `STRIPE_SECRET_KEY` | https://docs.stripe.com/mcp |
| **Vercel MCP** | `vercel` | `vercel-mcp` | `VERCEL_API_TOKEN` | https://vercel.com/docs/agent-resources/vercel-mcp |
| **Sentry MCP** | `sentry` | `@sentry/mcp-server` | `SENTRY_AUTH_TOKEN` | https://github.com/getsentry/sentry-mcp |
| **PostgreSQL MCP** | `postgres` | `@modelcontextprotocol/server-postgres` | `DATABASE_URL` | https://github.com/modelcontextprotocol/servers/tree/main/src/postgres |
| **Local SEO MCP** | `local-seo` | `@localseodata/mcp-server` | `LOCALSEO_API_KEY` | https://github.com/localseodata/mcp-server |
| **Google Drive MCP** | `gdrive` | `@modelcontextprotocol/server-gdrive` | `GDRIVE_CREDENTIALS_PATH` | https://github.com/modelcontextprotocol/servers-archived/tree/main/src/gdrive |
| **WhatsApp MCP** | `whatsapp` | `whatsapp-mcp` | Escaneo QR | https://github.com/lharries/whatsapp-mcp |
| **PayPal MCP** | `paypal` | `@paypal/mcp` | `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET` | https://github.com/paypal/agent-toolkit/tree/main/modelcontextprotocol |
| **Google Ads MCP** | `google-ads` | `google-ads-mcp` | `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_REFRESH_TOKEN`, `GOOGLE_ADS_DEVELOPER_TOKEN` | https://github.com/googleads/google-ads-mcp |
| **Hostinger MCP** | `hostinger` | `hostinger-mcp` | `HOSTINGER_API_TOKEN` | https://github.com/hostinger/api-mcp-server |
| **Docker MCP** | `docker` | `docker-mcp-server` | Docker env | https://github.com/docker/hub-mcp |
| **GCP Cloud Run** | `gcp-cloud-run` | `cloud-run-mcp` | GCP credentials | https://github.com/googlecloudplatform/cloud-run-mcp |
| **Falcon MCP** | `falcon` | `falcon-mcp-server` | CrowdStrike env | https://github.com/crowdstrike/falcon-mcp |
| **Atlassian MCP** | `atlassian` | `uvx mcp-atlassian` (Python) | `ATLASSIAN_URL`, `ATLASSIAN_EMAIL`, `ATLASSIAN_TOKEN` | https://github.com/sooperset/mcp-atlassian |
| **MailboxValidator** | `mailboxvalidator` | `uvx mcp-mailboxvalidator` (Python) | `MAILBOXVALIDATOR_API_KEY` | https://github.com/MailboxValidator/mcp-mailboxvalidator |
| **Cloudflare MCP** | `cloudflare` | `@cloudflare/mcp-server-cloudflare` | CF API token | https://github.com/cloudflare/mcp-server-cloudflare |
| **Fetch MCP** | `fetch` | `@modelcontextprotocol/server-fetch` | — (sin key, pero falla al conectar) | https://github.com/modelcontextprotocol/servers/blob/main/src/fetch/README.md |
| **CF Playwright MCP** | `cf-playwright` | `@cloudflare/playwright-mcp` | — (conectó antes, inestable) | https://github.com/cloudflare/playwright-mcp |

### 5.3 ⚠️ Configurado, fallback (no conecta consistentemente)

| MCP Server | Nombre config | Comando actual | Problema | Solución |
|---|---|---|---|---|
| **SQLite MCP** | `sqlite` | `@modelcontextprotocol/server-sqlite` | No publicado en npm | Clonar repo MCP servers + build |
| **Codegraph** | `codegraph` | `codegraph serve --mcp` | Binario no encontrado | Instalar codegraph CLI |

### 5.4 ❌ No instalables vía npm (requieren clonar repo + build)

| MCP Server | URL de referencia | Método |
|---|---|---|
| **Apple MCP** | https://github.com/supermemoryai/apple-mcp | `git clone` + `npm install && npm start` (requiere macOS) |
| **Debug MCP** (Microsoft) | https://github.com/microsoft/DebugMCP | `git clone` + build manual |
| **X/Twitter MCP** | https://github.com/xdevplatform/xmcp | `git clone` + `npm install && npm start` |
| **Astro Docs MCP** | https://github.com/withastro/docs-mcp | `git clone` + build manual |
| **CF Workers MCP** | https://github.com/cloudflare/workers-mcp | `git clone` + build manual |
| **CrowdStrike Falcon MCP** (official) | https://github.com/crowdstrike/falcon-mcp | `git clone` + build |
| **Groq Compound MCP** | https://github.com/groq/compound-mcp-server | `git clone` + build manual |
| **Cerebras Code MCP** | https://github.com/Cerebras/cerebras-code-mcp | `git clone` + build manual |
| **Vercel MCP** (official) | https://vercel.com/docs/agent-resources/vercel-mcp | `git clone` + build |
| **MCP on Vercel** | https://github.com/vercel-labs/mcp-on-vercel | Framework deploy Vercel |
| **AWS MCP** (awslabs) | https://github.com/awslabs/mcp | Múltiples servers, instalar individualmente |
| **Postman MCP** | https://github.com/postmanlabs/postman-mcp-server | `git clone` + build manual |
| **Docker Hub MCP** (official) | https://github.com/docker/hub-mcp | `git clone` + build manual |
| **Cloudflare MCP** (general) | https://github.com/cloudflare/mcp | Usar `@cloudflare/mcp-server-cloudflare` en su lugar |
| **PaddleOCR** | https://github.com/PaddlePaddle/PaddleOCR | `pip install paddleocr paddlepaddle` |

### 5.5 Librerías Python instaladas

| Paquete | Versión | Estado |
|---|---|---|
| `fastapi-mcp` | 0.4.0 | ✅ Instalado |
| `mcp-atlassian` | 0.21.1 | ✅ Instalado |

---

## 6. Comandos de Instalación (nombres npm verificados ✅)

```bash
# === SIN API KEYS ===
claude mcp add playwright -- npx @playwright/mcp
claude mcp add context7 -- npx @upstash/context7-mcp
claude mcp add chrome-devtools -- npx chrome-devtools-mcp
claude mcp add cf-playwright -- npx @cloudflare/playwright-mcp
claude mcp add cloudflare -- npx @cloudflare/mcp-server-cloudflare
claude mcp add fetch -- npx @modelcontextprotocol/server-fetch
claude mcp add next-devtools -- npx next-devtools-mcp

# === CON API KEYS (reemplazar PLACEHOLDER) ===
claude mcp add github-mcp -e GITHUB_PERSONAL_ACCESS_TOKEN=PLACEHOLDER -- npx @modelcontextprotocol/server-github
claude mcp add supabase -e SUPABASE_ACCESS_TOKEN=PLACEHOLDER -- npx @supabase/mcp-server-supabase
claude mcp add firecrawl -e FIRECRAWL_API_KEY=PLACEHOLDER -- npx firecrawl-mcp
claude mcp add stripe -e STRIPE_SECRET_KEY=PLACEHOLDER -- npx @stripe/mcp
claude mcp add vercel -e VERCEL_API_TOKEN=PLACEHOLDER -- npx vercel-mcp
claude mcp add sentry -e SENTRY_AUTH_TOKEN=PLACEHOLDER -- npx @sentry/mcp-server
claude mcp add notion -e NOTION_API_KEY=PLACEHOLDER -- npx @notionhq/notion-mcp-server
claude mcp add hostinger -e HOSTINGER_API_TOKEN=PLACEHOLDER -- npx hostinger-mcp
claude mcp add local-seo -e LOCALSEO_API_KEY=PLACEHOLDER -- npx @localseodata/mcp-server
claude mcp add gdrive -e GDRIVE_CREDENTIALS_PATH=PLACEHOLDER -- npx @modelcontextprotocol/server-gdrive
claude mcp add paypal -e PAYPAL_CLIENT_ID=PLACEHOLDER -e PAYPAL_CLIENT_SECRET=PLACEHOLDER -- npx @paypal/mcp
claude mcp add google-ads -e GOOGLE_ADS_CLIENT_ID=PLACEHOLDER -e GOOGLE_ADS_CLIENT_SECRET=PLACEHOLDER -e GOOGLE_ADS_REFRESH_TOKEN=PLACEHOLDER -e GOOGLE_ADS_DEVELOPER_TOKEN=PLACEHOLDER -- npx google-ads-mcp
claude mcp add postgres -e DATABASE_URL=postgresql://user:pass@host:5432/dbname -- npx @modelcontextprotocol/server-postgres
claude mcp add redis -e REDIS_URL=redis://localhost:6379 -- npx redis-mcp
claude mcp add atlassian -e ATLASSIAN_URL=PLACEHOLDER -e ATLASSIAN_EMAIL=PLACEHOLDER -e ATLASSIAN_TOKEN=PLACEHOLDER -- uvx mcp-atlassian
claude mcp add mailboxvalidator -e MAILBOXVALIDATOR_API_KEY=PLACEHOLDER -- uvx mcp-mailboxvalidator
claude mcp add whatsapp -- npx whatsapp-mcp                                  # escaneo QR al iniciar
claude mcp add wordpress -- npx wordpress-mcp-server
claude mcp add linkedin -- npx linkedin-mcp
claude mcp add google-analytics -- npx google-analytics-mcp-server
claude mcp add docker -- npx docker-mcp-server
claude mcp add gcp-cloud-run -- npx cloud-run-mcp
claude mcp add falcon -- npx falcon-mcp-server
```

### Librerías Python

```bash
pip install fastapi-mcp mcp-atlassian          # ✅ ya instaladas
pip install paddleocr paddlepaddle             # pendiente
```

---

## 7. Mapa de Dependencias MCP → Scripts Locales

| MCP Server | Scripts locales que beneficia | Caso de uso |
|---|---|---|
| Playwright MCP | `scripts/social_media_manager/whatsapp.py`, `scripts/social_media_manager/facebook.py` | RPA redes sociales, testing web |
| GitHub MCP | Todos los `core/` auxiliares | Gestión de repos, PRs, issues |
| Supabase MCP | `scripts/database_manager/`, `core/lead.py` | Backend, auth, storage para leads |
| Cloudflare MCP | `scripts/web_designer/example/` | Deploy de workers, KV, D1 |
| Vercel MCP | `scripts/web_designer/` | Deploy de sitios Astro/Next |
| Fetch MCP | `scripts/web_scraper/` | HTTP requests, scraping |
| Firecrawl MCP | `scripts/web_scraper/`, `scripts/seo_manager/` | Scraping con renderizado JS |
| Stripe MCP | `scripts/financial_manager/` | Pagos y facturación |
| Google Ads MCP | `scripts/ad_studio/` | Generación de creatividades para Ads |
| Google Analytics MCP | `scripts/seo_manager/`, `scripts/ad_studio/` | Métricas de tráfico |
| LinkedIn MCP | `scripts/social_media_manager/linkedin/`, `scripts/web_scraper/linkedin_ocr_scraper.py` | Prospección LinkedIn |
| WhatsApp MCP | `scripts/social_media_manager/whatsapp.py` | Mensajería WhatsApp directa |
| WordPress MCP | `scripts/web_scraper/wordpress-seo-crawler/`, `scripts/web_designer/` | Gestión de sitios WordPress |
| Atlassian MCP | — (sin script local) | Gestión de proyectos Jira/Confluence |
| Sentry MCP | Todos los scripts | Monitoreo de errores |
| SQLite MCP | `data/inputs/contacts.db` | Consultas directas a la DB |
| Postman MCP | `scripts/e-mail_marketing_manager/` | Testing de APIs |
| MailboxValidator MCP | `scripts/e-mail_marketing_manager/`, `scripts/database_manager/` | Validación de emails |
| Local SEO MCP | `scripts/seo_manager/` | Datos SEO local |
| X/Twitter MCP | `scripts/social_media_manager/` | Gestión de X/Twitter |
| Astro Docs MCP | `scripts/web_designer/example/` | Documentación Astro en contexto |
| Context7 MCP | Todos los scripts | Búsqueda contextual de docs |
| Chrome DevTools MCP | `scripts/graphic_designer/`, `scripts/web_designer/` | Debug de front-end |
| Notion MCP | — (sin script local) | Gestión de conocimiento |
| PayPal MCP | `scripts/financial_manager/` | Pagos PayPal |
| Hostinger MCP | `scripts/web_designer/` | Gestión hosting/VPS |
| Docker MCP | — (sin script local) | Gestión de contenedores |
| Redis MCP | `core/lead.py`, `scripts/database_manager/` | Cache y colas |
| Falcon MCP | `scripts/web_scraper/` | Seguridad endpoint |
| GCP Cloud Run | — (sin script local) | Deploy en GCP |

---

## 8. Resumen

| Categoría | Cantidad |
|---|---|
| Scripts utilitarios | 11 dirs (+ 1 .py raíz) |
| Repos auxiliares core/ | 1 (`free-claude-code`) |
| Skills | 2 |
| Módulos core/*.py | 5 (`lead`, `services`, `telemetry`, `ai_engine`, `__init__`) |
| MCP servers ✅ conectados | 14 |
| MCP servers ⏳ con keys | 18 |
| MCP servers ⚠️ fallback | 2 |
| MCP servers ❌ no-npm | 15 |
| Librerías Python | 2 instaladas + 1 pendiente |

---

## 9. Plan: Enriquecer contacts.db con logs/campaigns/

> **Fecha inicio:** 2026-07-05
> **DB:** `data/inputs/contacts.db` (~118.797 contactos)

### 9.1 Fuentes de datos

| Fuena | Archivos | Datos | Estado |
|---|---|---|---|
| Identity Maps | ~~12 JSON~~ `identity_map_*.json` | email → `assigned_sender` | ✅ Completado (JSONs borrados) |
| Logs EXITO | ~~37 log_*.txt~~ `log_*.txt` | email → `last_sender_account` + timestamp | ✅ Completado (logs borrados) |
| Validación emails | ~~`validation_results_04062026.csv`~~ `validation_*.csv` | email → deliverability | ✅ Completado (CSVs borrados) |
| Respuestas | ~~CSV `respuestas_sugeridas_*.csv`~~ | emails con respuestas IA | ✅ Completado (CSVs borrados, sin datos de contactos reales) |
| Listas campañas | ~~`contacts_*.txt`, `spain_500_emails.txt`~~ | emails objetivo | ✅ Completado (listas ya estaban en DB, archivos borrados) |
| Gmail CSVs | ~~`data/outputs/gmail_csv/csv1-csv5`~~ | Historial completo Gmail (sent, received, pending, campaigns, bounces) | ✅ Completado (CSVs borrados) |

### 9.2 Progreso

| Paso | Descripción | Resultado |
|---|---|---|
| Identity Maps | UPDATE `assigned_sender` + INSERT nuevos | ✅ 16.302 actualizados, 156 nuevos |
| Logs EXITO | Actualizar `last_sender_account`, `last_interaction_date`, `campaigns` + INSERT nuevos | ✅ 1.946 actualizados, 4 nuevos (logs borrados) |
| Validación | Actualizar `deliverability`, `last_validation_status` | ✅ 7.715 actualizados, 4 nuevos (CSVs borrados) |
| Respuestas | Marcar `email_last_response` | ✅ Completado (sin datos útiles, CSVs borrados) |
| Gmail CSVs | Append `campaigns` (sent/received/pending/campaign/bounce) + UPDATE `last_interaction_date`, `email_last_response`, `deliverability` + INSERT nuevos | ✅ 7.398 actualizados, 292 nuevos |

### 9.3 Scripts creados

- `scripts/database_manager/enrich_identity_maps.py` — Lee identity maps JSON, filtra basura, actualiza DB.
- `scripts/database_manager/enrich_campaign_logs.py` — Parsea 37 logs EXITO/FALLO, extrae sender+fecha+campaña, actualiza DB.
- `scripts/database_manager/enrich_validation.py` — Lee CSVs de validación, actualiza deliverability y validation_status.
- `scripts/database_manager/enrich_gmail_csvs.py` — Procesa 5 CSVs Gmail, append completo en campaigns + actualiza campos resumen.

---

## 10. Data Enrichment — Fase completada (2026-07-20)

### 10.1 DB Estado actual

| Métrica | Valor |
|---------|-------|
| Total contactos | 123,763 |
| Con email válido | 116,747 |
| Con teléfonos | 59,739 |
| Con LinkedIn | 114 |
| Phone-only (sin email) | 5,738 |
| BLACKLISTED | 198 |
| Importados (con fecha) | ~24,500 |
| Pre-existentes (sin fecha) | 99,261 |

### 10.2 Scripts de importación creados

| Script | Fuente | Resultado |
|--------|--------|-----------|
| `config.py` | Configuración centralizada | ✅ Activo |
| `utils.py` | Utilidades compartidas | ✅ Activo |
| `verify_imported.py` | Verificación de fuentes | ✅ Ejecutado |
| `import_vcf.py` | WhatsApp VCFs | ✅ 92 contactos (phone-only) |
| `import_gosom_root.py` | Gosom root CSVs | ✅ 303 contactos nuevos |
| `import_xlsx.py` | XLSX ferias | ✅ 0 nuevos (todos duplicados) |
| `import_blacklist.py` | CONTACTOS RECHAZADOS.docx | ✅ 198 blacklisted |
| `import_google_contacts.py` | Google Contacts CSVs | ✅ 2 teléfonos actualizados |
| `import_gosom_webdata.py` | Gosom webdata/ + web_marketing_caba | ✅ 0 nuevos (ya en DB por import_gosom_root.py) |
| `import_mailrelay.py` | Mailrelay CSV | ✅ 0 nuevos (ya en DB) |
| `import_phone_contacts.py` | contacts selvaggiesteban (phone-only) | ✅ 2,643 contactos importados |
| `import_linkedin_profiles.py` | LinkedIn people/authors CSVs | ✅ 118 perfiles importados |

### 10.3 Gap restante

| Fuente | Prioridad | Motivo |
|--------|-----------|--------|
| YOLANDA.csv | MEDIA | Formato no estándar (~500 contactos) |

---

**Versión:** 2026.07.27 | **Engineering Excellence**
