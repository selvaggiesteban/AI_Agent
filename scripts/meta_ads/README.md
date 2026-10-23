# Meta Ads Campaign Manager

Config-driven campaign creation for the Meta Marketing API (Facebook / Instagram ads).
The code is business-agnostic: everything business-specific (targeting, budget, copy,
creative images, Page) lives in a JSON file under `campaigns/`, and all credentials come
from the environment (`.env`, git-ignored).

## Requirements

- Python 3.10+
- `requests` and `pillow` (`pip install requests pillow`)
- A Meta ad account, a Facebook Page, and a long-lived user access token with the
  `ads_management`, `ads_read` and `business_management` permissions

## Environment variables (`.env`)

| Variable | Required | Description |
| :--- | :--- | :--- |
| `META_ACCESS_TOKEN` | yes | Long-lived user access token |
| `META_APP_ID` | no | Meta app id (token debug + exchange) |
| `META_APP_SECRET` | no | Meta app secret (token debug + exchange) |
| `META_AD_ACCOUNT_ID` | no | Ad account override (`act_...`); auto-detected when the token has a single account |
| `META_GRAPH_VERSION` | no | Graph API version (default `v26.0`) |

## Getting a token

1. Create an app at <https://developers.facebook.com/apps> (type: Business). Note the
   **App ID** and **App Secret**.
2. Open the Graph API Explorer (<https://developers.facebook.com/tools/explorer>), select
   the app, add the permissions `ads_management`, `ads_read`, `business_management` and
   click **Generate Access Token** (accept the warnings: the token only touches your own
   business assets).
3. Exchange the short-lived token for a long-lived one (valid ~60 days):

   ```bash
   python -m scripts.meta_ads exchange --app-id <APP_ID> --app-secret <APP_SECRET> --short-token <TOKEN> --write
   ```

4. Verify everything:

   ```bash
   python -m scripts.meta_ads doctor
   ```

`doctor` prints the ad accounts with their currency, the accessible Pages and (when
possible) their linked WhatsApp number. Refresh the token before expiry by repeating
step 2-3 with the current long-lived token.

## Commands

```bash
# Health check: token, ad accounts (currency), Pages, WhatsApp linkage
python -m scripts.meta_ads doctor

# Targeting search helper (resolves city keys)
python -m scripts.meta_ads resolve-geo "Lanús" --country AR

# Validate a config offline + API preflight (validate_only, no objects created)
python -m scripts.meta_ads validate --config scripts/meta_ads/campaigns/chillburgergrill.json

# Create campaign + ad set + ads, everything PAUSED (safe default)
python -m scripts.meta_ads create --config scripts/meta_ads/campaigns/chillburgergrill.json

# Review in Ads Manager (a billing method is required to deliver), then activate:
python -m scripts.meta_ads set-status --config scripts/meta_ads/campaigns/chillburgergrill.json --status ACTIVE

# Inspect current status / pause again
python -m scripts.meta_ads status --config scripts/meta_ads/campaigns/chillburgergrill.json
python -m scripts.meta_ads set-status PAUSED --config scripts/meta_ads/campaigns/chillburgergrill.json
```

`create --live` creates everything ACTIVE in one shot (only do this after reviewing the
config and ensuring the account has a payment method).

## Config schema (`campaigns/*.json`)

```text
meta_ads
  expected_currency   optional currency guard (create/validate abort on mismatch)
  page_id             optional; otherwise page_name is matched against /me/accounts
  page_name           Page display name used for the ads identity
  campaign.name / campaign.objective / campaign.status
  adset.name
  adset.budget.mode           auto | daily | lifetime
  adset.budget.daily_amount   in MAJOR currency units (e.g. 5000 = 5000 ARS)
  adset.budget.flight_days    used to compute the lifetime budget when needed
  adset.schedule.enabled / days (mon..sun) / start (HH:MM) / end (HH:MM, 00:00 = midnight)
  adset.optimization_goal     default CONVERSATIONS
  adset.destination_type      default WHATSAPP (click-to-WhatsApp ads)
  adset.targeting.geo         mode: coordinates | address | city_radius | city
  adset.targeting.age_min / age_max / genders (m,f) / device_platforms
  ads[]                       name, image, crop (square), crop_focus (center|left|right),
                              primary_text, headline, description, welcome_message
```

Behavior notes:

- **Image paths** are resolved relative to the repository root (or absolute). Images are
  converted to 1:1 JPEG with Pillow at upload time; nothing binary is committed.
- **Budgets** are sent in the account currency's minor denomination (e.g. cents/centavos);
  the offset is read from the ad account. `expected_currency` guards against creating
  5000 USD instead of 5000 ARS.
- **Day-parting** (`adset_schedule`) officially requires a *lifetime* budget. With
  `budget.mode: "auto"` the manager first tries a daily budget and automatically falls
  back to a lifetime budget computed from `daily_amount`, the scheduled days per week and
  `flight_days`.
- **WhatsApp**: ads use `destination_type: WHATSAPP` and the number linked to the Page
  (no phone number is hardcoded in the config).
- **State** (created object ids) is stored in `data/meta_ads/` (git-ignored) so `status`
  and `set-status` work without re-creating anything.
- Everything is created **PAUSED** unless `--live` is passed.

## Reusing this module for another business

1. Copy `campaigns/chillburgergrill.json` to `campaigns/<your-business>.json`.
2. Change Page name, geo, ages, schedule, budget, copy and image paths.
3. Point `META_ACCESS_TOKEN` / `META_AD_ACCOUNT_ID` at the target account and run
   `validate` → `create` → review → `set-status ACTIVE`.
