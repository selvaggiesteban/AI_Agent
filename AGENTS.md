# AGENTS.md — Inventory of Agents, Repositories, and MCP Servers

> **Last Update:** 2026-09-04
> **Root Project:** `.`

---

## 1. Utility Scripts (`scripts/`)

| Local Directory | Full Path | Main Files | Role |
|---|---|---|---|
| `scripts/ad_studio/` | `scripts/ad_studio/` | `generar_gsr.py`, `gsr_batch_v7.py`, `brand/loader.py`, `brand/prompt_builder.py` | AI Advertising Creative Generator (Pollinations) + brand manuals |
| `scripts/campaign_manager/` | `scripts/campaign_manager/` | `campaign_ui.py`, `drafts.py` | Campaign Dashboard and Gmail draft creation |
| `scripts/database_manager/` | `scripts/database_manager/` | `config.py`, `utils.py`, `audit_db.py`, `contacts_editor.py`, `enrich_*.py`, `import_*.py`, `cleanup_duplicate_emails.py`, `remove_duplicates.py` | contacts.db Management: audit, enrichment, import, dedup |
| `scripts/e-mail_marketing_manager/` | `scripts/e-mail_marketing_manager/` | `e-mail.py`, `generate_5_csvs.py` | SMTP Engine, Gmail CSV extraction |
| &emsp;↳ `e-mail_marketing_campaigns/` | `scripts/e-mail_marketing_manager/e-mail_marketing_campaigns/` | `campaign_engine.py`, `campaign_launcher.py`, `find_unknown_leads.py`, `gmail_report.py`, `imap_bot.py` | Email campaigns and reporting |
| `scripts/financial_manager/` | `scripts/financial_manager/` | `accountly/main.py` | Accounting Dashboard (ARCA/Santander/MP) |
| `scripts/graphic_designer/` | `scripts/graphic_designer/` | `web-screenshot/web_screenshots.py` | Web screenshots with Selenium |
| `scripts/inbox_manager/` | `scripts/inbox_manager/` | — | (Empty module, pending development) |
| `scripts/seo_manager/` | `scripts/seo_manager/` | `keywords.py`, `seo-content-generator/seo_content_generator.py` | Technical SEO, keywords, and content |
| `scripts/social_media_manager/` | `scripts/social_media_manager/` | `facebook.py`, `instagram.py`, `linkedin.py`, `messenger.py`, `telegram.py`, `whatsapp.py` | Social Media RPA (Playwright) |
| &emsp;↳ `linkedin/` | `scripts/social_media_manager/linkedin/` | `linkedin_tools.py`, `linkedin_full_scraper.py`, `linkedin_parser.py` | LinkedIn tools via MCP |
| `scripts/web_designer/` | `scripts/web_designer/` | `landing-page-generator/landing-page-generator.py` | Landing page generator |
| &emsp;↳ `example/` | `scripts/web_designer/example/` | Astro + TypeScript (i18n, D1, MercadoPago) | selvaggiesteban.dev site |
| `scripts/web_scraper/` | `scripts/web_scraper/` | `ecommerce.py`, `kompass.py`, `linkedin_ocr_scraper.py`, `research.py` | Scraping and market intelligence |
| &emsp;↳ `ecommercer-competitor-research/` | `scripts/web_scraper/ecommercer-competitor-research/` | — | Ecommerce competitive analysis |
| &emsp;↳ `long-tail-keyword-crawler/` | `scripts/web_scraper/long-tail-keyword-crawler/` | — | Long-tail keyword crawler |
| &emsp;↳ `paginasamarillas_web_scraper/` | `scripts/web_scraper/paginasamarillas_web_scraper/` | — | Yellow Pages scraper |
| &emsp;↳ `smart-research-assistant/` | `scripts/web_scraper/smart-research-assistant/` | — | AI Research + PDF reports |
| &emsp;↳ `wordpress-seo-crawler/` | `scripts/web_scraper/wordpress-seo-crawler/` | — | WordPress SEO crawler |

**Root File:** `scripts/check_providers.py` — Verifies LLM provider availability

---

## 2. Auxiliary Repositories (`core/`)

| Local Directory | Full Path | Remote URL (GitHub) | Purpose | Owner |
|---|---|---|---|---|
| `core/free-claude-code` | `core/free-claude-code` | https://github.com/Alishahryar1/free-claude-code | Proxy server for Claude Code CLI / Codex CLI | Alishahryar1 |

---

## 3. Skills (`skills/`)

| Local File | Full Path | Role |
|---|---|---|
| `skills/ads_strategist.md` | `skills/ads_strategist.md` | Advertising strategy TOFU/MOFU/BOFU |
| `skills/google-ads-audit.md` | `skills/google-ads-audit.md` | Google Ads Audit |
| `skills/diseño-web-ia.md` | `skills/diseño-web-ia.md` | Forward Deployed Engineer for AI Web Design |

---

## 4. Core Modules (`core/*.py`)

| File | Full Path | Function |
|---|---|---|
| `core/lead.py` | `core/lead.py` | Lead prospecting pipeline |
| `core/services.py` | `core/services.py` | Client services (contracts, web, SEO, ads) |
| `core/telemetry.py` | `core/telemetry.py` | Consolidated activity reports |
| `core/ai_engine.py` | `core/ai_engine.py` | AI Engine (LLMRouter: Gemini/OpenAI/Anthropic) |
| `core/__init__.py` | `core/__init__.py` | Package initialization |

---

## 5. MCP Servers — Real Status (verified 2026-06-24)

### 5.1 ✅ Connected (14)

| MCP Server | Config Name | Package | Reference URL |
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

### 5.2 ⏳ Configured, require real API keys (18)

| MCP Server | Config Name | npm Package | Env vars | Reference URL |
|---|---|---|---|---|
| **Stripe MCP** | `stripe` | `@stripe/mcp` | `STRIPE_SECRET_KEY` | https://docs.stripe.com/mcp |
| **Vercel MCP** | `vercel` | `vercel-mcp` | `VERCEL_API_TOKEN` | https://vercel.com/docs/agent-resources/vercel-mcp |
| **Sentry MCP** | `sentry` | `@sentry/mcp-server` | `SENTRY_AUTH_TOKEN` | https://github.com/getsentry/sentry-mcp |
| **PostgreSQL MCP** | `postgres` | `@modelcontextprotocol/server-postgres` | `DATABASE_URL` | https://github.com/modelcontextprotocol/servers/tree/main/src/postgres |
| **Local SEO MCP** | `local-seo` | `@localseodata/mcp-server` | `LOCALSEO_API_KEY` | https://github.com/localseodata/mcp-server |
| **Google Drive MCP** | `gdrive` | `@modelcontextprotocol/server-gdrive` | `GDRIVE_CREDENTIALS_PATH` | https://github.com/modelcontextprotocol/servers-archived/tree/main/src/gdrive |
| **WhatsApp MCP** | `whatsapp` | `whatsapp-mcp` | QR Scan | https://github.com/lharries/whatsapp-mcp |
| **PayPal MCP** | `paypal` | `@paypal/mcp` | `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET` | https://github.com/paypal/agent-toolkit/tree/main/modelcontextprotocol |
| **Google Ads MCP** | `google-ads` | `google-ads-mcp` | `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_REFRESH_TOKEN`, `GOOGLE_ADS_DEVELOPER_TOKEN` | https://github.com/googleads/google-ads-mcp |
| **Hostinger MCP** | `hostinger` | `hostinger-mcp` | `HOSTINGER_API_TOKEN` | https://github.com/hostinger/api-mcp-server |
| **Docker MCP** | `docker` | `docker-mcp-server` | Docker env | https://github.com/docker/hub-mcp |
| **GCP Cloud Run** | `gcp-cloud-run` | `cloud-run-mcp` | GCP credentials | https://github.com/googlecloudplatform/cloud-run-mcp |
| **Falcon MCP** | `falcon` | `falcon-mcp-server` | CrowdStrike env | https://github.com/crowdstrike/falcon-mcp |
| **Atlassian MCP** | `atlassian` | `uvx mcp-atlassian` (Python) | `ATLASSIAN_URL`, `ATLASSIAN_EMAIL`, `ATLASSIAN_TOKEN` | https://github.com/sooperset/mcp-atlassian |
| **MailboxValidator** | `mailboxvalidator` | `uvx mcp-mailboxvalidator` (Python) | `MAILBOXVALIDATOR_API_KEY` | https://github.com/MailboxValidator/mcp-mailboxvalidator |
| **Cloudflare MCP** | `cloudflare` | `@cloudflare/mcp-server-cloudflare` | CF API token | https://github.com/cloudflare/mcp-server-cloudflare |
| **Fetch MCP** | `fetch` | `@modelcontextprotocol/server-fetch` | — (no key, but connection fails) | https://github.com/modelcontextprotocol/servers/blob/main/src/fetch/README.md |
| **CF Playwright MCP** | `cf-playwright` | `@cloudflare/playwright-mcp` | — (connected before, unstable) | https://github.com/cloudflare/playwright-mcp |

### 5.3 ⚠️ Configured, fallback (not connecting consistently)

| MCP Server | Config Name | Current Command | Problem | Solution |
|---|---|---|---|---|
| **SQLite MCP** | `sqlite` | `@modelcontextprotocol/server-sqlite` | Not published on npm | Clone MCP servers repo + build |
| **Codegraph** | `codegraph` | `codegraph serve --mcp` | Binary not found | Install codegraph CLI |

### 5.4 ❌ Not installable via npm (require clone repo + build)

| MCP Server | Reference URL | Method |
|---|---|---|
| **Apple MCP** | https://github.com/supermemoryai/apple-mcp | `git clone` + `npm install && npm start` (requires macOS) |
| **Debug MCP** (Microsoft) | https://github.com/microsoft/DebugMCP | `git clone` + build manual |
| **X/Twitter MCP** | https://github.com/xdevplatform/xmcp | `git clone` + `npm install && npm start` |
| **Astro Docs MCP** | https://github.com/withastro/docs-mcp | `git clone` + build manual |
| **CF Workers MCP** | https://github.com/cloudflare/workers-mcp | `git clone` + build manual |
| **CrowdStrike Falcon MCP** (official) | https://github.com/crowdstrike/falcon-mcp | `git clone` + build |
| **Groq Compound MCP** | https://github.com/groq/compound-mcp-server | `git clone` + build manual |
| **Cerebras Code MCP** | https://github.com/Cerebras/cerebras-code-mcp | `git clone` + build manual |
| **Vercel MCP** (official) | https://vercel.com/docs/agent-resources/vercel-mcp | `git clone` + build |
| **MCP on Vercel** | https://github.com/vercel-labs/mcp-on-vercel | Framework deploy Vercel |
| **AWS MCP** (awslabs) | https://github.com/awslabs/mcp | Multiple servers, install individually |
| **Postman MCP** | https://github.com/postmanlabs/postman-mcp-server | `git clone` + build manual |
| **Docker Hub MCP** (official) | https://github.com/docker/hub-mcp | `git clone` + build manual |
| **Cloudflare MCP** (general) | https://github.com/cloudflare/mcp | Use `@cloudflare/mcp-server-cloudflare` instead |
| **PaddleOCR** | https://github.com/PaddlePaddle/PaddleOCR | `pip install paddleocr paddlepaddle` |

### 5.5 Installed Python Libraries

| Package | Version | Status |
|---|---|---|
| `fastapi-mcp` | 0.4.0 | ✅ Installed |
| `mcp-atlassian` | 0.21.1 | ✅ Installed |

---

## 6. Installation Commands (npm names verified ✅)

```bash
# === WITHOUT API KEYS ===
claude mcp add playwright -- npx @playwright/mcp
claude mcp add context7 -- npx @upstash/context7-mcp
claude mcp add chrome-devtools -- npx chrome-devtools-mcp
claude mcp add cf-playwright -- npx @cloudflare/playwright-mcp
claude mcp add cloudflare -- npx @cloudflare/mcp-server-cloudflare
claude mcp add fetch -- npx @modelcontextprotocol/server-fetch
claude mcp add next-devtools -- npx next-devtools-mcp

# === WITH API KEYS (replace PLACEHOLDER) ===
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
claude mcp add whatsapp -- npx whatsapp-mcp                                  # QR scan on start
claude mcp add wordpress -- npx wordpress-mcp-server
claude mcp add linkedin -- npx linkedin-mcp
claude mcp add google-analytics -- npx google-analytics-mcp-server
claude mcp add docker -- npx docker-mcp-server
claude mcp add gcp-cloud-run -- npx cloud-run-mcp
claude mcp add falcon -- npx falcon-mcp-server
```

### Python Libraries

```bash
pip install fastapi-mcp mcp-atlassian          # ✅ already installed
pip install paddleocr paddlepaddle             # pending
```

---

## 7. Dependency Map: MCP $\rightarrow$ Local Scripts

| MCP Server | Local scripts it benefits | Use case |
|---|---|---|
| Playwright MCP | `scripts/social_media_manager/whatsapp.py`, `scripts/social_media_manager/facebook.py` | Social media RPA, web testing |
| GitHub MCP | All `core/` utilities | Repo management, PRs, issues |
| Supabase MCP | `scripts/database_manager/`, `core/lead.py` | Backend, auth, storage for leads |
| Cloudflare MCP | `scripts/web_designer/example/` | Deploy of workers, KV, D1 |
| Vercel MCP | `scripts/web_designer/` | Deploy of Astro/Next sites |
| Fetch MCP | `scripts/web_scraper/` | HTTP requests, scraping |
| Firecrawl MCP | `scripts/web_scraper/`, `scripts/seo_manager/` | Scraping with JS rendering |
| Stripe MCP | `scripts/financial_manager/` | Payments and billing |
| Google Ads MCP | `scripts/ad_studio/` | Creative generation for Ads |
| Google Analytics MCP | `scripts/seo_manager/`, `scripts/ad_studio/` | Traffic metrics |
| LinkedIn MCP | `scripts/social_media_manager/linkedin/`, `scripts/web_scraper/linkedin_ocr_scraper.py` | LinkedIn prospecting |
| WhatsApp MCP | `scripts/social_media_manager/whatsapp.py` | Direct WhatsApp messaging |
| WordPress MCP | `scripts/web_scraper/wordpress-seo-crawler/`, `scripts/web_designer/` | WordPress site management |
| Atlassian MCP | — (no local script) | Jira/Confluence project management |
| Sentry MCP | All scripts | Error monitoring |
| SQLite MCP | `data/inputs/contacts.db` | Direct DB queries |
| Postman MCP | `scripts/e-mail_marketing_manager/` | API testing |
| MailboxValidator MCP | `scripts/e-mail_marketing_manager/`, `scripts/database_manager/` | Email validation |
| Local SEO MCP | `scripts/seo_manager/` | Local SEO data |
| X/Twitter MCP | `scripts/social_media_manager/` | X/Twitter management |
| Astro Docs MCP | `scripts/web_designer/example/` | Astro documentation in context |
| Context7 MCP | All scripts | Contextual doc search |
| Chrome DevTools MCP | `scripts/graphic_designer/`, `scripts/web_designer/` | Front-end debug |
| Notion MCP | — (no local script) | Knowledge management |
| PayPal MCP | `scripts/financial_manager/` | PayPal payments |
| Hostinger MCP | `scripts/web_designer/` | Hosting/VPS management |
| Docker MCP | — (no local script) | Container management |
| Redis MCP | `core/lead.py`, `scripts/database_manager/` | Cache and queues |
| Falcon MCP | `scripts/web_scraper/` | Endpoint security |
| GCP Cloud Run | — (no local script) | GCP deploy |

---

## 8. Summary

| Category | Quantity |
|---|---|
| Utility scripts | 11 dirs (+ 1 root .py) |
| Auxiliary core repos/ | 1 (`free-claude-code`) |
| Skills | 3 |
| Core modules core/*.py | 5 (`lead`, `services`, `telemetry`, `ai_engine`, `__init__`) |
| MCP servers ✅ connected | 14 |
| MCP servers ⏳ with keys | 18 |
| MCP servers ⚠️ fallback | 2 |
| MCP servers ❌ non-npm | 15 |
| Python libraries | 2 installed + 1 pending |

---

## 9. Plan: Enrich contacts.db with logs/campaigns/

> **Start Date:** 2026-07-05
> **DB:** `data/inputs/contacts.db` (~118,797 contacts)

### 9.1 Data Sources

| Source | Files | Data | Status |
|---|---|---|---|
| Identity Maps | ~~12 JSON~~ `identity_map_*.json` | email $\rightarrow$ `assigned_sender` | ✅ Completed (JSONs deleted) |
| SUCCESS Logs | ~~37 log_*.txt~~ `log_*.txt` | email $\rightarrow$ `last_sender_account` + timestamp | ✅ Completed (logs deleted) |
| Email Validation | ~~`validation_results_04062026.csv`~~ `validation_*.csv` | email $\rightarrow$ deliverability | ✅ Completed (CSVs deleted) |
| Responses | ~~CSV `respuestas_sugeridas_*.csv`~~ | emails with AI responses | ✅ Completed (CSVs deleted, no real contact data) |
| Campaign Lists | ~~`contacts_*.txt`, `spain_500_emails.txt`~~ | target emails | ✅ Completed (lists already in DB, files deleted) |
| Gmail CSVs | ~~`data/outputs/gmail_csv/csv1-csv5`~~ | Full Gmail history (sent, received, pending, campaigns, bounces) | ✅ Completed (CSVs deleted) |

### 9.2 Progress

| Step | Description | Result |
|---|---|---|
| Identity Maps | UPDATE `assigned_sender` + INSERT new | ✅ 16,302 updated, 156 new |
| SUCCESS Logs | Update `last_sender_account`, `last_interaction_date`, `campaigns` + INSERT new | ✅ 1,946 updated, 4 new (logs deleted) |
| Validation | Update `deliverability`, `last_validation_status` | ✅ 7,715 updated, 4 new (CSVs deleted) |
| Responses | Mark `email_last_response` | ✅ Completed (no useful data, CSVs deleted) |
| Gmail CSVs | Append `campaigns` (sent/received/pending/campaign/bounce) + UPDATE `last_interaction_date`, `email_last_response`, `deliverability` + INSERT new | ✅ 7,398 updated, 292 new |

### 9.3 Scripts Created

- `scripts/database_manager/enrich_identity_maps.py` — Reads identity maps JSON, filters junk, updates DB.
- `scripts/database_manager/enrich_campaign_logs.py` — Parses 37 SUCCESS/FAILURE logs, extracts sender+date+campaign, updates DB.
- `scripts/database_manager/enrich_validation.py` — Reads validation CSVs, updates deliverability and validation_status.
- `scripts/database_manager/enrich_gmail_csvs.py` — Processes 5 Gmail CSVs, full append in campaigns + updates summary fields.

---

## 10. Data Enrichment — Phase Completed (2026-07-20)

### 10.1 DB Current State

| Metric | Value |
|---------|-------|
| Total contacts | 123,763 |
| With valid email | 116,747 |
| With phones | 59,739 |
| With LinkedIn | 114 |
| Phone-only (no email) | 5,738 |
| BLACKLISTED | 198 |
| Imported (with date) | ~24,500 |
| Pre-existing (no date) | 99,261 |

### 10.2 Import Scripts Created

| Script | Source | Result |
|--------|--------|-----------|
| `config.py` | Centralized configuration | ✅ Active |
| `utils.py` | Shared utilities | ✅ Active |
| `verify_imported.py` | Source verification | ✅ Executed |
| `import_vcf.py` | WhatsApp VCFs | ✅ 92 contacts (phone-only) |
| `import_gosom_root.py` | Gosom root CSVs | ✅ 303 new contacts |
| `import_xlsx.py` | Trade fair XLSX | ✅ 0 new (all duplicates) |
| `import_blacklist.py` | CONTACTOS RECHAZADOS.docx | ✅ 198 blacklisted |
| `import_google_contacts.py` | Google Contacts CSVs | ✅ 2 phones updated |
| `import_gosom_webdata.py` | Gosom webdata/ + web_marketing_caba | ✅ 0 new (already in DB via import_gosom_root.py) |
| `import_mailrelay.py` | Mailrelay CSV | ✅ 0 new (already in DB) |
| `import_phone_contacts.py` | contacts selvaggiesteban (phone-only) | ✅ 2,643 contacts imported |
| `import_linkedin_profiles.py` | LinkedIn people/authors CSVs | ✅ 118 profiles imported |

### 10.3 Remaining Gap

| Source | Priority | Reason |
|--------|-----------|--------|
| YOLANDA.csv | MEDIUM | Non-standard format (~500 contacts) |

---

**Version:** 2026.09.04 | **Engineering Excellence**
