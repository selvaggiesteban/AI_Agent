"""CLI command implementations for the Meta Ads campaign manager."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import builder
from .builder import ConfigError, load_config, validate_config
from .client import GraphAPIError, GraphClient, REPO_ROOT, exchange_long_lived_token
from .images import prepare_image

STATE_DIR = REPO_ROOT / "data" / "meta_ads"


def _print(text: str = "") -> None:
    print(text)


def _state_path(config: dict) -> Path:
    stem = Path(config["_path"]).stem
    return STATE_DIR / f"{stem}.state.json"


def save_state(config: dict, state: dict) -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = _state_path(config)
    state["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_state(config: dict) -> dict:
    path = _state_path(config)
    if not path.is_file():
        raise ConfigError(f"no state file yet: {path} (run `create` first)")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_account(client: GraphClient, config: dict, force: bool = False) -> tuple[str, dict]:
    meta = config["meta_ads"]
    account_id = meta.get("account_id") or os.environ.get("META_AD_ACCOUNT_ID", "")
    infos: list[dict] = []
    if not account_id:
        infos = client.paginate("/me/adaccounts", {"fields": "id,name,currency,currency_offset,account_status"})
        if not infos:
            raise ConfigError("token has access to no ad accounts (check Meta Business permissions)")
        if len(infos) > 1 and not force:
            lines = "\n".join(f"  {i['id']}  {i.get('name','')}  {i.get('currency','')}" for i in infos)
            raise ConfigError(f"multiple ad accounts found; set META_AD_ACCOUNT_ID or account_id in config:\n{lines}")
        account_id = infos[0]["id"]
    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"
    info = next((i for i in infos if i["id"] == account_id), None)
    if info is None:
        info = client.get(account_id, {"fields": "id,name,currency,currency_offset,account_status"})
    currency = info.get("currency", "")
    offset = info.get("currency_offset")
    if offset is None:
        offset = 2 if currency not in ("JPY", "KRW", "VND") else 0
    info["currency_offset"] = int(offset)
    expected = meta.get("expected_currency")
    if expected and currency and currency != expected and not force:
        raise ConfigError(
            f"ad account currency is {currency}, config expects {expected}. "
            "Budgets would be interpreted in the wrong currency. Re-run with --force to override."
        )
    if info.get("account_status") not in (None, 1):
        _print(f"WARNING: ad account status is {info.get('account_status')} (1=active); ads may not deliver.")
    return account_id, info


def resolve_page(client: GraphClient, config: dict) -> dict:
    meta = config["meta_ads"]
    if meta.get("page_id"):
        return {"id": str(meta["page_id"]), "name": meta.get("page_name", "")}
    wanted = (meta.get("page_name") or "").strip().casefold()
    pages = client.paginate("/me/accounts", {"fields": "id,name,category"})
    if not pages:
        raise ConfigError("token has access to no Facebook Pages (share a Page with the token's user)")
    matches = [p for p in pages if (p.get("name") or "").strip().casefold() == wanted]
    if matches:
        return matches[0]
    if len(pages) == 1:
        _print(f"NOTE: using the only accessible Page: {pages[0]['name']} ({pages[0]['id']})")
        return pages[0]
    lines = "\n".join(f"  {p['id']}  {p.get('name','')}" for p in pages)
    raise ConfigError(f'Page "{meta.get("page_name")}" not found among accessible Pages:\n{lines}')


def resolve_city(client: GraphClient, geo: dict) -> dict:
    term = geo.get("city") or geo.get("name") or ""
    country = geo.get("country", "AR")
    results = client.get(
        "/search",
        {
            "type": "adgeolocation",
            "location_types": '["city"]',
            "q": term,
            "country_code": country,
        },
    ).get("data", [])
    if not results:
        raise ConfigError(f"geo search returned no cities for {term!r} (country {country})")
    same_country = [r for r in results if (r.get("country_code") or "").upper() == country.upper()]
    pool = same_country or results
    exact = [r for r in pool if (r.get("name") or "").casefold() == term.casefold()]
    chosen = exact[0] if exact else pool[0]
    if not exact:
        options = ", ".join(r.get("name", "?") for r in pool[:5])
        _print(f"NOTE: no exact match for {term!r}; using {chosen.get('name')!r} (options: {options})")
    return chosen


def _extract_image_hash(payload: dict) -> str:
    images = payload.get("images") or {}
    for value in images.values():
        if isinstance(value, dict) and value.get("hash"):
            return value["hash"]
    raise RuntimeError(f"could not extract image hash from response: {payload}")


def cmd_doctor(args: argparse.Namespace) -> int:
    client = GraphClient()
    try:
        me = client.get("/me", {"fields": "id,name"})
    except GraphAPIError as exc:
        _print(f"Token check FAILED: {exc}")
        return 1
    _print(f"Token OK: {me.get('name')} (user id {me.get('id')})")
    _print(f"Graph API version: {client.version}")

    app_id = os.environ.get("META_APP_ID", "")
    app_secret = os.environ.get("META_APP_SECRET", "")
    if app_id and app_secret:
        try:
            debug = client.get("/debug_token", {"input_token": client.token, "app_id": app_id, "app_secret": app_secret})
            data = debug.get("data", {})
            expires = data.get("expires_at", 0)
            expires_txt = datetime.fromtimestamp(expires, tz=timezone.utc).isoformat() if expires else "never"
            _print(f"Token valid={data.get('is_valid')} expires={expires_txt}")
            _print(f"Scopes: {', '.join(data.get('scopes', []))}")
        except GraphAPIError as exc:
            _print(f"debug_token unavailable: {exc}")
    else:
        _print("META_APP_ID/META_APP_SECRET not set (optional: enables token inspection)")

    try:
        accounts = client.paginate("/me/adaccounts", {"fields": "id,name,currency,currency_offset,account_status"})
    except GraphAPIError as exc:
        _print(f"Ad accounts FAILED: {exc}")
        accounts = []
    _print()
    _print(f"Ad accounts ({len(accounts)}):")
    for account in accounts:
        status = account.get("account_status")
        _print(
            f"  {account['id']}  {account.get('name','')}  "
            f"currency={account.get('currency')} offset={account.get('currency_offset')} status={status}"
        )

    try:
        pages = client.paginate("/me/accounts", {"fields": "id,name,category"})
    except GraphAPIError as exc:
        _print(f"Pages FAILED: {exc}")
        pages = []
    _print(f"Pages ({len(pages)}):")
    for page in pages:
        line = f"  {page['id']}  {page.get('name','')}  ({page.get('category','')})"
        _print(line)
        for field in ("whatsapp_business_api_business_phone_number", "whatsapp_business_phone_number"):
            try:
                detail = client.get(page["id"], {"fields": field})
                if detail.get(field):
                    _print(f"      WhatsApp: {detail[field]}")
                    break
            except GraphAPIError:
                continue

    if not accounts or not pages:
        _print()
        _print("Fix: grant the token's user admin/developer access to the Business ad account and Page.")
        return 1
    return 0


def cmd_resolve_geo(args: argparse.Namespace) -> int:
    client = GraphClient()
    payload = client.get(
        "/search",
        {
            "type": "adgeolocation",
            "location_types": '["city"]',
            "q": args.term,
            "country_code": args.country,
        },
    )
    results = payload.get("data", [])
    if not results:
        _print("No results.")
        return 1
    _print(f"{'KEY':<14} {'COUNTRY':<8} NAME")
    for item in results:
        _print(f"{item.get('key',''):<14} {item.get('country_code',''):<8} {item.get('name','')}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    warnings = validate_config(config)
    meta = config["meta_ads"]
    _print(f"Config OK: {config['_path']}")
    for warning in warnings:
        _print(f"  WARNING: {warning}")

    adset = meta["adset"]
    budget = adset.get("budget", {})
    schedule = adset.get("schedule", {})
    _print()
    _print(f"Campaign : {meta['campaign']['name']} ({meta['campaign'].get('objective','OUTCOME_ENGAGEMENT')})")
    _print(f"Ad set   : {adset['name']}")
    _print(f"Budget   : {budget.get('daily_amount')} / day (mode={budget.get('mode','auto')}, "
           f"flight={budget.get('flight_days', 28)}d, API units need account currency offset)")
    if schedule.get("enabled"):
        _print(f"Schedule : {', '.join(schedule['days'])} {schedule['start']}-{schedule['end']} ({schedule.get('timezone_type','ADVERTISER')} tz)")
    else:
        _print("Schedule : continuous")
    geo = adset["targeting"]["geo"]
    _print(f"Geo      : {geo['mode']} -> {json.dumps({k: v for k, v in geo.items() if k != 'mode'}, ensure_ascii=False)}")
    _print(f"Ages     : {adset['targeting'].get('age_min')}-{adset['targeting'].get('age_max')} "
           f"genders={adset['targeting'].get('genders')}")
    _print("Ads      :")
    for ad in meta["ads"]:
        prepared, filename = prepare_image(ad["image"], ad.get("crop", "square"), ad.get("crop_focus", "center"))
        _print(f"  - {ad['name']}: image -> {filename} ({len(prepared)//1024} KB JPEG)")

    client = GraphClient()
    if not client.token:
        _print()
        _print("META_ACCESS_TOKEN not set: skipped API preflight (local checks passed).")
        return 0

    _print()
    _print("API preflight (read-only + validate_only):")
    account_id, account_info = resolve_account(client, config, force=args.force)
    _print(f"  account: {account_id} currency={account_info.get('currency')} offset={account_info['currency_offset']}")
    page = resolve_page(client, config)
    _print(f"  page   : {page['id']} {page.get('name','')}")
    geo_mode = adset["targeting"]["geo"]["mode"]
    resolved_city = None
    if geo_mode in ("city", "city_radius") and not adset["targeting"]["geo"].get("key"):
        resolved_city = resolve_city(client, adset["targeting"]["geo"])
        _print(f"  city   : {resolved_city.get('name')} key={resolved_city.get('key')}")
    targeting = builder.build_targeting_fields(config, resolved_city)
    budget_fields = builder.budget_variants(config, account_info["currency_offset"])[0][1]
    campaign_fields = builder.build_campaign_fields(config, status="PAUSED")
    result = client.post(f"{account_id}/campaigns", {**campaign_fields, "execution_options": ["validate_only"]})
    _print(f"  campaign validate_only: {result}")
    adset_fields = builder.build_adset_fields(
        config, campaign_id="0", page_id=page["id"], targeting=targeting,
        budget_fields=budget_fields, status="PAUSED", validate_only=True,
    )
    try:
        result = client.post(f"{account_id}/adsets", adset_fields)
        _print(f"  adset validate_only: {result}")
    except GraphAPIError as exc:
        _print(f"  adset validate_only FAILED: {exc}")
        return 1
    _print("Preflight OK.")
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    validate_config(config)
    meta = config["meta_ads"]
    adset_cfg = meta["adset"]
    status = "ACTIVE" if args.live else "PAUSED"
    client = GraphClient()

    account_id, account_info = resolve_account(client, config, force=args.force)
    currency = account_info.get("currency", "?")
    offset = account_info["currency_offset"]
    _print(f"Account  : {account_id} ({account_info.get('name','')}) currency={currency} offset={offset}")

    page = resolve_page(client, config)
    _print(f"Page     : {page['id']} {page.get('name','')}")

    geo = adset_cfg["targeting"]["geo"]
    resolved_city = None
    if geo["mode"] in ("city", "city_radius") and not geo.get("key"):
        resolved_city = resolve_city(client, geo)
        _print(f"City     : {resolved_city.get('name')} (key {resolved_city.get('key')})")

    if not args.live:
        _print("Creating everything PAUSED. After review in Ads Manager, activate with:")
        _print(f"  python -m scripts.meta_ads set-status {args.config} --status ACTIVE")

    _print("Creating campaign...")
    campaign_fields = builder.build_campaign_fields(config, status=status)
    campaign = client.post(f"{account_id}/campaigns", campaign_fields)
    campaign_id = campaign["id"]
    _print(f"  campaign {campaign_id}")

    targeting = builder.build_targeting_fields(config, resolved_city)
    chosen_mode, chosen_budget = None, None
    budget_errors: list[str] = []
    for mode_name, budget_fields in builder.budget_variants(config, offset):
        adset_fields = builder.build_adset_fields(
            config, campaign_id, page["id"], targeting, budget_fields, status, validate_only=True
        )
        try:
            client.post(f"{account_id}/adsets", adset_fields)
            chosen_mode, chosen_budget = mode_name, budget_fields
            break
        except GraphAPIError as exc:
            budget_errors.append(f"{mode_name}: {exc}")
            _print(f"  budget mode {mode_name} rejected, trying next... ({exc})")
    if chosen_mode is None:
        raise GraphAPIError(
            {"error": {"message": "no budget variant accepted: " + " || ".join(budget_errors)}},
            "adset budget",
        )

    daily = adset_cfg["budget"]["daily_amount"]
    _print(f"Ad set budget: {daily} {currency}/day equivalent (mode={chosen_mode}); creating ad set...")
    adset_fields = builder.build_adset_fields(
        config, campaign_id, page["id"], targeting, chosen_budget, status, validate_only=False
    )
    adset = client.post(f"{account_id}/adsets", adset_fields)
    adset_id = adset["id"]
    _print(f"  adset {adset_id}")

    state: dict = {
        "config": str(config["_path"]),
        "account_id": account_id,
        "currency": currency,
        "currency_offset": offset,
        "budget_mode": chosen_mode,
        "campaign": {"id": campaign_id, "name": campaign_fields["name"]},
        "adset": {"id": adset_id, "name": adset_cfg["name"]},
        "ads": [],
        "status": status,
    }

    for ad in meta["ads"]:
        image_bytes, filename = prepare_image(ad["image"], ad.get("crop", "square"), ad.get("crop_focus", "center"))
        upload = client.post(f"{account_id}/adimages", files={"filename": (filename, image_bytes, "image/jpeg")})
        image_hash = _extract_image_hash(upload)
        creative_fields = builder.build_creative_fields(config, page["id"], ad, image_hash)
        creative = client.post(f"{account_id}/adcreatives", creative_fields)
        ad_fields = builder.build_ad_fields(ad, adset_id, creative["id"], status)
        ad_resp = client.post(f"{account_id}/ads", ad_fields)
        state["ads"].append({"id": ad_resp["id"], "name": ad["name"], "creative_id": creative["id"]})
        _print(f"  ad {ad_resp['id']}  {ad['name']}")

    state_path = save_state(config, state)
    _print()
    _print(f"Done. Everything is {status}. State: {state_path}")
    _print(f"Campaign {campaign_id} | Ad set {adset_id} | {len(state['ads'])} ads")
    if status == "PAUSED":
        _print("Next: review in Ads Manager (billing method required to deliver), then run set-status ACTIVE.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    state = load_state(config)
    client = GraphClient()
    ids = [state["campaign"]["id"], state["adset"]["id"]] + [ad["id"] for ad in state["ads"]]
    payload = client.get("/", {"ids": ",".join(ids), "fields": "name,status,effective_status"})
    _print(f"Config  : {config['_path']}")
    _print(f"Budget  : mode={state.get('budget_mode')} currency={state.get('currency')}")
    _print(f"{'ID':<16} {'STATUS':<10} {'EFFECTIVE':<18} NAME")
    for entity_id in ids:
        item = payload.get(entity_id, {})
        _print(f"{entity_id:<16} {item.get('status',''):<10} {item.get('effective_status',''):<18} {item.get('name','')}")
    return 0


def cmd_set_status(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    state = load_state(config)
    client = GraphClient()
    targets = [state["campaign"]["id"], state["adset"]["id"]] + [ad["id"] for ad in state["ads"]]
    for entity_id in targets:
        client.post(entity_id, {"status": args.status})
        _print(f"  {entity_id} -> {args.status}")
    state["status"] = args.status
    save_state(config, state)
    _print(f"All entities set to {args.status}.")
    return 0


def cmd_exchange(args: argparse.Namespace) -> int:
    app_id = args.app_id or os.environ.get("META_APP_ID", "")
    app_secret = args.app_secret or os.environ.get("META_APP_SECRET", "")
    short_token = args.short_token or ""
    if not (app_id and app_secret and short_token):
        _print("exchange requires --app-id, --app-secret and --short-token (or META_APP_ID/META_APP_SECRET in .env)")
        return 1
    payload = exchange_long_lived_token(app_id, app_secret, short_token)
    token = payload.get("access_token", "")
    expires = payload.get("expires_in")
    _print(f"Long-lived token (expires_in={expires}s):")
    _print(token)
    if args.write:
        env_path = REPO_ROOT / ".env"
        lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.is_file() else []
        output, replaced = [], False
        for line in lines:
            if line.strip().startswith("META_ACCESS_TOKEN="):
                output.append(f"META_ACCESS_TOKEN={token}")
                replaced = True
            else:
                output.append(line)
        if not replaced:
            output.append(f"META_ACCESS_TOKEN={token}")
        env_path.write_text("\n".join(output) + "\n", encoding="utf-8")
        _print(f"Saved to {env_path} (git-ignored).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m scripts.meta_ads",
        description="Config-driven Meta Ads (Marketing API) campaign manager",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="check token, ad accounts and Pages")

    resolve_geo = sub.add_parser("resolve-geo", help="search targeting locations")
    resolve_geo.add_argument("term", help='city name, e.g. "Lanús"')
    resolve_geo.add_argument("--country", default="AR", help="ISO country code (default AR)")

    validate = sub.add_parser("validate", help="validate config locally and preflight against the API")
    validate.add_argument("--config", required=True, help="path to campaign config JSON")
    validate.add_argument("--force", action="store_true", help="ignore expected_currency mismatch")

    create = sub.add_parser("create", help="create campaign, ad set and ads from a config")
    create.add_argument("--config", required=True, help="path to campaign config JSON")
    create.add_argument("--live", action="store_true", help="create as ACTIVE (default: PAUSED)")
    create.add_argument("--force", action="store_true", help="ignore expected_currency mismatch")

    status = sub.add_parser("status", help="show status of created entities")
    status.add_argument("--config", required=True)

    set_status = sub.add_parser("set-status", help="activate or pause created entities")
    set_status.add_argument("status", choices=["ACTIVE", "PAUSED"])
    set_status.add_argument("--config", required=True)

    exchange = sub.add_parser("exchange", help="exchange a short-lived token for a long-lived one")
    exchange.add_argument("--app-id", default="")
    exchange.add_argument("--app-secret", default="")
    exchange.add_argument("--short-token", default="")
    exchange.add_argument("--write", action="store_true", help="write META_ACCESS_TOKEN into .env")
    return parser


COMMANDS = {
    "doctor": cmd_doctor,
    "resolve-geo": cmd_resolve_geo,
    "validate": cmd_validate,
    "create": cmd_create,
    "status": cmd_status,
    "set-status": cmd_set_status,
    "exchange": cmd_exchange,
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return COMMANDS[args.command](args)
    except (ConfigError, GraphAPIError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
